#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
set -euo pipefail
main() {
engine=${1:?Usage: build/local.sh llama|whisper linux|android amd64|arm64 vulkan|cuda}
os=${2:?}; arch=${3:?}; backend=${4:?}
case "$engine/$os/$arch/$backend" in
  llama/linux/amd64/vulkan|llama/linux/amd64/cuda|whisper/linux/amd64/vulkan|whisper/linux/amd64/cuda|llama/android/amd64/vulkan|llama/android/arm64/vulkan|whisper/android/amd64/vulkan|whisper/android/arm64/vulkan) ;;
  *) echo 'Unsupported local target (Linux arm64 needs a native arm64 builder).' >&2; exit 2;;
esac
repo=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
work=${BASHKITTEN_LOCALAI_WORK:-/run/media/user/Data/BashkittenBuild/localai}
python3 "$repo/build/releases.py" --verify "$engine"
mkdir -p "$work"/{cache,sources,artifacts,logs}
readarray -t pin < <(python3 - "$repo/upstreams.json" "$engine" <<'PY'
import json,sys
p=json.load(open(sys.argv[1]))[sys.argv[2]]
for k in ('repository','commit','version','packageRevision'):print(p[k])
PY
)
src="$work/sources/$engine"
if [[ ! -d "$src/.git" ]]; then git clone --no-checkout "https://github.com/${pin[0]}.git" "$src"; fi
git -C "$src" fetch --depth 1 origin "${pin[1]}"
git -C "$src" checkout --detach "${pin[1]}"
git -C "$src" submodule update --init --recursive
builder_commit=$(git -C "$repo" rev-parse HEAD)
# Snapshot recipe inputs before starting; this also preserves the exact source of
# an in-progress build if the working checkout is edited concurrently.
recipe_hash=$(python3 - "$repo" <<'PYHASH'
import hashlib,pathlib,sys
root=pathlib.Path(sys.argv[1]);h=hashlib.sha256()
for name in ['build/Dockerfile','build/package.py','build/releases.py','build/local.sh','build/termux.cmake','build/DONOR-LICENSE','LICENSE','upstreams.json']:
 h.update(name.encode());h.update((root/name).read_bytes())
print(h.hexdigest())
PYHASH
)
mkdir -p "$work/recipes"
recipe="$work/recipes/$recipe_hash"
if [[ ! -d "$recipe" ]]; then
  staging=$(mktemp -d "$work/recipes/.staging.XXXXXX")
  cp "$repo/build/"{Dockerfile,package.py,releases.py,local.sh,termux.cmake,DONOR-LICENSE} "$repo/"{LICENSE,upstreams.json} "$staging/"
  if ! mv -T "$staging" "$recipe" 2>/dev/null; then rm -r "$staging"; fi
fi
image="localhost/bashkitten-localai-$os-$backend:builder"
podman build --target builder --build-arg "TARGETARCH=amd64" --build-arg "TARGETOS=$os" --build-arg "BACKEND=$backend" -t "$image" -f "$recipe/Dockerfile" "$repo"
# Cache and source are bind-mounted on the data drive. Unbounded compiler cache,
# active OpenMP wait policy and all 8 requested P cores. Memory cap is overridable.
podman run --rm --userns=keep-id --cpuset-cpus="${BUILD_CPUS:-0-7}" --memory="${BUILD_MEMORY:-40g}" \
  -e ENGINE="$engine" -e TARGETOS="$os" -e TARGETARCH="$arch" -e BACKEND="$backend" \
  -e SOURCE_COMMIT="${pin[1]}" -e UPSTREAM_VERSION="${pin[2]}" -e RELEASE_TAG="$engine-${pin[2]}-r${pin[3]}" \
  -e BUILDER_COMMIT="$builder_commit" -e BUILD_JOBS="${BUILD_JOBS:-8}" \
  -e OMP_NUM_THREADS=8 -e OMP_WAIT_POLICY=ACTIVE -e GOMP_SPINCOUNT=INFINITE \
  -e SOURCE_DIR=/src -e CACHE_DIR=/cache -e OUTPUT_DIR=/out -e BUILD_INPUTS=/recipe \
  -v "$src:/src" -v "$work/cache:/cache" -v "$work/artifacts:/out" \
  -v "$recipe:/recipe:ro" \
  "$image" taskset -c "${BUILD_CPUS:-0-7}" python3 /recipe/package.py 2>&1 | tee "$work/logs/$engine-$os-$arch-$backend.log"
}
main "$@"
