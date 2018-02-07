#!/bin/bash

set -e

python3 xml_to_pyx.py
cython gl.pyx
cython testsupport.pyx

python3 setup.py build_ext -i -q


# python3 test.py "$@"

