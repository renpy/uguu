from __future__ import print_function
from libc.stdio cimport printf

import argparse

from sdl2 cimport *
from gl cimport *
from gl import load, enable_check_error, get_error, reset_error


def main():

    cdef SDL_Window *window
    cdef SDL_Event event

    cdef unsigned char *buf

    cdef SDL_GLContext glc

    ap = argparse.ArgumentParser()
    ap.add_argument("--egl", action="store_true")
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()


    SDL_Init(SDL_INIT_VIDEO)

    SDL_GL_SetAttribute(SDL_GL_RED_SIZE, 8);
    SDL_GL_SetAttribute(SDL_GL_GREEN_SIZE, 8);
    SDL_GL_SetAttribute(SDL_GL_BLUE_SIZE, 8);
    SDL_GL_SetAttribute(SDL_GL_ALPHA_SIZE, 8);

    if args.egl:
        SDL_SetHint("SDL_OPENGL_ES_DRIVER", "1")
        SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, 2);
        SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_ES)

    window = SDL_CreateWindow("UGUU Test Window", SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED, 400, 400, SDL_WINDOW_OPENGL)

    glc = SDL_GL_CreateContext(window);

    load()

    if args.check:
        enable_check_error()


    print("Start", get_error())

    buf = glGetString(GL_VERSION)
    print("VERSION", buf)

    print("After version", get_error())

    buf = glGetString(GL_TEXTURE_2D)

    print("After bad get.", get_error())

    reset_error()

    print("After reset.", get_error())



    while True:

        if SDL_WaitEventTimeout(&event, 200):

            if event.type == SDL_QUIT:
                break






