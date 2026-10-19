#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Verify retained corresponding sources before building or packaging native code."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess


def sha256(path):
    if path.is_symlink():
        return hashlib.sha256(os.readlink(path).encode()).hexdigest()
    with path.open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def verify_inventory(root):
    expected = {}
    for line in (root / 'SHA256SUMS').read_text().splitlines():
        digest, name = line.split('  ', 1)
        if not re.fullmatch('[0-9a-f]{64}', digest) or name in expected or Path(name).is_absolute() or '..' in Path(name).parts:
            raise RuntimeError(f'Invalid source inventory entry: {name}')
        expected[name] = digest
    actual = {str(p.relative_to(root)): sha256(p) for p in root.rglob('*')
              if (p.is_file() or p.is_symlink()) and p != root / 'SHA256SUMS'}
    if actual != expected:
        changed = sorted(name for name in actual.keys() | expected.keys() if actual.get(name) != expected.get(name))
        raise RuntimeError(f'Native source inventory mismatch: {changed[:10]}')
    return {'inventorySHA256': sha256(root / 'SHA256SUMS'), 'fileCount': len(expected)}


def verify_ubuntu(root, target_os, backend, query_packages=True):
    pins = json.loads((root / 'SOURCE.json').read_text())
    selected = {}
    for name, spec in pins['packages'].items():
        if target_os not in spec['targets'] or (name in ('vulkan-loader', 'spirv-headers') and backend != 'vulkan'):
            continue
        for item in [*spec['files'], spec['notices']]:
            path = root / item['file']
            if sha256(path) != item['sha256'] or ('size' in item and path.stat().st_size != item['size']):
                raise RuntimeError(f'Corresponding source changed: {path}')
        if query_packages:
            for binary in spec['binaryPackages']:
                actual = subprocess.check_output(['dpkg-query', '-W', '-f=${source:Package}\t${source:Version}', binary], text=True)
                if actual != name + '\t' + spec['version']:
                    raise RuntimeError(f'{binary}: installed source {actual!r} does not match retained {name} {spec["version"]}; refresh source pins before building')
        selected[name] = spec
    return selected


def verify_cuda(root, arch, query_packages=True):
    record = verify_inventory(root)
    pin = json.loads((root / 'SOURCE.json').read_text())
    if query_packages:
        for name, package in pin['packages'][arch].items():
            actual = subprocess.check_output(['dpkg-query', '-W', '-f=${Version}', name], text=True)
            if actual != package['version']:
                raise RuntimeError(f'{name}: installed {actual} differs from retained CUDA headers {package["version"]}')
            for filename, digest in package['retainedFiles'].items():
                if sha256(Path('/') / filename) != digest:
                    raise RuntimeError(f'Installed CUDA header/license differs from retained source: {filename}')
    record['provenance'] = pin
    return record


def audit_cuda_device_link(commands):
    if re.search(r'(?:^|\s)(?:-dlink|--device-link|--relocatable-device-code=true|-rdc=true)(?:\s|$)', commands):
        raise RuntimeError('CUDA device-link/RDC stage needs a separate static device-runtime incorporation audit; host maps are insufficient')


def verify_sources(inputs, target_os, arch, backend, ndk=None, query_packages=True):
    sources = inputs / 'native-sources'
    record = {'ubuntu': verify_ubuntu(sources / 'ubuntu-24.04', target_os, backend, query_packages)}
    if backend == 'cuda':
        record['cuda'] = verify_cuda(sources / 'cuda-13.2', arch, query_packages)
    if target_os == 'android':
        retained = sources / 'android-r29'
        record['android'] = verify_inventory(retained)
        pin = json.loads((retained / 'SOURCE.json').read_text())
        record['android']['provenance'] = pin
        if ndk is not None:
            toolchain = ndk / 'toolchains/llvm/prebuilt/linux-x86_64'
            for name in ('AndroidVersion.txt', 'clang_source_info.md', 'manifest_13989888.xml'):
                if sha256(toolchain / name) != sha256(retained / 'provenance' / name):
                    raise RuntimeError(f'NDK compiler provenance differs: {name}')
            for name in ('source.properties', 'NOTICE', 'NOTICE.toolchain'):
                if sha256(ndk / name) != sha256(retained / 'provenance' / name):
                    raise RuntimeError(f'NDK provenance differs: {name}')
            triple = 'x86_64-linux-android' if arch == 'amd64' else 'aarch64-linux-android'
            runtime = toolchain / 'sysroot/usr/lib' / triple / 'libc++_shared.so'
            if sha256(runtime) != pin['libcxxShared'][arch]:
                raise RuntimeError('NDK libc++ does not match the retained source provenance')
    return record


def native_notices(inputs, record):
    root = inputs / 'native-sources/ubuntu-24.04'
    notices = ['===== ' + name + ' corresponding runtime/header sources =====\n' + (root / spec['notices']['file']).read_text()
            for name, spec in record['ubuntu'].items()]
    if 'cuda' in record:
        for name in ('CUDA-LICENSE.txt', 'CCCL-LICENSES.txt'):
            notices.append('===== CUDA compiler/header ' + name + ' =====\n' + (inputs / 'native-sources/cuda-13.2' / name).read_text())
    return notices


