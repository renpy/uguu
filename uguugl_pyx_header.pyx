from sdl2 cimport SDL_GL_GetProcAddress
from libc.stdio cimport printf
from libc.stdlib cimport calloc, free
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
    """
    Resets the
    """

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

cdef object proxy_return_string(const GLubyte *s):
    """
    This is used for string return values. It returns the return value as
    a python string if it's not NULL, or None if it's null.
    """

    if s == NULL:
        return None

    cdef const char *ss = <const char *> s
    return ss


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

cdef class BytesListBuffer:

    cdef object value
    cdef Py_ssize_t length
    cdef Py_ssize_t itemsize
    cdef const char *format
    cdef const char **data

    def __init__(self, value):
        self.value = [ ptr(v) for v in value ]
        self.length = len(value)
        self.itemsize = sizeof(const char *)
        self.format = "P"
        self.data = <const char **> calloc(self.length, self.itemsize)

        cdef int i

        for 0 <= i < self.length:
            self.data[i] = <const char *> (<ptr> value[i]).ptr

    def __getbuffer__(self, Py_buffer *buffer, int flags):

        buffer.buf = &self.data[0]
        buffer.format = self.format
        buffer.internal = NULL
        buffer.itemsize = self.itemsize
        buffer.len = self.length * self.itemsize
        buffer.ndim = 1
        buffer.obj = self
        buffer.readonly = 1
        buffer.shape = &self.length
        buffer.strides = &self.itemsize
        buffer.suboffsets = NULL

    def __releasebuffer__(self, Py_buffer *buffer):
        pass
