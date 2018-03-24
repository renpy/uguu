from sdl2 cimport SDL_GL_GetProcAddress
from libc.stdio cimport printf
from cpython.buffer cimport PyObject_GetBuffer, PyBuffer_Release, PyBUF_CONTIG, PyBUF_CONTIG_RO

cdef void *find_gl_command(names):

    cdef void *rv = NULL

    for i in names:
        rv = SDL_GL_GetProcAddress(i)

        if rv != NULL:
            return rv

    raise Exception("{} not found.".format(names[0]))


cdef const char *error_function
cdef GLenum error_code

def reset_error():
    global error_function
    error_function = NULL

    global error_code
    error_code = GL_NO_ERROR

reset_error()

def get_error():

    if error_function != NULL:
        return error_function.decode("utf-8"), error_code
    else:
        return None, GL_NO_ERROR


cdef void check_error(const char *function) nogil:

    global error_function
    global error_code

    cdef GLenum error

    error = real_glGetError()

    if (error_function == NULL) and (error != GL_NO_ERROR):
        error_function = function
        error_code = error

cdef class ptr:
    """
    This is a class that wraps a generic contiguous Python buffer, and
    allows the retrieval of a pointer to that buffer.
    """

    cdef void *ptr
    cdef Py_buffer view

    def __init__(self, o, ro=True):
        PyObject_GetBuffer(o, &self.view, PyBUF_CONTIG_RO if ro else PyBUF_CONTIG)
        self.ptr = self.view.buf

    def __dealloc__(self):
        PyBuffer_Release(&self.view)

cdef ptr get_ptr(o):
    """
    If o is a ptr, return it. Otherwise, convert the buffer into a ptr, and
    return that.
    """

    if isinstance(o, ptr):
        return o
    else:
        return ptr(o)

cdef object proxy_return_string(const GLubyte *s):
    """
    This is used for string return values. It returns the return value as
    a python string if it's not NULL, or None if it's null.
    """

    if s == NULL:
        return None

    cdef const char *ss = <const char *> s
    return ss

