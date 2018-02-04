from __future__ import print_function

from sdl2 cimport *

def init():
    print(SDL_Init(SDL_INIT_VIDEO))

