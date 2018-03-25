from distutils.core import Extension, setup

uguu = Extension(
    "uguu",
    ["gen/uguu.c" ],
    libraries=[ "SDL2", ],
    include_dirs=[ "/usr/include/SDL2" ],
    )

uguugl = Extension(
    "uguugl",
    ["gen/uguugl.c" ],
    libraries=[ "SDL2", ],
    include_dirs=[ "/usr/include/SDL2" ],
    )

testsupport = Extension(
    "testsupport",
    [ "gen/testsupport.c" ],
    libraries=[ "SDL2", ],
    include_dirs=[ "/usr/include/SDL2" ],
    )

setup(
    name='uguu',
    ext_modules=[ uguu, uguugl, testsupport ],
)
