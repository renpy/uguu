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


BAD_COMMANDS = {
    "glAttachObjectARB",
    "glDetachObjectARB",
}

PXD_HEADER = """\
from libc.stdint cimport int64_t, uint64_t
from libc.stddef cimport ptrdiff_t

"""

PYX_HEADER = """\
from sdl2 cimport SDL_GL_GetProcAddress

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

from libc.stdio cimport printf

cdef void check_error(const char *function) nogil:

    global error_function
    global error_code

    cdef GLenum error

    error = real_glGetError()

    if (error_function == NULL) and (error != GL_NO_ERROR):
        error_function = function
        error_code = error

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
    text = "".join(node.itertext()).strip()
    type_ = text[:-len(name)]

    return type_, name


class Command:

    def __init__(self, node):
        self.return_type = type_and_name(node.find("proto"))[0].strip()

        self.parameters = [ ]
        self.parameter_types = [ ]

        for i in node.findall("param"):
            t, n = type_and_name(i)
            self.parameters.append(n)
            self.parameter_types.append(t)

        self.aliases = set()

    def format_param_list(self):
        l = [ ]

        for name, type_ in zip(self.parameters, self.parameter_types):
            l.append(f"{type_} {name}")

        return "(" + ", ".join(l) + ")"

    def format_proxy_call(self):
        return "(" + ", ".join(self.parameters) + ")"

    def typedef(self, name):
        return "ctypedef {} (*{}){} nogil".format(self.return_type, name, self.format_param_list())


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

        self.types = [ ]

        self.convert_types()

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

        with open("gl.pxd", "w") as f:
            self.generate_pxd(f)

        with open("gl.pyx", "w") as f:
            self.generate_pyx(f)

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

            self.types.append(text)

    def add_command(self, node):
        name = type_and_name(node.find("proto"))[1]

        if name in BAD_COMMANDS:
            return

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

    def generate_pxd(self, f):

        f.write(PXD_HEADER)

        def w(s):
            f.write(s + "\n")

        w('cdef extern from "renpygl.h":')
        w('')

        for l in self.types:
            w(f"    {l}")

        print(file=f)

        enums = list(self.features.enums)
        enums.sort(key=lambda n : int(self.enums[n], 0))

        print(file=f)

        for i in enums:
            w(f"    GLenum {i}")

        for i in sorted(self.features.commands):
            typename = i + "_type"
            c = self.commands[i]

            w("")
            w(c.typedef(typename))
            w(f"cdef {typename} {i}")

    def generate_pyx(self, f):

        f.write(PYX_HEADER)

        def w(s):
            f.write(s + "\n")

        for i in sorted(self.features.commands):
            c = self.commands[i]

            w("")
            w(f"cdef {i}_type real_{i}")
            w(f"cdef {i}_type {i}")

            w("")

            param_list = c.format_param_list()
            proxy_call = c.format_proxy_call()

            if c.return_type != "void":

                w(f'cdef {c.return_type} check_{i}{param_list} nogil:')
                w(f'    cdef {c.return_type} rv')
                w(f'    rv = real_{i}{proxy_call}')
                w(f'    check_error("{i}")')
                w(f'    return rv')

            else:

                w(f'cdef {c.return_type} check_{i}{param_list} nogil:')
                w(f'    real_{i}{proxy_call}')
                w(f'    check_error("{i}")')

        w("")
        w("def load():")

        for i in sorted(self.features.commands):

            names = list(self.commands[i].aliases)
            names.remove(i)
            names.insert(0, i)

            names = [ i.encode("utf-8") for i in names ]

            w(f"")
            w(f"    global real_{i}, {i}")
            w(f"    real_{i} = <{i}_type> find_gl_command({names!r})")
            w(f"    {i} = real_{i}")

        w("")
        w("def enable_check_error():")

        for i in sorted(self.features.commands):
            w(f"    global {i}")
            w(f"    {i} = check_{i}")


if __name__ == "__main__":
    XMLToPYX()
