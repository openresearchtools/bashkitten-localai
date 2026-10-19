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
InRelease metadata (key `EB693B3035CD5710E231E123A4B469963BF863CC`). Standalone binary
compiler programs and CUDA DSOs are not copied into runtime payloads. Exact
libdevice bitcode is retained as a binary compiler input in the matching source/
provenance archive, explicitly not as original human-readable source.

The runtime packages contain engine/ggml libraries and, on Android, libc++.
Linux glibc, libstdc++, libgcc, OpenMP and Vulkan remain system libraries.
CUDA 13's driver, cudart and cuBLAS remain external prerequisites.

On 19 October 2026 the user directed removal of the additional blocking native
source audits from this separate MIT runtime repository. The library-name lists,
source-package version matching, static-link classification and publication
attestation gates are removed. Retained source records, full notices, actual
build-package versions and archive hashes remain delivered. Historical audit
results in VERIFICATION.md describe those earlier builds, not current gates.

NVIDIA compiler/runtime components retain NVIDIA's license. Original libdevice
implementation source is unavailable; its retained bitcode is identified as a
binary input, not original source. This does not change the browser's AGPL/MPL
boundary. Runtime builds keep their official upstream release pins, checksums,
executable smoke checks and Android ABI/alignment verification.
