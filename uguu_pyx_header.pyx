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


cdef class Buffer:
    """
    The base class for all buffers.
    """

    cdef Py_ssize_t length
    cdef Py_ssize_t itemsize
    cdef const char *format
    cdef void *data
    cdef int readonly

    cdef setup_buffer(self, Py_ssize_t length, Py_ssize_t itemsize, const char *format, int readonly):
        """
        This is called by a specific buffer's init method to set up various fields, and especially
        allocate the data field.

        `length`
            The number of items in this buffer.
        `itemsize`
            The size of a single item.
        `format`
            The struct-style format code.
        `readonly`
            1 if readonly, 0 if read-write.
        """

        self.length = length
        self.itemsize = itemsize
        self.format = format
        self.readonly = readonly
        self.data = calloc(self.length, self.itemsize)

    def __getbuffer__(self, Py_buffer *buffer, int flags):

        buffer.buf = self.data
        buffer.format = self.format
        buffer.internal = NULL
        buffer.itemsize = self.itemsize
        buffer.len = self.length * self.itemsize
        buffer.ndim = 1
        buffer.obj = self
        buffer.readonly = self.readonly
        buffer.shape = &self.length
        buffer.strides = &self.itemsize
        buffer.suboffsets = NULL

    def __releasebuffer__(self, Py_buffer *buffer):
        pass

    def __dealloc__(self):
        if self.data:
            free(self.data)
            self.data = NULL

    def bytes(self):
        raise TypeError("{} does not support .bytes.".format(self.__class__.__name__))


cdef class BytesBuffer(Buffer):

    def __init__(self, value):

        self.setup_buffer(len(value), 1, "B", 0)

        cdef int i

        for 0 <= i < self.length:
            (<char *> self.data)[i] = <char> value[i]

    def bytes(self):
        return (<char *> self.data)[0:self.length]

    def __getitem__(self, index):
        if index < 0 or index >= self.length:
            raise IndexError("index out of range")

        return (<char *> self.data)[index]


cdef class BytesListBuffer(Buffer):
    cdef object pyvalue
    cdef object ptrs

    def __init__(self, value):
        self.pyvalue = value
        self.ptrs = [ ptr(v) for v in value ]
        self.setup_buffer(len(value), sizeof(const char *), "P", 1)

        cdef int i

        for 0 <= i < self.length:
            (<const char **> self.data)[i] = <const char *> (<ptr> self.ptrs[i]).ptr

    def __getitem__(self, index):
        return self.value[index]

cdef class IntBuffer(Buffer):

    def __init__(self, value):

        self.setup_buffer(len(value), sizeof(int), "i", 0)

        cdef int i

        for 0 <= i < self.length:
            (<int *> self.data)[i] = <int> value[i]

    def __getitem__(self, index):
        if index < 0 or index >= self.length:
            raise IndexError("index out of range")

        return (<int *> self.data)[index]

cdef class FloatBuffer(Buffer):

    def __init__(self, value):

        self.setup_buffer(len(value), sizeof(float), "f", 0)

        cdef int i

        for 0 <= i < self.length:
            (<float *> self.data)[i] = <float> value[i]

    def __getitem__(self, index):
        if index < 0 or index >= self.length:
            raise IndexError("index out of range")

        return (<float *> self.data)[index]

# Types for pointers.
byte = object()
strings = object()


# A map from the type to the buffer.
TYPE_BUFFERS = {
    byte : BytesBuffer,
    float : FloatBuffer,
    int : IntBuffer,
    strings : BytesListBuffer,
}



# Note: We need to do a bit of indirection here, so that the object doesn't
# have a pointer to itself that would cause the GC to run. That's why we have
# the ptr as one object and the Buffer as a second object.


cdef class ptr:
    """
    This returns an object that serves as a pointer a Python buffer.

    `kind`
        If None, makes a NULL pointer. Otherwise, the type of the
        buffer to create.

    `value`
        The default value of the contents of the buffer. If this is
        a list, it's used directly. Otherwise, it's put into a list
        of `count` items and used to create the buffer.

    """

    cdef object buffer
    cdef void *ptr
    cdef Py_buffer view

    def __init__(self, kind, value=0, count=1):

        if kind is None:
            self.buffer = None
            self.ptr = NULL
            return

        buffer_type = TYPE_BUFFERS.get(kind, None)

        if buffer_type:

            if isinstance(value, ptr):
                raise Exception("The second argument to ptr can't be a ptr.")

            if not isinstance(value, list):
                value = [ value ] * count

            self.buffer = buffer_type(value)
            ro = False

        else:
            self.buffer = kind
            ro = True

        if PyObject_GetBuffer(self.buffer, &self.view, PyBUF_CONTIG_RO if ro else PyBUF_CONTIG) == 0:
            self.ptr = self.view.buf

    def __dealloc__(self):
        if self.ptr:
            PyBuffer_Release(&self.view)
            self.ptr = NULL

    def __getitem__(self, index):
        return self.buffer[index]

    @property
    def value(self):
        return self.buffer[0]

    @property
    def bytes(self):
        return self.buffer.bytes()


cdef ptr get_ptr(o):
    """
    If o is a ptr, return it. Otherwise, convert the buffer into a ptr, and
    return that.
    """

    if isinstance(o, ptr):
        return o
    else:
        return ptr(o)
