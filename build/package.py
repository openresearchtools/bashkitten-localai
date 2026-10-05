#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Build pinned upstream servers and their native libraries, with source/notices."""
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import tarfile

engine, backend, arch = (os.environ[name] for name in ('ENGINE', 'BACKEND', 'TARGETARCH'))
assert engine in ('llama', 'whisper') and backend in ('cpu', 'vulkan', 'cuda') and arch in ('amd64', 'arm64')
source = os.environ['SOURCE_COMMIT']
assert len(source) == 40 and all(c in '0123456789abcdef' for c in source)
root = Path('/src'); build = Path('/build'); payload = Path('/payload'); output = Path('/out')
for directory in (payload / 'bin', output): directory.mkdir(parents=True)
args = ['cmake', '-S', str(root), '-B', str(build), '-G', 'Ninja', '-DCMAKE_BUILD_TYPE=Release',
        '-DCMAKE_INSTALL_RPATH=$ORIGIN', '-DCMAKE_BUILD_WITH_INSTALL_RPATH=ON', '-DGGML_NATIVE=OFF',
        '-DGGML_BACKEND_DL=ON', '-DGGML_CPU_ALL_VARIANTS=ON', '-DBUILD_SHARED_LIBS=ON']
args += ['-DGGML_CUDA=' + ('ON' if backend == 'cuda' else 'OFF'), '-DGGML_VULKAN=' + ('ON' if backend == 'vulkan' else 'OFF')]
if engine == 'llama':
    args += ['-DLLAMA_BUILD_TESTS=OFF', '-DLLAMA_BUILD_EXAMPLES=OFF', '-DLLAMA_BUILD_TOOLS=ON', '-DLLAMA_BUILD_SERVER=ON',
             '-DLLAMA_BUILD_APP=OFF', '-DLLAMA_BUILD_UI=ON', '-DLLAMA_USE_PREBUILT_UI=OFF', '-DLLAMA_OPENSSL=OFF']
else:
    args += ['-DWHISPER_BUILD_TESTS=OFF', '-DWHISPER_BUILD_EXAMPLES=ON', '-DWHISPER_BUILD_SERVER=ON', '-DWHISPER_CURL=OFF']
subprocess.run(args, check=True)
subprocess.run(['cmake', '--build', str(build), '--parallel', str(min(os.cpu_count() or 2, 4))], check=True)
for filename in (build / 'bin').iterdir():
    if filename.is_file() and (filename.name == engine + '-server' or '.so' in filename.name):
        shutil.copy2(filename.resolve(), payload / 'bin' / filename.name)
assert (payload / 'bin' / (engine + '-server')).is_file()
if backend != 'cpu': assert (payload / 'bin' / ('libggml-' + backend + '.so')).is_file()
# Keep installed-library requirements explicit; never redistribute GPU drivers.
dependencies = subprocess.run(['ldd', str(payload / 'bin' / (engine + '-server'))], check=True, text=True, capture_output=True).stdout
record = {'version': 1, 'engine': engine, 'upstreamVersion': os.environ['UPSTREAM_VERSION'], 'sourceCommit': source,
          'os': 'linux', 'arch': arch, 'backend': backend, 'release': os.environ['RELEASE_TAG'], 'cmake': args, 'builderCommit': os.environ['BUILDER_COMMIT'],
          'externalLibraries': dependencies, 'minimumGlibc': '2.39',
          'cudaRequirements': 'NVIDIA driver >=580, CUDA 13 libcudart/libcublas' if backend == 'cuda' else None}
(payload / 'build.json').write_text(json.dumps(record, indent=2) + '\n')
(payload / 'SOURCE.json').write_text(json.dumps({'repository': 'https://github.com/ggml-org/' + engine + '.cpp', 'commit': source,
    'release': 'https://github.com/openresearchtools/bashkitten-localai/releases/tag/' + os.environ['RELEASE_TAG'],
    'build': 'https://github.com/openresearchtools/bashkitten-localai/tree/' + os.environ['BUILDER_COMMIT']}, indent=2) + '\n')
# Embedded frontend/vendor dependency license files are collected from the actual
# built tree, including npm dependencies. Full source below preserves each file.
if not (root / 'LICENSE').is_file(): raise RuntimeError('Upstream license is missing')
notices = ['===== BashKitten build integration (AGPL-3.0-only) =====\n' + Path('/build-license').read_text(), '===== MIT build recipe provenance =====\n' + Path('/donor-license').read_text()]
for filename in sorted(root.rglob('*')):
    if '.git' in filename.parts or not filename.is_file(): continue
    if filename.name.lower().startswith(('license', 'licence', 'copying', 'notice', 'copyright')):
        content = filename.read_bytes()
        try: text = content.decode('utf-8')
        except UnicodeDecodeError: continue
        notices.append('===== ' + str(filename.relative_to(root)) + ' =====\n' + text)
# Some upstream vendors keep the full MIT grant in their header rather
# than a separate LICENSE file; preserve that embedded notice too.
for filename in sorted(root.rglob('*.h')):
    if '.git' in filename.parts or not filename.is_file(): continue
    text = filename.read_text(errors='replace')
    for notice in re.findall(r'/\*[\s\S]*?\*/', text):
        if 'Permission is hereby granted' in notice:
            notices.append('===== ' + str(filename.relative_to(root)) + ' =====\n' + notice)
(payload / 'LICENSES.txt').write_text('\n\n'.join(notices))
(payload / 'BUILD-PACKAGES.txt').write_text(subprocess.check_output(['dpkg-query', '-W', '-f=${Package}\t${Version}\n'], text=True))
base = f'{engine}-{os.environ["UPSTREAM_VERSION"]}-linux-{arch}-{backend}'
archive = output / (base + '.tar.gz')
with tarfile.open(archive, 'w:gz') as tar:
    for child in sorted(payload.iterdir()): tar.add(child, arcname=child.name)
source_archive = output / (base + '-source.tar.gz')
with tarfile.open(source_archive, 'w:gz') as tar:
    tar.add(root, arcname='source', filter=lambda info: None if '/.git/' in info.name or info.name.endswith('/.git') else info)
    tar.add('/build-inputs', arcname='build')
    tar.add('/build-license', arcname='build/LICENSE')
sha = hashlib.file_digest(archive.open('rb'), 'sha256').hexdigest()
entry = {key: record[key] for key in ('engine', 'os', 'arch', 'backend', 'sourceCommit')}
entry.update(file=archive.name, sha256=sha, executable=engine + '-server')
(output / (base + '.json')).write_text(json.dumps(entry, indent=2) + '\n')
