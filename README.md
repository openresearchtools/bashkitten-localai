# BashKitten LocalAI · llama.cpp, llama-tts, Whisper and Parakeet

![Testing releases: current releases are for automated testing only. Not ready for production. Coming soon.](docs/testing-releases.svg)

Unchanged stable upstream release sources for llama.cpp and whisper.cpp. Linux
amd64 and arm64 provide Vulkan and CUDA archives; native Android/Termux aarch64
and x86_64 provide Vulkan archives. **Every archive includes CPU execution**, so
separate CPU downloads are unnecessary. Android uses the NDK's Bionic ABI.

`upstreams.json` records the stable release version, its annotated tag object, its
peeled commit, release URL/ID and our integer package revision. Llama is v0.6.0;
whisper is v1.9.5. The build verifies the actual release tag, not GitHub's
`target_commitish` field. No fork or GPU workaround patch is applied. Model weights
and GPU drivers are not bundled.

**Text to speech is included in every llama archive as `bin/llama-tts`.** It is
built from the same official llama.cpp release as the router; it is not a separate
repository or download. Pocket TTS and Qwen3-TTS model files remain separate.

Llama archives include `bin/llama-server`, `llama-cli`, `llama-tts`, and
`llama-quantize`; whisper archives include `whisper-server`, `whisper-cli`,
`parakeet-cli`, and `parakeet-quantize`. Shared libraries live beside executables.
Parakeet uses its CLI, **not whisper-server**. Pocket TTS and Qwen3-TTS use
llama.cpp's own `llama-tts`, not a similarly named third-party runtime.

## Release builds

All project runtime builds run in GitHub Actions. The full matrix is six archives
per engine: Linux amd64/arm64 × Vulkan/CUDA, plus Android amd64/arm64 × Vulkan.
Native Linux arm64 uses an arm64 runner; Android cross-compiles with pinned NDK
r29, API 28. Execution in Termux uses neither QEMU nor proot.

[The daily workflow](.github/workflows/releases.yml) checks upstream stable
releases at 03:00 UTC. It verifies the current pinned tag has not moved, then
updates and builds only a strictly newer semantic release. An unchanged version,
a moved backwards `latest` pointer, or unrelated packaging commits do not trigger
builds. Moved/recreated release tags fail verification instead of silently changing
source. Build failures require inspection and an explicit manual retry.

For a packaging fix to the same upstream release, increment `packageRevision` in
`upstreams.json`, commit it and manually dispatch `build.yml`. Revision 1 produces
`llama-v0.6.0-r1` and `android-llama-v0.6.0-r1` (likewise whisper). Existing release
tags cannot be overwritten; source SHA and recipe SHA remain in metadata rather
than being used as user-facing version suffixes. `build/local.sh` remains an
optional recipe entry point for other contributors; this project's runtime
production and validation do not require local compilation.

Actions persist CMake/ccache/npm caches and builder layers. Each matrix job uploads
its archive and complete source immediately. Optional publication waits until the
complete requested matrix passes. Desktop tags start with `llama-` or `whisper-`;
Android tags start with `android-llama-` or `android-whisper-`, so one platform's
release cannot displace another platform's downloads.

Manifest v1 records `upstreamRelease` (`tag`, peeled `commit`, `url`, `releaseId`,
`tagObject`) and integer `packageRevision`. Each artifact repeats that provenance
and contains `os`, `arch`, `backend`, `sourceCommit`, `file`, `sha256`, `executable`,
`executables`, plus `capabilities.cpu: true` and `executionBackends` inside
`capabilities`. Android uses `os: android`, `arch: arm64|amd64`, `backend: vulkan`
and `minimumAndroidApi: 28`. Payloads include full license notices, build metadata,
and links to their corresponding source archives.

Linux artifacts require glibc 2.39+, libstdc++6, libgcc-s1 and libgomp1. CUDA needs a
CUDA 13 compatible NVIDIA driver and matching libcudart/libcublas. Vulkan needs a
working platform Vulkan loader and hardware driver. Android includes NDK
`libc++_shared.so` and its notice; no Termux libc++ package mismatch is required.
Keep `LD_LIBRARY_PATH` pointed at the selected archive's `bin` directory. CPU/GPU
selection must be explicit; runtime failure never silently changes backends.
Leave `GGML_BACKEND_PATH` unset; it names a single library, not a directory.
Llama builds explicitly enable subprocess support, including on Android, for the
router to launch model workers. Build metadata and manifests record this capability.

See [runtime integration](docs/runtime-integration.md) for commands, compatible
model assets and Android GPU considerations. `models.json` records verified
Hugging Face revisions, byte sizes and SHA256s. Product UI remains in
[BashKitten](https://github.com/openresearchtools/BashKitten).

Build recipes derive from MIT-licensed
[llama-cpp-arm64-builds](https://github.com/openresearchtools/llama-cpp-arm64-builds/tree/d6e2239e6b96365b6c79391c137c4e1e4df2944c).
Archives include upstream licenses, actual dependency notices and full source.

## Licenses

This repository's own build integration and documentation are **MIT licensed**;
see [LICENSE](LICENSE). The original MIT recipe attribution remains in
[build/DONOR-LICENSE](build/DONOR-LICENSE). Upstream llama.cpp, whisper.cpp and
their dependencies retain their own licenses, which are collected in each
archive's `LICENSES.txt` (and Android NDK notice). The BashKitten application is
a separate repository with its own license.

Packages built from earlier recipe revisions (including r1) preserve their
original source and recipe notices. Their files and tags are immutable; this license
change does not overwrite historical archives or trigger engine recompilation.
Future package revisions use the MIT build-integration notice.
