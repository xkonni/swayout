from swayout import __version__
import pkg_resources

def test_true():
    assert True

def test_version():
    assert __version__ == pkg_resources.get_distribution('swayout').version

