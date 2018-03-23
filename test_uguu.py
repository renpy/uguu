import gl
import testsupport
import pytest

sdl = testsupport.SDL()
sdl.init()


@pytest.fixture(scope="function", params=[False, True])
def context(request):
    sdl.open_window(request.param)

    if request.param:
        yield "gles"
    else:
        yield "gl"

    sdl.close_window()


NO_ERROR = (None, 0)


def test_no_checking(context):

    gl.load()
    gl.reset_error()

    assert gl.get_error() == NO_ERROR

    version = gl.glGetString(gl.GL_VERSION)

    assert version

    if context == "gles":
        assert b"OpenGL ES" in version
    else:
        assert b"OpenGL ES" not in version

    assert gl.get_error() == NO_ERROR

    gl.glGetString(gl.GL_TEXTURE_2D)

    assert gl.get_error() == NO_ERROR


def test_checking(context):

    gl.load()
    gl.enable_check_error()
    gl.reset_error()

    assert gl.get_error() == NO_ERROR

    version = gl.glGetString(gl.GL_VERSION)

    assert version

    if context == "gles":
        assert b"OpenGL ES" in version
    else:
        assert b"OpenGL ES" not in version

    assert gl.get_error() == NO_ERROR

    gl.glGetString(gl.GL_TEXTURE_2D)

    assert gl.get_error() ==  ('glGetString', 1280)

    gl.reset_error()

    assert gl.get_error() == NO_ERROR
