![Testing releases: current releases are for automated testing only. Not ready for production. Coming soon.](https://raw.githubusercontent.com/openresearchtools/bashkitten-localai/main/docs/testing-releases.svg)

**Testing releases only. Not ready for production.**

Stable released upstream llama.cpp (including llama-tts) or whisper.cpp (including
Parakeet CLI) runtimes. Linux amd64/arm64: Vulkan and CUDA archives. Native Android API 28+
aarch64/x86_64: Vulkan archives. Every archive also supports explicit CPU execution. Model weights and drivers are not included.

**TTS download:** select the matching llama archive and run `bin/llama-tts`
for Pocket TTS or Qwen3-TTS. The same archive contains `bin/llama-server`,
`bin/llama-cli` and `bin/llama-quantize`; TTS models are separate downloads.
Whisper archives contain both Whisper and Parakeet executables.

The project's build integration is MIT licensed; upstream and dependency notices
remain in `LICENSES.txt` and the corresponding source archives.

Versions use the upstream release tag plus our package revision (r1, r2, etc.).
The manifest verifies the release tag’s peeled commit. Each archive records its exact sources, ABI, executables, linked libraries and
licenses. Matching source archives, manifest and SHA256SUMS accompany the
release. CUDA engines also incorporate NVIDIA device math/compiler runtime code
under NVIDIA's own license; its original implementation source is unavailable.
The archives retain full NVIDIA notices and exact binary-input provenance rather
than claiming that component is MIT-licensed or supplied as original source.
Build success does not establish hardware/device or full BashKitten
acceptance. See the runtime integration document for supported interfaces.
