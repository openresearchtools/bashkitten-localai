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


## Completed old Linux arm64 CUDA artifact inspection

Run `39323147173`, job `118302617084`, artifact `12222848457` completed
successfully at the old recipe `85ac10fdc934273c09271fa55f040859eef70cd3`.
Its `bin/libggml-cuda.so` is 160,470,240 bytes, SHA-256
`5bd30193d81a4b0c8c89c188b61ae82e816ca6ef5d50451008def77144785dfd`.
It is the only one of the archive's 26 regular ELF files with a CUDA fatbin.
The installed package inventory confirms CUDA 13.2.86, GCC
14.2.0-4ubuntu2~24.04.1 and glibc 2.39-0ubuntu8.9.

Offline NVIDIA `cuobjdump` 13.2.86 inspection demonstrates actual incorporated
libdevice math: the delivered PTX `op_gelu_erf` kernel contains both seven-term
coefficient sets and the branch threshold from `__nv_erff` in the exact
13.2.86 `libdevice.10.bc`. All 15 floating-point bit patterns match, along with
the absolute-value/square selection, fused polynomial evaluation and signed
exponential tail. The upstream kernel calls `erff`; the retained CUDA headers
provide its declaration, not this device implementation. This is actual inlined
library code in the shipped asset, not merely a toolkit dependency or an
unresolved dynamic symbol.

The official arm64 `libnvvm-13-2_13.2.86-1_arm64.deb` SHA-256 is
`fa22d6cf5151304d681b9ae1ccd72d5bfbacf1e2bf30ccee1f149e0f87b2c375`;
its libdevice SHA-256 is
`0c6b4d4e4c033e2faffcc6f671c68fec5e813020845a5a08f1dbdd35c19629d6`
(and matches the amd64 package). Package integrity was checked against the
previously signature-verified NVIDIA index. LLVM bitcode decoding here was
inspection only; it did not compile an engine or access a GPU.

NVIDIA documents [libdevice inlining during compilation](https://docs.nvidia.com/cuda/archive/13.2.0/libdevice-users-guide/basic-usage.html)
and lists `libdevice.10.bc` as a distributable component in the
[CUDA 13.2 license](https://docs.nvidia.com/cuda/archive/13.2.0/eula/index.html).
That conditional binary redistribution permission does not supply original
human-readable implementation source. The official package supplies bitcode;
neither that bitcode nor its decoded IR/PTX is relabelled as full corresponding
source. The current source requirement therefore remains unmet for this
confirmed incorporated component. Full notices and the repaired header/CCCL
sources do not resolve this specific gap.

Device ELF symbols also contain compiler-generated division, remainder,
reciprocal and warp helpers. The old nonverbose job log and delivered archives
contain no compiler command graph, host linker maps or device-link intermediates
that attribute these to exact compiler inputs. No `cudaLaunchDevice`,
`cudaGetParameterBuffer` or `cudadevrt` markers were found in the device symbol
dump; this does **not** prove that no libcudadevrt archive member was incorporated.
No linkage or kernel changes are justified by that absence alone.

The queued corrective run `39330013225` at `511454d5` remains unchanged and
unpublished. Its existing diagnostics will support direct command/map review;
this inspection adds no approval mechanism or permanent attestation requirement.
Resolving CUDA publication requires the missing implementation source, or an
explicitly authorized change to the existing source requirement or supported
implementation. No such change is inferred here. Vulkan source verification is
separate and does not acquire this CUDA-specific limitation.

Raw job log, original ZIP, all ELF hashes, PTX/ELF-symbol dumps, the exact
coefficient comparison and package provenance are saved outside the repository
under `daughter-artifacts/old-linux-arm64-cuda/` in the existing
`component-refresh-20261019` acceptance directory. No AI engine was built or run
locally, no host NVIDIA installation changed, and no CI run was dispatched or
cancelled for this inspection.
