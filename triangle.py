import testsupport
import uguu
from uguu import *


VERTEX_SHADER = b"""\
attribute vec4 vPosition;
void main() {
    gl_Position = vPosition;
}
"""

FRAGMENT_SHADER = b"""\
precision mediump float;
void main() {
    gl_FragColor = vec4(1.0, 0.0, 0.0, 1.0);
}
"""


class ShaderError(Exception):
    pass


def load_shader(shader_type, source):

    shader = glCreateShader(shader_type)

    sourceptr = ptr(BytesListBuffer([ source ]))
    lengthsptr = ptr(IntBuffer([ len(source) ]))

    glShaderSource(shader, 1, sourceptr, lengthsptr)
    glCompileShader(shader)

    status = IntBuffer([ 0 ])
    glGetShaderiv(shader, GL_COMPILE_STATUS, status)

    if status[0] == GL_FALSE:

        logLength = IntBuffer([ 0 ])
        glGetShaderiv(shader, GL_INFO_LOG_LENGTH, logLength)

        log = BytesBuffer(logLength[0])
        glGetShaderInfoLog(shader, logLength[0], None, log)

        raise ShaderError(log.get().decode("utf-8"))

    return shader


def main():

    sdl = testsupport.SDL()
    sdl.init()

    # Open a 400x400 window and GL context.
    sdl.open_window(False)

    uguu.load()
    uguu.enable_check_error()

    vertex = load_shader(GL_VERTEX_SHADER, VERTEX_SHADER)
    fragment = load_shader(GL_FRAGMENT_SHADER, FRAGMENT_SHADER)

    program = glCreateProgram()

    glAttachShader(program, vertex)
    glAttachShader(program, fragment)

    glBindAttribLocation(program, 0, b"vPosition")

    glLinkProgram(program)

    status = IntBuffer([ 0 ])
    glGetProgramiv(program, GL_LINK_STATUS, status)
    print("Status:", status[0])

    glClearColor(0.0, 0.0, 0.0, 1.0)

    print(uguu.get_error())

    first = True

    while sdl.loop():

        glViewport(0, 0, 400, 400)
        glClear(GL_COLOR_BUFFER_BIT)

        glUseProgram(program)

        vertices = [ 0.0, 0.5, 0.0,
                     -0.5, -0.5, 0.0,
                     0.5, -0.5, 0.0, ]

        verticesptr = ptr(FloatBuffer(vertices))

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, verticesptr)
        glEnableVertexAttribArray(0)

        glDrawArrays(GL_TRIANGLES, 0, 3)

        if first:
            print(uguu.get_error())

        first = False

        pass


if __name__ == "__main__":
    main()
