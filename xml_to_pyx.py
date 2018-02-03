from xml.etree.ElementTree import parse, tostring
import collections
import itertools

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

GL_FEATURES = [
    "GL_VERSION_1_0",
    "GL_VERSION_1_1",
    "GL_VERSION_1_2",
    "GL_VERSION_1_3",
    "GL_VERSION_1_4",
    "GL_VERSION_1_5",
    "GL_VERSION_2_0",
    "GL_VERSION_2_1",
    "GL_VERSION_3_0",
    ]

GLES_FEATURES = [
    "GL_ES_VERSION_2_0",
    ]


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


class Feature:

    def __init__(self):
        self.commands = set()
        self.enums = set()

    def from_node(self, node):

        for i in node.findall("require/enum"):
            self.enums.add(i.attrib["name"])

        for i in node.findall("require/command"):
            self.commands.add(i.attrib["name"])

    def __or__(self, other):
        rv = Feature()
        rv.commands = self.commands | other.commands
        rv.enums = self.enums | other.enums
        return rv

    def __and__(self, other):
        rv = Feature()
        rv.commands = self.commands & other.commands
        rv.enums = self.enums & other.enums
        return rv


class XMLToPYX:

    def __init__(self):
        self.root = parse("gl.xml").getroot()

        self.externs = [ ]

        self.convert_types()

        print(HEADER)

        # A map from command name to command.
        self.commands = { }

        self.find_commands()

        # A map from enum name to value.
        self.enums = collections.OrderedDict()

        self.find_enums()

        # A map from feature name to value.
        self.features = { }

        self.find_features()
        self.select_features()

        self.generate_externs()
        self.generate_enums()

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

    def find_enums(self):

        for enums in self.root.findall("enums"):
            for i in enums.findall("enum"):
                value = i.attrib["value"]
                name = i.attrib["name"]

                self.enums[name] = value

                alias = i.attrib.get("alias", None)

                if alias is not None:
                    self.enums[alias] = value

    def find_features(self):

        for i in itertools.chain(
                self.root.findall("feature"),
                self.root.findall("extensions/extension")
                ):

            name = i.attrib["name"]

            f = Feature()
            f.from_node(i)
            self.features[name] = f

            # print(name)

    def select_features(self):

        gl = Feature()

        for i in GL_FEATURES:
            gl = gl | self.features[i]

        gles = Feature()

        for i in GLES_FEATURES:
            gles = gles | self.features[i]

        f = gl & gles

        self.features = f

    def generate_enums(self):

        enums = list(self.features.enums)
        enums.sort(key=lambda n : int(self.enums[n], 0))

        print()

        for i in enums:

            print("cdef public GLenum {} = {}".format(i, self.enums[i]))


if __name__ == "__main__":
    XMLToPYX()
