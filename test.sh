#!/bin/bash

set -e

python3 xml_to_pyx.py
cp testsupport.pyx gen
cp sdl2.pxd gen
cp renpygl.h gen

pushd gen
cython uguugl.pyx
cython testsupport.pyx
popd

export CC="ccache gcc"
export LD="ccache ld"

python3 setup.py build_ext -q

PYTHONVERSION=$(python3 -c 'import sysconfig; print(sysconfig.get_platform() + "-" + sysconfig.get_python_version())')
export PYTHONPATH="build/lib.$PYTHONVERSION"

python3 "$@"

