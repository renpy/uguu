from distutils.core import Extension, setup

uguu = Extension(
    "gl",
    ["gl.c" ],
    libraries=[ "SDL2", ],
    include_dirs=[ "/usr/include/SDL2" ],
    )

testsupport = Extension(
    "testsupport",
    [ "testsupport.c" ],
    libraries=[ "SDL2" ],
    include_dirs=[ "/usr/include/SDL2" ],
    )

setup(
    name='uguu',
    ext_modules=[ uguu, testsupport ],
)
