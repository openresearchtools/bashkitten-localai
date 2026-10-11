# Streaming speech activity helper

`main.cpp` is BashKitten's small MIT-licensed adapter around whisper.cpp's public
streaming Silero VAD API. It does not change the released engine. CMake adds it
through `CMAKE_PROJECT_INCLUDE`; it is built in the same CI matrix and links the
same packaged Whisper/ggml libraries.

Run `bin/bashkitten-vad models/ggml-silero-v6.2.0.bin`. After successful CPU model
initialization stdout emits `READY\n`. Feed 16 kHz mono signed PCM16 little-endian,
exactly 512 samples per frame. Each frame yields one float32 little-endian speech
probability (0–1). Recurrent state persists between frames. EOF exits and releases
state; partial frames, invalid input/model or inference failures exit nonzero.
Diagnostics use stderr. There are no files, listeners, telemetry or audio logs.
The calling app owns VAD thresholds, silence timing, cancellation and lifetime.

## Sources and reproducible conversion

`SOURCE.json` pins every imported byte. The complete pristine Silero source is
release **v6.2** (`pyproject.toml` package version **6.2.0**) at
`be95df9152c0d7618fa1edfeb296fc3dae32376f`; it includes the original TorchScript
weights, MIT license and upstream conversion-related code. The unchanged
converter and its MIT license come from Whisper **v1.9.5**, commit
`d1be6fde11ac6e0407606b4e42fe72d34add8037`. These sources stay independently pinned
when daily checks update the engine; an engine update still has to compile and
pass the helper protocol checks.

The hosted GGML model is pinned at Hugging Face `ggml-org/whisper-vad` revision
`9ffd54a1e1ee413ddf265af9913beaf518d1639b`, SHA256
`2aa269b785eeb53a82983a20501ddf7c1d9c48e33ab63a41391ac6c9f7fb6987` (885098 bytes).
It is the 16 kHz model only. The released converter stores convolution weights
and the STFT basis as float16, and LSTM weights/biases and other biases as
float32. It is not a uniformly float16 or quantized-integer model.

On 11 October 2026, conversion from the committed Silero TorchScript model using
PyTorch 2.9.1+cpu and NumPy 2.3.5 produced that exact file byte for byte. Run
`python3 build/vad/verify.py --reproduce` with those two verification dependencies
to repeat it; no native engine is compiled. CI performs the reproduction before
any Whisper matrix build. Every package also verifies the committed source and
model checksums before configuring CMake. The Python libraries are verification
tools only and are not shipped or used on phones.

The runtime archive contains the small GGML model, helper, full MIT notices and
`models/VAD-SOURCE.json`. The matching source archive contains this entire
recipe, pristine donor sources, original weights, converter and pinned model.
Only the helper and GGML model are executed at runtime; upstream examples,
notebooks, workflows and their optional dependencies are provenance, not runtime
components. No model download or external service is used by this helper.
