import importlib

def test_package_exports_version():
    pkg = importlib.import_module("topolib")
    assert hasattr(pkg, "__version__"), "topolib should expose __version__"
    assert isinstance(pkg.__version__, str), "__version__ should be a string"
