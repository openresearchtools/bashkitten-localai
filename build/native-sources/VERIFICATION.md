# 19 October 2026 source-delivery repair

The audit of daughter run `39323147173` at
`85ac10fdc934273c09271fa55f040859eef70cd3` found that both Android
Whisper r3 artifacts shipped NDK r29 libc++ and its complete notice but their
2,177-file source archives omitted its corresponding source. Those artifacts
are not source-complete and must not be published as the repaired recipe.

The pristine source imports are `e3b1aa1` (Android, 24,293 inventoried source and
provenance files) and `785a48a8` (Ubuntu original/packaging source archives).
The exact Ubuntu versions match `BUILD-PACKAGES.txt` in all four available
Vulkan artifacts: GCC 14.2.0-4ubuntu2~24.04.1, glibc 2.39-0ubuntu8.9,
Vulkan-Loader/Headers 1.3.275.0-1build1 and
SPIRV-Headers 1.6.1+1.4.309.0-1~ubuntu0.24.04.2.

Completed bounded verification:

* Six source/linkage unit tests, including complete retained-source hashes,
  both Linux backend selections and Android selection, missing/changed/extra
  files, changed installed source version, unknown static incorporation,
  mismatched compiler CRT and missing linker evidence.
* Tiny standalone C++ shared-library links (not AI engine builds) exercised the
  CMake link wrapper with the host GNU linker and NDK r29 x86_64/arm64-v8a
  Android API 28 linkers. Both Android maps identify Bionic CRT objects; both
  ABI-specific libc++ and complete NDK provenance fingerprints match. The host
  is GCC 15 and is deliberately rejected as the GCC 14 release source cohort.
* A real 27,722-member native-source delivery tar was created and inspected,
  including runtime source, compiler-rt builtins, Android patches, Bionic CRT
  and the complete GCC nested source archive. This is a source-delivery test,
  not a runtime release or a relabelled old artifact.
* Python compilation, shell syntax and whitespace checks pass.
* Published `whisper-v1.9.5-r2` Linux amd64 CUDA contains only engine/ggml
  libraries and executables. Its CUDA backend dynamically needs cudart13,
  cuBLAS13 and the driver; cudaMalloc/cudaFree/cudaLaunchKernel symbols resolve
  to `libcudart.so.13`. Its metadata already declares those system prerequisites.
  Main BashKitten's readiness check also requires these DSOs and driver >=580.

No CUDA compiler/RDC/backend flags were changed, and no AI engine was built
locally. `DT_NEEDED` and unresolved CUDA symbols alone do not prove absence of
statically incorporated device/runtime code. The new packaging gate therefore
requires actual per-target linker maps and rejects every unknown incorporated
archive member or external CRT object. The final CI CUDA artifacts must pass
this gate and receive independent source/artifact inspection before publication.

Whisper r3 remains unpublished and keeps that revision. Llama r1 is already
published, so its repaired future artifacts use r2. Existing releases/tags are
not rewritten. A corrective CI run and installed CPU/GPU/Android acceptance
remain pending; these source and helper checks do not establish that acceptance.

CUDA header audit additionally found CCCL and toolkit header code omitted from
the old source archives. Pristine import `60354bc9` retains full CCCL 3.2.0
release source and all include files from five exact NVIDIA development/compiler
packages for each architecture, with their full notices. Both repository
InRelease signatures and package-index hashes were verified before import.
These source files are checked against actual installed package/file fingerprints.

CUDA source closure is explicitly `pending-cuda-device-code-inspection` in
artifact metadata, so a successful host static-map check cannot permit CUDA
publication by itself. This records missing evidence, not a claim that a specific
libdevice function was incorporated into a particular artifact. Commands and
link maps are retained for the required final inspection. Unknown static inputs
fail packaging; a device-link/RDC stage requires its own audit. Compiler caches
and diagnostics are saved even when a source gate blocks packaging.
