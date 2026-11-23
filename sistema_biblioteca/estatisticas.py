from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from functools import reduce
from types import MappingProxyType
from typing import Dict, Hashable, Iterable, Mapping, TypeVar

from sistema_biblioteca.emprestimo import Emprestimo
from sistema_biblioteca.funcional import filtrar_emprestimos_ativos, filtrar_emprestimos_atrasados
from sistema_biblioteca.livro import Livro
from sistema_biblioteca.relatorios import gerar_relatorio_multas
from sistema_biblioteca.usuario import Usuario

Chave = TypeVar("Chave", bound=Hashable)


@dataclass(frozen=True)
class Estatisticas:
    data_referencia: date
    livros_por_categoria: Mapping[str, int]
    emprestimos_por_usuario: Mapping[Usuario, int]
    emprestimos_ativos: int
    emprestimos_atrasados: int
    total_multas: Decimal


def incrementar_contagem(contagem: Mapping[Chave, int], chave: Chave) -> Dict[Chave, int]:
    return {**contagem, chave: contagem.get(chave, 0) + 1}


def contar_livros_por_categoria(livros: Iterable[Livro]) -> Mapping[str, int]:
    contagem = reduce(
        lambda acumulado, livro: incrementar_contagem(acumulado, livro.categoria),
        livros,
        {},
    )
    return MappingProxyType(contagem)


def contar_emprestimos_por_usuario(
    usuarios: Iterable[Usuario], emprestimos: Iterable[Emprestimo]
) -> Mapping[Usuario, int]:
    contagem = reduce(
        lambda acumulado, emprestimo: incrementar_contagem(acumulado, emprestimo.usuario),
        emprestimos,
        dict.fromkeys(usuarios, 0),
    )
    return MappingProxyType(contagem)


def contar_emprestimos_ativos(emprestimos: Iterable[Emprestimo]) -> int:
    return len(filtrar_emprestimos_ativos(emprestimos))


def contar_emprestimos_atrasados(emprestimos: Iterable[Emprestimo], data_referencia: date) -> int:
    return len(filtrar_emprestimos_atrasados(emprestimos, data_referencia))


def gerar_estatisticas(
    livros: Iterable[Livro],
    usuarios: Iterable[Usuario],
    emprestimos: Iterable[Emprestimo],
    data_referencia: date,
) -> Estatisticas:
    emprestimos_registrados = tuple(emprestimos)
    return Estatisticas(
        data_referencia=data_referencia,
        livros_por_categoria=contar_livros_por_categoria(livros),
        emprestimos_por_usuario=contar_emprestimos_por_usuario(usuarios, emprestimos_registrados),
        emprestimos_ativos=contar_emprestimos_ativos(emprestimos_registrados),
        emprestimos_atrasados=contar_emprestimos_atrasados(emprestimos_registrados, data_referencia),
        total_multas=gerar_relatorio_multas(emprestimos_registrados, data_referencia).total,
    )
