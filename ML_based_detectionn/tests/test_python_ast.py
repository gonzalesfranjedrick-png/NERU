import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import analyze_python_ast


def test_simple_exec():
    code = """
x = 1
exec('print(1)')
"""
    res = analyze_python_ast(code)
    assert 'exec' in res


def test_import_ctypes():
    code = "import ctypes\nctypes.CDLL('lib')"
    res = analyze_python_ast(code)
    assert any(r.startswith('import:') for r in res)


def test_subprocess_call():
    code = "from subprocess import Popen\nPopen(['ls'])"
    res = analyze_python_ast(code)
    assert any(r.startswith('from:') or 'subprocess' in r for r in res)
