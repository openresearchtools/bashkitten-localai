#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Record the actual static archive members incorporated by each native link."""
from pathlib import Path
import subprocess
import sys


def main(argv):
    command = list(argv)
    if '-o' in command:
        output = Path(command[command.index('-o') + 1])
        # RULE_LAUNCH_LINK also sees archive creation. Only compiler-driver
        # executable/shared-library links support linker maps.
        if not output.name.endswith(('.a', '.o')):
            name = str(output) + '.native-link-map'
            option = '-Xlinker=-Map,' + name if Path(command[0]).name == 'nvcc' else '-Wl,-Map,' + name
            command.append(option)
    return subprocess.call(command)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
