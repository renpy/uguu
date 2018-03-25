from libc.stddef cimport ptrdiff_t
from libc.stdint cimport int64_t, uint64_t
from libc.stdio cimport printf
from libc.stdlib cimport calloc, free

from cpython.buffer cimport PyObject_GetBuffer, PyBuffer_Release, PyBUF_CONTIG, PyBUF_CONTIG_RO

cimport uguugl
from uguugl import reset_error, get_error, enable_check_error, load

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
