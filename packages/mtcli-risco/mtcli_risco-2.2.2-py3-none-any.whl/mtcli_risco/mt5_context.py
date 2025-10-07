from contextlib import contextmanager
from mtcli.conecta import conectar, shutdown


@contextmanager
def mt5_conexao():
    conectar()
    try:
        yield
    finally:
        shutdown()
