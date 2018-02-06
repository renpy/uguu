from __future__ import print_function
from libc.stdio cimport printf

from sdl2 cimport *


ctypedef unsigned char *(*GetString)(unsigned int)

cdef extern from "GL/gl.h":
    ctypedef unsigned int GLenum
    ctypedef unsigned char GLboolean
    ctypedef unsigned int GLbitfield
    ctypedef void GLvoid
    ctypedef signed char GLbyte
    ctypedef short GLshort
    ctypedef int GLint
    ctypedef int GLclampx
    ctypedef unsigned char GLubyte
    ctypedef unsigned short GLushort
    ctypedef unsigned int GLuint
    ctypedef int GLsizei
    ctypedef float GLfloat
    ctypedef float GLclampf
    ctypedef double GLdouble
    ctypedef double GLclampd
    ctypedef void *GLeglClientBufferEXT
    ctypedef void *GLeglImageOES
    ctypedef char GLchar
    ctypedef char GLcharARB
    ctypedef unsigned short GLhalfARB
    ctypedef unsigned short GLhalf
    ctypedef GLint GLfixed
    ctypedef ptrdiff_t GLintptr
    ctypedef ptrdiff_t GLsizeiptr
    ctypedef int64_t GLint64
    ctypedef uint64_t GLuint64
    ctypedef ptrdiff_t GLintptrARB
    ctypedef ptrdiff_t GLsizeiptrARB
    ctypedef int64_t GLint64EXT
    ctypedef uint64_t GLuint64EXT


    GLubyte *glGetString(GLenum)
    GLenum glGetError()

    enum:
        GL_VERSION


def main():

    cdef SDL_Window *window
    cdef SDL_Event event

    cdef GetString gl_get_string
    cdef unsigned char *buf

    cdef SDL_GLContext glc


    SDL_Init(SDL_INIT_VIDEO)

    # SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_ES)

    window = SDL_CreateWindow("UGUU Test Window", SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED, 400, 400, SDL_WINDOW_OPENGL)

    glc = SDL_GL_CreateContext(window);
    print("ERROR", SDL_GetError())

    get_string = <GetString> SDL_GL_GetProcAddress("glGetString")

    buf = get_string(GL_VERSION)
    print("VERSION", buf)

    while True:

        if SDL_WaitEventTimeout(&event, 200):

            if event.type == SDL_QUIT:
                break






