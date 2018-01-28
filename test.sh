#!/bin/bash

set -e
python3 xml_to_pyx.py > gl.pyx
cython gl.pyx
