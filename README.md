# BashKitten LocalAI runtimes

![Testing releases: current releases are for automated testing only. Not ready for production. Coming soon.](docs/testing-releases.svg)

Testing-only native Linux builds of mainstream llama.cpp and whisper.cpp for
amd64 and arm64, with separate CPU, Vulkan and CUDA variants. These are not ready
for production. No TurboQuant, model weights, GPU drivers or product UI lives here.

`upstreams.json` pins each engine. Run **Build pinned LocalAI runtimes** for one
engine; every matrix job uploads its archive and corresponding source immediately
for manual download from Actions. Publication is an explicit workflow option.
Engine-prefixed releases include checksums, a machine-readable manifest, full
source, actual dependency notices and build records. Rebuild source changes under
a new tag; do not replace published bytes.

Linux builds require glibc 2.39 or later. CUDA requires NVIDIA driver 580 or later
and CUDA 13 libcudart/libcublas; Vulkan requires a functioning Vulkan loader/driver.
The CPU artifact requires neither GPU stack. BashKitten reports incompatible
libraries/devices without changing system drivers or substituting another runtime.

Build recipes adapt the MIT-licensed mainstream workflow from
[llama-cpp-arm64-builds](https://github.com/openresearchtools/llama-cpp-arm64-builds/tree/d6e2239e6b96365b6c79391c137c4e1e4df2944c).
Upstream source remains unmodified with its original licenses. Product integration
and LocalAI controls remain in [BashKitten](https://github.com/openresearchtools/BashKitten).
