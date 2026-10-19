# Native runtime corresponding source

This directory retains source for runtime/header code incorporated by the
packaged engines. It is copied into each matching `*-source.tar.gz`, together
with the exact engine, build recipe, compiler commands and per-target linker maps.
Nothing here is built as an AI engine on the workstation.

`android-r29/` is a pristine selected-source import, before the packaging changes:

* NDK r29 (29.0.14206865), Clang 21.0.0 / r563880c, ships the retained
  `clang_source_info.md` and `manifest_13989888.xml`. These identify LLVM base
  `386af4a5c64ab75eaee2448dc38f2e34a40bfed0`, Android patch/build commit
  `1dab3288f660d43a6cb2479107e2b54b3ab0a2a1`, and Google's corresponding patched
  LLVM checkout `5e96669f06077099aa41290cdb4c5e6fa0f59349`.
* Complete libc++, libc++abi, libunwind, compiler-rt, runtimes, CMake support,
  LLVM include and Clang builtin-header directories are retained from that
  exact LLVM base. The complete Android patch/build repository is retained
  separately, so the imported sources are not anonymously patched.
* Exact NDK r29 release-tag source (`196e0661200bad5361340700fea67be12e1f1684`)
  and Bionic (`a63b21091ada240d92f8ceadb1cabbdedaaab81b`) include the build
  recipes and CRT source incorporated into Android executables/DSOs. The
  toolchain-utils source referenced by Google's compiler manifest is retained.
* `SOURCE.json` records official archive URLs, full commits, archive SHA256s,
  source selection and the two shipped libc++ binary hashes. `SHA256SUMS`
  inventories every retained source/provenance file. Symlinks are inventoried
  by link text and never followed; upstream tooling links remain pristine.
  The complete NDK notices and compiler provenance are retained verbatim.

`ubuntu-24.04/` retains the exact original and Debian source-package archives
for the installed GCC 14 runtime/headers, glibc CRT/headers, Vulkan headers and
SPIRV headers. These are the release-tested compiler/package cohort used by
this builder, not independently upgraded runtime libraries. The original
signed `.dsc` files enumerate the archive SHA256s; `SOURCE.json` pins the same
files and versions. GCC's original source archive contains the complete GCC
and newlib source tarballs. Vulkan-Loader's distribution source includes the
matching complete Vulkan-Headers tree. The `*-LICENSES.txt` files collect full
license/notice files from these archives, including nested source archives.

`cuda-13.2/` retains the full official CCCL 3.2.0 source archive at
`477f8bcb27eb80c28e18bbd97e5dde80ecfc648b` (peeled release tag), and every
include-file source from the actual amd64/arm64 CUDA 13.2.86 compiler/runtime
header packages plus cuBLAS development headers 13.4.1.3. Original package URLs,
SHA256s, installed-file fingerprints and complete EULA/notices are recorded.
Both official NVIDIA package indexes are retained and verified against signed
InRelease metadata (key `EB693B3035CD5710E231E123A4B469963BF863CC`). Binary
compiler programs and CUDA libraries are not copied into runtime payloads.
The exact installed header/package fingerprints must match before a CUDA build.

Before compilation, `native_sources.py` verifies the retained files and exact
installed source-package versions. A changed distro package therefore fails
with an explicit source-refresh error. It also compares the NDK's compiler
manifest, patch list, notices, revision and ABI-specific libc++ hash. Source
snapshots and the compiler-content identity are included in cache provenance.

The runtime packages contain the engine/ggml DSOs and, on Android, libc++.
Linux glibc, libstdc++, libgcc, OpenMP and Vulkan remain system libraries.
CUDA 13's driver, cudart and cuBLAS were already external prerequisites; the
source repair does not add a toolkit installation requirement or change CUDA,
RDC, kernel or backend options. Linker maps additionally enumerate actual
static archive members and CRT objects: an unknown incorporated component
blocks packaging even when it is absent from `DT_NEEDED`. Merely listing an
unused static archive on a linker command does not establish incorporation.

The compiler program itself is not distributed in runtime archives. Its exact
provenance and build recipes are retained above; the selected LLVM tree is the
complete incorporated runtime/header source, not a claim to import the whole
LLVM compiler, Android platform or host operating system.

CUDA device-code source closure remains a separate inspection of the actual
final assets. The presence of a compiler libdevice input is not by itself proof
that a particular function was incorporated, and its bitcode is not described
as full corresponding source. CUDA metadata explicitly reports this pending
inspection and cannot pass the publication source gate yet. A device-link/RDC
stage also stops packaging for a separate incorporation audit; it is never
silently disabled. Vulkan's completed source checks are recorded separately.
