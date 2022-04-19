import pkg_resources
import swayout.libswayout as libswayout

__version__ = pkg_resources.get_distribution('swayout').version


def main():
    swayout = libswayout.SwayOut()
    swayout.show("outputs")
    swayout.show("presets")
    swayout.prompt()
