from distutils.core import Extension, setup

uguu = Extension(
    "gl",
    ["gl.c" ],
    libs=[ "SDL2", "gl" ],
    include_dirs=[ "/usr/include/SDL2" ],
    )

setup(
    name='uguu',
    ext_modules=[ uguu ],
)
