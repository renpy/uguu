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

NOGIL_COMMANDS = {
    "glClear",
}

HEADER = """\
from libc.stdint cimport int64_t, uint64_t
from libc.stddef cimport ptrdiff_t

"""


def type_and_name(node):
    name = node.findtext("name")
    text = "".join(node.itertext())
    type_ = text.replace(name, "")

    return type_, name


class Command:

    def __init__(self, node):
        self.return_type = type_and_name(node.find("proto"))[0]

        self.parameters = [ ]
        self.parameter_types = [ ]

        for i in node.findall("param"):
            t, n = type_and_name(i)
            self.parameters.append(n)
            self.parameter_types.append(t)

        self.aliases = set()


class XMLToPYX:

    def __init__(self):
        self.root = parse("gl.xml").getroot()

        self.externs = [ ]

        self.convert_types()

        print(HEADER)

        self.generate_externs()

        # A map from command name to command.
        self.commands = { }

        self.find_commands()

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

    def add_command(self, node):
        name = type_and_name(node.find("proto"))[1]

        names = [ name ]

        for i in node.findall("alias"):
            names.append(i.attrib["name"])

        for i in names:
            c = self.commands.get(i, None)
            if c is not None:
                break
        else:
            c = Command(node)

        for i in names:
            c.aliases.add(i)
            self.commands[i] = c

    def find_commands(self):
        commands = self.root.find("commands")

        for c in commands.findall("command"):
            self.add_command(c)

        print(self.commands)


if __name__ == "__main__":
    XMLToPYX()
