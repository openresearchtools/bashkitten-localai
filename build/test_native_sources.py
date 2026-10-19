#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Bounded source and linkage gate tests; never builds an AI engine."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from native_sources import describe_source_closure, audit_libraries, audit_static_maps, verify_inventory, verify_sources, verify_ubuntu, verify_cuda


class SourceGates(unittest.TestCase):
    def test_inventory_missing_changed_extra_and_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'file').write_text('source')
            (root / 'link').symlink_to('../upstream-tooling')
            (root / 'SHA256SUMS').write_text(hashlib.sha256(b'source').hexdigest() + '  file\n' + hashlib.sha256(b'../upstream-tooling').hexdigest() + '  link\n')
            self.assertEqual(verify_inventory(root)['fileCount'], 2)
            (root / 'file').write_text('changed')
            with self.assertRaises(RuntimeError): verify_inventory(root)
            (root / 'file').unlink()
            with self.assertRaises(RuntimeError): verify_inventory(root)
            (root / 'file').write_text('source')
            (root / 'extra').write_text('extra')
            with self.assertRaises(RuntimeError): verify_inventory(root)

    def test_real_retained_source_inventory_and_archives(self):
        inputs = Path(__file__).parent
        for os_name, backend in [('android', 'vulkan'), ('linux', 'vulkan'), ('linux', 'cuda')]:
            record = verify_sources(inputs, os_name, 'amd64', backend, query_packages=False)
            self.assertTrue(record['ubuntu'])
            if os_name == 'android': self.assertGreater(record['android']['fileCount'], 24000)

    def test_unknown_bundled_or_platform_libraries_are_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); (root / 'libggml-base.so').write_bytes(b'ELF fixture')
            with patch('native_sources.subprocess.check_output', return_value='(NEEDED) Shared library: [libc.so]'):
                self.assertEqual(audit_libraries(root, [], 'android', 'vulkan', 'readelf')['libggml-base.so']['platformDependencies'], ['libc.so'])
            with patch('native_sources.subprocess.check_output', return_value='(NEEDED) Shared library: [libunknown.so]'):
                with self.assertRaisesRegex(RuntimeError, 'without a source/system classification'):
                    audit_libraries(root, [], 'android', 'vulkan', 'readelf')
            (root / 'libunknown.so').write_bytes(b'unknown')
            with self.assertRaisesRegex(RuntimeError, 'Unmapped bundled'):
                audit_libraries(root, [], 'android', 'vulkan', 'readelf')

    def test_upstream_arm_cpu_variant_names_keep_their_source_classification(self):
        # Actual upstream GGML_CPU_ALL_VARIANTS outputs from the arm64 CI job.
        names = ['libggml-cpu-armv8.0_1.so', 'libggml-cpu-armv8.2_1.so',
                 'libggml-cpu-armv8.2_2.so', 'libggml-cpu-armv8.2_3.so',
                 'libggml-cpu-armv8.6_1.so', 'libggml-cpu-armv8.6_2.so',
                 'libggml-cpu-armv9.2_1.so', 'libggml-cpu-armv9.2_2.so',
                 'libggml-cpu-android_armv9.2_2.so', 'libggml-base.so.0.15.1', 'libggml-vulkan.so']
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for name in names: (root / name).write_bytes(b'ELF fixture')
            with patch('native_sources.subprocess.check_output', return_value='(NEEDED) Shared library: [libc.so.6]'):
                self.assertEqual(set(audit_libraries(root, [], 'linux', 'vulkan', 'readelf')), set(names))
            (root / 'libunrelated-1.2.so').write_bytes(b'unknown')
            with self.assertRaisesRegex(RuntimeError, 'Unmapped bundled'):
                audit_libraries(root, [], 'linux', 'vulkan', 'readelf')

    def test_cuda_binary_authorization_does_not_claim_full_original_source(self):
        pin = json.loads((Path(__file__).parent / 'native-sources/cuda-13.2/SOURCE.json').read_text())
        cuda = describe_source_closure({'cuda': {'provenance': pin}})
        self.assertEqual(cuda['status'], 'verified-with-nvidia-binary-components')
        self.assertFalse(cuda['nvidiaBinaryComponents']['libdevice']['originalImplementationSourceAvailable'])
        self.assertNotIn('nvidiaBinaryComponents', describe_source_closure({}))

    def test_cuda_binary_input_fingerprint_must_match(self):
        root = Path(__file__).parent / 'native-sources/cuda-13.2'
        pin = json.loads((root / 'SOURCE.json').read_text())
        packages = pin['packages']['amd64']
        expected = {}
        for package in packages.values():
            expected.update({'/' + name: digest for name, digest in package['retainedFiles'].items()})
            expected.update({'/' + name: item['sha256'] for name, item in package.get('binaryInputs', {}).items()})
        with patch('native_sources.verify_inventory', return_value={}), patch('native_sources.subprocess.check_output', side_effect=lambda command, **kwargs: packages[command[-1]]['version']), patch('native_sources.sha256', side_effect=lambda path: expected[str(path)]):
            result = verify_cuda(root, 'amd64')
            self.assertTrue(result['binaryInputs'])
            expected['/usr/local/cuda-13.2/bin/ptxas'] = 'changed'
            with self.assertRaisesRegex(RuntimeError, 'binary input differs'):
                verify_cuda(root, 'amd64')

    def test_installed_source_version_must_match(self):
        with patch('native_sources.subprocess.check_output', return_value='gcc-14\twrong'):
            with self.assertRaisesRegex(RuntimeError, 'does not match retained'):
                verify_ubuntu(Path(__file__).parent / 'native-sources/ubuntu-24.04', 'linux', 'cuda')

    def test_static_runtime_members_need_source_but_unused_archives_do_not(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); build = root / 'build'; binary = root / 'payload'
            (build / 'bin').mkdir(parents=True); binary.mkdir()
            (binary / 'test').write_bytes(b'ELF fixture')
            m = build / 'bin/test.native-link-map'
            m.write_text('LOAD /usr/local/cuda/lib64/libcudart_static.a\n')
            self.assertEqual(audit_static_maps(build, binary, 'linux')['test']['staticMembers'], [])
            m.write_text('/usr/local/cuda/lib64/libcudart_static.a(runtime.o)\n')
            with self.assertRaisesRegex(RuntimeError, 'without corresponding source'):
                audit_static_maps(build, binary, 'linux')
            inputs = {str(Path('/usr/local/cuda/lib64/libcudart_static.a').resolve()): {'kind': 'static-runtime'}}
            self.assertEqual(audit_static_maps(build, binary, 'linux', cuda_inputs=inputs)['test']['staticMembers'][0]['source'], 'nvidia-cuda-13.2-binary')
            m.write_text('/usr/lib/gcc/x86_64-linux-gnu/14/libgcc.a(unwind.o)\n')
            self.assertEqual(audit_static_maps(build, binary, 'linux')['test']['staticMembers'][0]['source'], 'gcc-14')
            m.write_text('LOAD /usr/lib/gcc/x86_64-linux-gnu/15/crtbeginS.o\n')
            with self.assertRaisesRegex(RuntimeError, 'without corresponding source'):
                audit_static_maps(build, binary, 'linux')
            m.unlink()
            with self.assertRaisesRegex(RuntimeError, 'Missing static linkage'):
                audit_static_maps(build, binary, 'linux')


if __name__ == '__main__':
    unittest.main()
