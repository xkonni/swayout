from importlib.metadata import version
from swayout import __version__
from swayout import libswayout


def test_version():
    assert __version__ == version('swayout')


def test_libswayout_class():
    libswayout.SwayOut()


def test_libswayout_show():
    swayout = libswayout.SwayOut()
    items = ["help", "outputs", "presets"]
    for item in items:
        try:
            swayout.show(item)
        except Exception as ex:
            raise AssertionError(
                False, f"set_mode('{item}') has raised an exception {type(ex).__name__}")


def test_libswayout_set_mode():
    swayout = libswayout.SwayOut()
    items = [["main", None], ["output", None], ["output", 1], ["preset", None]]
    for item in items:
        try:
            swayout.set_mode(item[0], item[1])
        except Exception as ex:
            raise AssertionError(
                False, f"set_mode('{item}') has raised an exception {type(ex).__name__}")


def test_libswayout_set_output():
    swayout = libswayout.SwayOut()
    items = [[1, "configure"], [1, "disable"], [1, "enable"], [1, "reconfigure"], [1, "show"]]
    for item in items:
        try:
            swayout.set_output(item[0], item[1])
        except Exception as ex:
            raise AssertionError(
                False, f"set_mode('{item}') has raised an exception {type(ex).__name__}")


def test_libswayout_set_preset():
    swayout = libswayout.SwayOut()
    num_presets = len(swayout.config["presets"])
    for item in range(1, num_presets + 1):
        try:
            swayout.set_preset(str(item))
        except Exception as ex:
            raise AssertionError(
                False, f"set_mode('{item}') has raised an exception {type(ex).__name__}")
