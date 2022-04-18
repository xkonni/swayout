import pytest
import sys
import pkg_resources
from swayout import __version__
from swayout import *

def test_version():
    assert __version__ == pkg_resources.get_distribution('swayout').version

def test_libswayout_class():
    swayout = libswayout.SwayOut()

def test_libswayout_show():
    swayout = libswayout.SwayOut()
    items = [ "help", "outputs", "presets" ]
    for item in items:
        try:
            swayout.show(item)
        except Exception as ex:
            assert False, f"show('{item}') has raised an exception {type(ex).__name__}"

def test_libswayout_set_mode():
    swayout = libswayout.SwayOut()
    items = [ ["main", None], ["output", None], ["output", 1], ["preset", None] ]
    for item in items:
        try:
            swayout.set_mode(item[0], item[1]) 
        except Exception as ex:
            assert False, f"set_mode('{item}') has raised an exception {type(ex).__name__}"

def test_libswayout_set_output():
    swayout = libswayout.SwayOut()
    items = [[1, "configure"], [1, "disable"], [1, "enable"], [1, "reconfigure"], [1, "show"]]
    for item in items:
        try:
            swayout.set_output(item[0], item[1]) 
        except Exception as ex:
            assert False, f"set_output('{item}') has raised an exception {type(ex).__name__}"

def test_libswayout_set_preset():
    swayout = libswayout.SwayOut()
    num_presets = len(swayout.config["presets"])
    for item in range(1, num_presets+1):
        try:
            swayout.set_preset(str(item))
        except Exception as ex:
            assert False, f"set_output('{item}') has raised an exception {type(ex).__name__}"
