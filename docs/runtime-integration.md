# Runtime integration, verified 2026-10-08

## Router and Android

Run `llama-server --models-dir MODELS --host 127.0.0.1 --port 8080` without `-m` for
router mode. The process can remain available while no model is loaded. Preserve
user-controlled per-model launch options in the router presets. Use `-ngl 0` for
CPU together with `--device none`, or `-ngl all` for all layers on the selected GPU; Android has a CPU/GPU selector,
not a VRAM split UI. `--list-devices` lists actual available ggml devices.

Termux execution is native. Keep models under its private home for direct storage
access and configure its foreground/background service through BashKitten. Inspect
`vulkaninfo --summary` and llama's device list before declaring GPU availability;
llvmpipe is software, not a hardware GPU. Do not install/replace device drivers or
claim emulator graphics acceleration proves physical phone inference performance.

The upstream [Android guide](https://github.com/ggml-org/llama.cpp/blob/d81235049384534c167caea52b85a694f6103d14/docs/android.md)
recommends portable NDK flags: native architecture tuning off, OpenMP off, llamafile
off, OpenSSL off and API 28. Our builds follow these and bundle the NDK C++ runtime.
The official [Termux recipe](https://github.com/termux/termux-packages/blob/master/packages/llama-cpp/build.sh)
also builds dynamic Vulkan backends. On-device Termux builds use libandroid-spawn;
our API 28 NDK binaries select the vendored subprocess library's documented
`SUBPROCESS_SPAWN_VIA_FORK=1` implementation. Android API 28 lacks the
`posix_spawn_file_actions_addchdir_np` extension; native fork/exec preserves working
directories and exec failure reporting without that extension or source changes.
Upstream defaults `LLAMA_SUBPROCESS` to OFF on Android. These Termux builds
explicitly enable it; packaging checks the configured value and records
`capabilities.router` and `capabilities.subprocess` in the manifest and build
metadata, including `subprocessImplementation: fork-exec` on Android. A server that
only passes `--help` is not enough to validate router mode.

Set `LD_LIBRARY_PATH` to the selected runtime's `bin` directory. Leave
`GGML_BACKEND_PATH` unset: at this upstream version it names a single plugin file,
not a search directory. GGML discovers the sibling backend libraries itself.

Both GPU archive types include the CPU backend. For an explicitly CPU-only child,
set `GGML_VK_VISIBLE_DEVICES=''` (empty, not `-1`) for Vulkan or
`CUDA_VISIBLE_DEVICES=''` for CUDA, together with `--device none -ngl 0` for llama,
`--no-mmproj-offload` for CPU TTS, and `-ng` for Whisper/Parakeet. Vulkan still
creates its instance and enumerates physical devices before applying visibility;
the empty list prevents GPU device initialization, not loader enumeration. Scope
these settings to the child: a router with mixed CPU/GPU presets cannot globally
hide GPU devices. Per-model `device`, `gpu-layers`, `mmproj-offload` and `fit`
settings belong in the INI file; CLI arguments override per-model presets.

The upstream `sleep-idle-seconds` setting counts inactivity since use, excluding
active inference. UI minutes zero must map to `-1` (disabled); upstream rejects
zero. Positive minutes map to seconds. Sleep frees the model and its active KV
context, and a new request reloads it. There is no separate KV-cache TTL setting;
`cache-ram` is a MiB limit (zero disables, -1 unlimited), not a duration. Router
capacity eviction can still unload an idle model even if sleeping is disabled.
Router `GET /models` returns cached model metadata. `GET /health` and child
`GET /props` bypass the inference task queue and remain accessible during sleep.
These discovery requests do not reset the model's idle timer. Avoid using
`GET /slots` for passive status: it queues work and can wake/reset a model.

Upstream [Adreno subgroup fix](https://github.com/ggml-org/llama.cpp/issues/25734)
and [Termux shader compiler report](https://github.com/ggml-org/llama.cpp/issues/28234)
show why current engine and compiler versions matter. The [Mali discussion](https://github.com/ggml-org/llama.cpp/discussions/23193)
includes both success and software-only device reports. Do not force universal
Adreno/Mali workarounds or infer Vulkan support from a GPU name.

## Speech recognition

Whisper uses `whisper-server -m MODEL --host 127.0.0.1 --port 8081`, with multipart
`POST /inference` containing `file` audio and `response_format=json`.
`-ng` selects CPU. GPU is enabled by default when the selected backend supports it.

Parakeet is a separate API inside whisper.cpp. There is no Parakeet support in
`whisper-server` at the pinned commit. Use:

```sh
parakeet-cli -m MODEL -f - -np -ng < audio.wav
```

Omit `-ng` for GPU. Feed the in-memory recording to stdin (`-f -`); stdout is the
transcription and stderr contains diagnostics. No temporary audio file is needed.
The CLI can return success after an audio error, so an empty result must not be
silently sent. `ggml-org/parakeet-GGUF` publishes Q4_0, Q4_K, Q8_0 and F16 files;
these are the whisper.cpp format despite the repository's GGUF name.

## Speech synthesis

`llama-tts` is a command-line synthesizer, not a server and not `/v1/audio/speech`.

```sh
llama-tts -m MODEL.gguf -mm PROJECTOR.gguf -p 'Hello world' \
  --tts-speaker-file reference.wav --output out.wav -ngl 0
```

Qwen3-TTS accepts `--tts-lang en` and other documented languages. Pocket's language
is determined by its weights and requires a speaker reference. Both need the
matching multimodal projector/codec. Keep memory-only recording/processing policies
in the app; this example illustrates the upstream file interface only.

Official `ggml-org/Qwen3-TTS-12Hz-1.7B-Base-GGUF` provides Q4_K_M, Q8_0 and BF16
language-model weights plus Q8_0/BF16 projectors. The verified Pocket download is
`EryriLabs/pocket-tts-GGUF`'s English model/projector F16 pair. Popular Pocket
Q4/Q8 repositories for CrispASR, pockettts.cpp and other projects are incompatible
with llama-tts; do not put those into this runtime's catalog. Additional compatible
quants can be produced from the verified pair using bundled `llama-quantize`:

```sh
llama-quantize pocket-tts-en.gguf pocket-tts-en-Q4_0.gguf Q4_0
llama-quantize pocket-tts-en.gguf pocket-tts-en-Q8_0.gguf Q8_0
```

Keep the original matching `mmproj-pocket-tts-en.gguf`. The Q4_0 conversion was
validated with non-silent 24 kHz output on the local Vulkan GPU; F16 was validated
on CPU. Qwen3-TTS's official Q4_K_M/Q8_0 projector pair was also validated with
non-silent 24 kHz output with all language-model layers on Vulkan. Whisper
transcribed both generated Vulkan samples back to their exact test sentences.
These checks verify inference and intelligible audio, not subjective voice
quality. These generated files are local build outputs, not claimed upstream
hosted downloads. Test each generated quant before publication. All model source revisions, checksums and
licenses are in `models.json`.

The primary small language models are Qwen3.5 0.8B, 2B and 4B, sorted smallest first,
with plain Q4_0 as well as Q4_K_M and Q8_0. A Q4_0 option is a compatibility choice,
not a promise that every phone driver supports the model.

## Current device verification

The public `llama-v0.6.0-r1` and `android-llama-v0.6.0-r1` releases completed
on 8 October 2026. All 14 Linux and 8 Android checksum entries were verified,
including matching build metadata, full source recipes and license notices. All
six archives contain the correct-architecture executable `bin/llama-tts`. Both
package tags and embedded builder provenance identify recipe
`89fa3bf4db2bc51736e3f79649d434ae3b17598d`. Android x86_64 public archive SHA256
`a489f0bac4b829253a720f6c92523ee113ccb3e36c1dc08ea4938df8fc9caab6` matches the
artifact used for the native inference/router checks below.

The exact-release Android x86_64 Vulkan `v0.6.0-r1` llama artifact from Actions
run `37794302751` generated the correct Qwen3.5 0.8B Q4_0 answer in explicit CPU
mode (`device=none`, `gpu-layers=0`) with normal GPU visibility. Its native router
also loaded that model from an INI, spawned its child and returned the correct
answer through `/v1/chat/completions`; both processes exited after the check.
The published Android x86_64 Vulkan `v1.9.5-r1` whisper artifact transcribed the
upstream JFK sample correctly with `-ng` and empty Vulkan visibility. A repeat
under the Termux UID used two CPU threads, completed in 3.7 seconds and left no
CLI process. All 24 installed binaries/libraries matched the published archive
(SHA256 `dc3a224889214470d2f86950cff8410eda5b615e4948dd814ba8036f1a962bc2`).
No Parakeet model was present in the guest, so Android Parakeet inference remains
unverified. These checks use the new release bytes, not an earlier build with
similar version text; they do not verify microphone or application UI behavior.

The published Android x86_64 `v0.6.0-r1` Vulkan bundle also generated speech
with Pocket F16 and Qwen3-TTS 1.7B Q4_K_M under the Termux UID on Android 17
Cuttlefish. All 28 installed binary/library files matched the public archive.
Both stock `llama-tts` commands used explicit CPU mode (`--device none -ngl 0`,
empty `GGML_VK_VISIBLE_DEVICES`, two threads), exited successfully and left no
TTS process. They produced non-silent mono 24 kHz audio lasting 2.48 and 2.88
seconds respectively. Stock Whisper transcribed both as “The local speech
engine is ready.” The checks reused public models and the upstream JFK voice
sample without changing the active router or application configuration. This is
native-runtime verification, not LocalAI UI or physical-device GPU acceptance.

The exact published Linux amd64 CUDA `v0.6.0-r1` and `v1.9.5-r1` archives also
passed stock-binary inference checks on the RTX 5090 Laptop GPU. Qwen3.5 0.8B
Q4_0 returned “Two plus two equals four.” with all 25 layers on CUDA. Its router
loaded the same model from an INI, spawned a CUDA child and returned the same
answer through `/v1/chat/completions`. The router and child exited successfully,
with no remaining owned process or listener.

Whisper tiny Q5_1 and Parakeet Q4_0 each transcribed the upstream JFK sample
correctly with CUDA model buffers. Pocket Q4_0 and Qwen3-TTS Q4_K_M generated
non-silent 24 kHz speech; their logs confirm respectively 7/7 and 29/29 layers,
plus both codecs, on CUDA. Whisper transcribed both generated samples exactly as
“The local speech engine is ready.” All stock commands completed successfully;
GPU memory returned to its 16 MiB baseline and no CUDA compute process remained.
These checks reused existing public models, compiled no native code and changed
no application configuration. They establish artifact execution, not app UI
acceptance or physical ARM64 compatibility.

The additional historical evidence below covers previous `c811cb8f0ac9` llama
artifacts and released whisper v1.9.5.

The published Android Vulkan llama archive from recipe `3926d9a0290d` also
successfully generated coherent Qwen3.5 text on Cuttlefish with explicit CPU mode
and empty Vulkan visibility. This confirms the GPU archive's included CPU backend
works even when that guest's GPU compute device cannot initialize. The published
Android Vulkan whisper archive also transcribed the JFK sample correctly with
`-ng` and empty Vulkan visibility, exiting successfully.

The native Linux x86_64 CPU and Vulkan builds transcribed speech, synthesized
matching Pocket/Qwen3-TTS speech, and generated Qwen3.5 text. On stock Android 17
Cuttlefish, native x86_64 CPU Whisper transcription and Qwen3.5 generation passed.
Both Android architectures' packaged ELF files have at least 16 KiB load alignment;
the ARM64 binaries still need execution on a physical ARM64 device.

The published Linux CUDA releases built from recipe `8998bc4e4db9` were also
downloaded through BashKitten's managed installer and executed on an RTX 5090
Laptop GPU. Qwen3.5 0.8B Q4_0 generated the correct short answer with 25/25 layers
on CUDA. Whisper tiny Q5_1 and Parakeet Q4_0 transcribed the upstream JFK sample
correctly with CUDA model buffers. Pocket Q4_0 and Qwen3-TTS Q4_K_M generated
non-silent 24 kHz speech with every language-model layer and their codec on CUDA.
Whisper transcribed Qwen's test sentence exactly; Pocket's transcription changed
the initial article from “The” to “A”. These artifact checks do not replace app UI
acceptance or establish physical Android GPU compatibility.

The Cuttlefish Intel GFXStream device enumerates in Vulkan but the unmodified
upstream engine cannot create its inference device: the guest exposes 16-bit
storage in core Vulkan 1.1 without advertising `VK_KHR_16bit_storage`, which
upstream nevertheless requests. An isolated diagnostic patch removes that
extension-name failure, but the guest still fails upstream L2 normalization and
gated-delta-net correctness checks and generates incorrect text. That diagnostic
patch is not included in these builds. Vulkan graphics acceleration and device
enumeration alone therefore do not establish inference correctness. No automatic
CPU substitution or guest driver changes are performed.
