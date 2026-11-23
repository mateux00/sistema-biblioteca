from datetime import date
from typing import Optional

from sistema_biblioteca.emprestimo import Emprestimo
from sistema_biblioteca.livro import Livro
from sistema_biblioteca.usuario import Usuario


def criar_livro(identificador: int = 1, categoria: str = "Literatura") -> Livro:
    return Livro(identificador, f"Livro {identificador}", "Autor", categoria)


def criar_usuario(identificador: int = 1) -> Usuario:
    return Usuario(identificador, f"Usuário {identificador}", f"MAT{identificador:03d}")


def criar_emprestimo(
    identificador: int = 1,
    data_prevista: date = date(2026, 11, 10),
    data_devolucao: Optional[date] = None,
    livro: Optional[Livro] = None,
    usuario: Optional[Usuario] = None,
) -> Emprestimo:
    return Emprestimo(
        identificador=identificador,
        livro=livro or criar_livro(identificador),
        usuario=usuario or criar_usuario(),
        data_emprestimo=date(2026, 11, 1),
        data_prevista_devolucao=data_prevista,
        data_devolucao=data_devolucao,
    )
