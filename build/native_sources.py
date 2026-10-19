#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Package retained third-party notices and source records with runtime builds."""
import hashlib
import json
import os


def sha256(path):
    if path.is_symlink():
        return hashlib.sha256(os.readlink(path).encode()).hexdigest()
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def retained_sources(inputs, target_os, backend):
    root = inputs / 'native-sources'
    ubuntu = json.loads((root / 'ubuntu-24.04/SOURCE.json').read_text())
    record = {'ubuntu': {name: spec for name, spec in ubuntu['packages'].items()
              if target_os in spec['targets'] and
              (name not in ('vulkan-loader', 'spirv-headers') or backend == 'vulkan')}}
    if backend == 'cuda':
        record['cuda'] = {'provenance': json.loads((root / 'cuda-13.2/SOURCE.json').read_text())}
    if target_os == 'android':
        record['android'] = {'provenance': json.loads((root / 'android-r29/SOURCE.json').read_text())}
    return record


def native_notices(inputs, record):
    root = inputs / 'native-sources/ubuntu-24.04'
    notices = ['===== ' + name + ' corresponding runtime/header sources =====\n' + (root / spec['notices']['file']).read_text()
            for name, spec in record['ubuntu'].items()]
    if 'cuda' in record:
        for name in ('CUDA-LICENSE.txt', 'CCCL-LICENSES.txt'):
            notices.append('===== NVIDIA CUDA component ' + name + ' =====\n' + (inputs / 'native-sources/cuda-13.2' / name).read_text())
        notices.append('NVIDIA libdevice and compiler/runtime implementation code retain the NVIDIA CUDA license, not MIT. Original implementation source is unavailable; retained bitcode and exact package/input hashes are identified in build/native-sources/cuda-13.2/SOURCE.json. CUDA driver, cudart and cuBLAS DSOs remain external prerequisites.')
    return notices
