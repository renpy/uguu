from xml.etree.ElementTree import parse, tostring

# Bad/weird types we don't need or want to generate.
BAD_TYPES = {
    "GLVULKANPROCNV",
    "GLvdpauSurfaceNV",
    "GLhalfNV",
    "struct _cl_event",
    "struct _cl_context",
    "GLDEBUGPROCAMD",
    "GLDEBUGPROCKHR",
    "GLDEBUGPROCARB",
    "GLDEBUGPROC",
    "GLsync",
}

HEADER = """\
from libc.stdint cimport int64_t, uint64_t
from libc.stddef cimport ptrdiff_t

"""


class XMLToPYX:

    def __init__(self):
        self.root = parse("gl.xml").getroot()

        self.externs = [ ]

        self.convert_types()

        print(HEADER)

        self.generate_externs()

    def extern(self, l):
        self.externs.append(l)

    def generate_externs(self):
        print('cdef extern from "renpygl.h":')

        for l in self.externs:
            print("    " + l)

    def convert_types(self):
        types = self.root.find('types')

        for t in types:
            if t.get("api", ""):
                continue

            name = t.find("name")
            if name is None:
                continue

            name = name.text
            if name in BAD_TYPES:
                continue

            text  = "".join(t.itertext())

            text = text.replace(";", "")
            text = text.replace("typedef", "ctypedef")

            self.extern(text)


if __name__ == "__main__":
    XMLToPYX()
