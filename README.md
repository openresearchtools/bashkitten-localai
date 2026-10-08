# BashKitten LocalAI runtimes

![Testing releases: current releases are for automated testing only. Not ready for production. Coming soon.](docs/testing-releases.svg)

Pinned, unchanged mainstream llama.cpp and whisper.cpp runtimes. Linux amd64 and
arm64 support CPU, Vulkan and CUDA; native Android/Termux aarch64 and x86_64 support
CPU and Vulkan. Android artifacts use the NDK's Bionic ABI, not Linux glibc binaries.

`upstreams.json` pins exact commits. Llama follows the verified 2026-10-08 mainstream
commit after v0.6.0 for current mobile GPU fixes; whisper is v1.9.5. No fork or
TurboQuant patch is applied. Model weights and GPU drivers are not bundled.

Llama archives include `bin/llama-server`, `llama-cli`, `llama-tts`, and
`llama-quantize`; whisper archives include `whisper-server`, `whisper-cli`,
`parakeet-cli`, and `parakeet-quantize`. Shared libraries live beside executables.
Parakeet uses its CLI, **not whisper-server**. Pocket TTS and Qwen3-TTS use
llama.cpp's own `llama-tts`, not a similarly named third-party runtime.

## Cached local builds

```sh
./build/local.sh llama linux amd64 cpu
./build/local.sh llama linux amd64 vulkan
./build/local.sh llama linux amd64 cuda
./build/local.sh llama android arm64 vulkan
./build/local.sh whisper android amd64 cpu
```

Run the same command for the other supported engine/platform/backend combinations.
Native Linux arm64 builds run on Actions' arm64 worker. Android cross-compilation
runs on amd64 using pinned Android NDK r29, API 28. No QEMU or proot is involved in
running these binaries inside Termux.

Local source, CMake trees, unlimited ccache, npm cache, artifacts and logs default to
`/run/media/user/Data/BashkittenBuild/localai`. Set `BASHKITTEN_LOCALAI_WORK` to change
this root. Local builds use CPUs 0–7, eight build jobs, active OpenMP waits and a
40 GiB cap; override `BUILD_CPUS`, `BUILD_JOBS`, or `BUILD_MEMORY` as needed. Podman
retains image layers and every build reuses its platform/backend CMake tree.

The Actions workflow also persists CMake/ccache/npm caches and builder layers.
Every matrix job uploads its archive and complete source immediately; publishing
is a workflow option after the full Linux/Android matrix succeeds. Release assets
contain manifest v1 with `os`, `arch`, `backend`, `sourceCommit`, `file`, `sha256`,
`executable`, and `executables`. Android uses `os: android`, `arch: arm64|amd64` and
`minimumAndroidApi: 28`. Rebuild under a new immutable tag.

Linux artifacts require glibc 2.39+, libstdc++6, libgcc-s1 and libgomp1. CUDA needs a
CUDA 13 compatible NVIDIA driver and matching libcudart/libcublas. Vulkan needs a
working platform Vulkan loader and hardware driver. Android includes NDK
`libc++_shared.so` and its notice; no Termux libc++ package mismatch is required.
Keep `LD_LIBRARY_PATH` pointed at the selected archive's `bin` directory. CPU/GPU
selection must be explicit; runtime failure never silently changes backends.

See [runtime integration](docs/runtime-integration.md) for commands, compatible
model assets and Android GPU considerations. `models.json` records verified
Hugging Face revisions, byte sizes and SHA256s. Product UI remains in
[BashKitten](https://github.com/openresearchtools/BashKitten).

Build recipes derive from MIT-licensed
[llama-cpp-arm64-builds](https://github.com/openresearchtools/llama-cpp-arm64-builds/tree/d6e2239e6b96365b6c79391c137c4e1e4df2944c).
Archives include upstream licenses, actual dependency notices and full source.
