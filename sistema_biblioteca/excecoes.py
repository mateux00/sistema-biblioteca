class BibliotecaError(Exception):
    pass


class DadosInvalidosError(BibliotecaError, ValueError):
    pass


class LivroNaoEncontradoError(BibliotecaError, LookupError):
    pass


class UsuarioNaoEncontradoError(BibliotecaError, LookupError):
    pass


class EmprestimoNaoEncontradoError(BibliotecaError, LookupError):
    pass


class MatriculaDuplicadaError(BibliotecaError):
    pass


class LivroIndisponivelError(BibliotecaError):
    pass


class EmprestimoJaDevolvidoError(BibliotecaError):
    pass
