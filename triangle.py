import testsupport
import uguu
from uguu import *


VERTEX_SHADER = b"""\
attribute vec4 vPosition;
attribute vec3 vColor;
varying vec3 fColor;
void main() {
    fColor = vColor;
    gl_Position = vPosition;
}
"""

# precision mediump float;


FRAGMENT_SHADER = b"""\
varying vec3 fColor;
void main() {
    gl_FragColor = vec4(fColor.r, fColor.g, fColor.b, 1.0);
}
"""


class ShaderError(Exception):
    pass


def load_shader(shader_type, source):

    shader = glCreateShader(shader_type)

    sourceptr = ptr(strings, source)
    lengthsptr = ptr(int, len(source))

    glShaderSource(shader, 1, sourceptr, lengthsptr)
    glCompileShader(shader)

    status = ptr(int)
    glGetShaderiv(shader, GL_COMPILE_STATUS, status)

    if status.value == GL_FALSE:

        logLength = ptr(int)
        glGetShaderiv(shader, GL_INFO_LOG_LENGTH, logLength)

        log = ptr(byte, count=logLength.value)
        glGetShaderInfoLog(shader, logLength.value, None, log)
        raise ShaderError(log.bytes.decode("utf-8"))


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
    glBindAttribLocation(program, 1, b"vColor")

    glLinkProgram(program)

    status = ptr(int)
    glGetProgramiv(program, GL_LINK_STATUS, status)
    print("Status:", status.value)

    glClearColor(0.0, 0.0, 0.0, 1.0)

    print(uguu.get_error())

    first = True

    while sdl.loop():

        glViewport(0, 0, 400, 400)
        glClear(GL_COLOR_BUFFER_BIT)

        glUseProgram(program)

        vertices = [ 0.0, 0.9, 0.0,
                     -0.9, -0.9, 0.0,
                     0.9, -0.9, 0.0, ]

        colors = [ 1.0, 0.0, 0.0,
                   0.0, 1.0, 0.0,
                   0.0, 0.0, 1.0, ]

        verticesptr = ptr(float, vertices)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, verticesptr)
        glEnableVertexAttribArray(0)

        colorsptr = ptr(float, colors)

        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, colorsptr)
        glEnableVertexAttribArray(1)

        glDrawArrays(GL_TRIANGLES, 0, 3)

        if first:
            print(uguu.get_error())

        first = False

        pass


if __name__ == "__main__":
    main()