def audit_libraries(binary_dir, executables, target_os, backend, readelf):
    bundled = {p.name for p in binary_dir.iterdir() if p.is_file()}
    engine_library = r'lib(?:ggml(?:-[\w-]+)?|whisper|parakeet|llama(?:-common)?|mtmd|common)\.so(?:\.\d+)*'
    for name in bundled - set(executables):
        if not re.fullmatch(engine_library, name) and not (target_os == 'android' and name == 'libc++_shared.so'):
            raise RuntimeError(f'Unmapped bundled native library: {name}')
    if target_os == 'android':
        platform = {'libc.so', 'libm.so', 'libdl.so', 'libvulkan.so'}
    else:
        platform = {'libc.so.6', 'libm.so.6', 'libdl.so.2', 'libpthread.so.0', 'librt.so.1',
                    'libstdc++.so.6', 'libgcc_s.so.1', 'libgomp.so.1', 'ld-linux-x86-64.so.2', 'ld-linux-aarch64.so.1'}
        platform |= {'libvulkan.so.1'} if backend == 'vulkan' else {'libcuda.so.1', 'libcudart.so.13', 'libcublas.so.13', 'libcublasLt.so.13'}
    result = {}
    for name in sorted(bundled):
        dynamic = subprocess.check_output([str(readelf), '-d', str(binary_dir / name)], text=True)
        needed = re.findall(r'\(NEEDED\).*?\[([^\]]+)\]', dynamic)
        unknown = set(needed) - bundled - platform
        if unknown:
            raise RuntimeError(f'{name}: external libraries without a source/system classification: {sorted(unknown)}')
        result[name] = {'sha256': sha256(binary_dir / name), 'bundledDependencies': sorted(set(needed) & bundled),
                        'platformDependencies': sorted(set(needed) - bundled)}
    return result


def audit_static_maps(build, binary_dir, target_os, ndk=None):
    result = {}
    for binary in sorted(binary_dir.iterdir()):
        if not binary.is_file() or binary.name == 'libc++_shared.so':
            continue
        link_map = build / 'bin' / (binary.name + '.native-link-map')
        # Versioned SONAME copies resolve to the same actual build output.
        if not link_map.is_file():
            original = (build / 'bin' / binary.name).resolve()
            link_map = original.with_name(original.name + '.native-link-map')
        if not link_map.is_file():
            raise RuntimeError(f'Missing static linkage evidence: {binary.name}')
        text = link_map.read_text(errors='replace')
        # GNU ld and lld both print archive(member) for incorporated sections.
        members = sorted(set(re.findall(r'([^\s()]+\.a)\(([^)\n]+)\)', text)))
        classified = []
        for archive, member in members:
            path = Path(archive)
            resolved = (build / path).resolve() if not path.is_absolute() else path.resolve()
            if resolved.is_relative_to(build.resolve()):
                source = 'engine-source'
            elif target_os == 'android' and ndk and resolved.is_relative_to(ndk.resolve()) and re.fullmatch(r'lib(?:clang_rt\.[\w.-]+|unwind|c\+\+abi|c\+\+_static)\.a', path.name):
                source = 'android-r29'
            elif target_os == 'linux' and re.fullmatch(r'lib(?:gcc(?:_eh)?|stdc\+\+|supc\+\+|gomp)\.a', path.name) and str(resolved).startswith('/usr/lib/gcc/') and '/14/' in str(resolved):
                source = 'gcc-14'
            elif target_os == 'linux' and path.name in ('libc_nonshared.a', 'libpthread_nonshared.a') and str(resolved).startswith('/usr/lib/'):
                source = 'glibc'
            else:
                raise RuntimeError(f'{binary.name}: incorporated archive member without corresponding source: {archive}({member})')
            classified.append({'archive': archive, 'member': member, 'source': source})
        external_objects = []
        for obj in sorted(set(re.findall(r'(?:^|\s)([^\s()]+\.o)(?=[:\s])', text, re.M))):
            path = Path(obj)
            resolved = (build / path).resolve() if not path.is_absolute() else path.resolve()
            if resolved.is_relative_to(build.resolve()):
                continue
            if target_os == 'android' and ndk and resolved.is_relative_to(ndk.resolve()) and path.name.startswith('crt'):
                origin = 'android-r29/bionic'
            elif target_os == 'linux' and path.name.startswith('crt') and str(resolved).startswith('/usr/lib/gcc/') and '/14/' in str(resolved):
                origin = 'gcc-14'
            elif target_os == 'linux' and re.fullmatch(r'[Srg]?crt[\w]*\.o', path.name) and str(resolved).startswith('/usr/lib/') and not str(resolved).startswith('/usr/lib/gcc/'):
                origin = 'glibc'
            else:
                raise RuntimeError(f'{binary.name}: incorporated object without corresponding source: {obj}')
            external_objects.append({'object': obj, 'source': origin})
        result[binary.name] = {'map': str(link_map.relative_to(build)), 'sha256': sha256(link_map),
                               'staticMembers': classified, 'externalObjects': external_objects}
    return result
