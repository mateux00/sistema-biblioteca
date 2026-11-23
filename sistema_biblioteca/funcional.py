from datetime import date, timedelta
from decimal import Decimal
from typing import FrozenSet, Iterable, Mapping, Tuple

from sistema_biblioteca.emprestimo import Emprestimo
from sistema_biblioteca.excecoes import DadosInvalidosError
from sistema_biblioteca.livro import Livro
from sistema_biblioteca.usuario import Usuario

MULTA_DIARIA = Decimal("2.00")
VALOR_ZERO = Decimal("0.00")
CENTAVOS = Decimal("0.01")


def calcular_multa(dias_de_atraso: int, valor_diario: Decimal) -> Decimal:
    dias_cobrados = max(dias_de_atraso, 0)
    return (valor_diario * dias_cobrados).quantize(CENTAVOS)


def calcular_data_prevista(data_emprestimo: date, prazo_em_dias: int) -> date:
    if prazo_em_dias <= 0:
        raise DadosInvalidosError("O prazo do empréstimo deve ser de pelo menos um dia.")
    return data_emprestimo + timedelta(days=prazo_em_dias)


def proximo_identificador(registros: Mapping[int, object]) -> int:
    return max(registros, default=0) + 1


def filtrar_livros_por_categoria(livros: Iterable[Livro], categoria: str) -> Tuple[Livro, ...]:
    return tuple(filter(lambda livro: livro.pertence_a_categoria(categoria), livros))


def filtrar_emprestimos_ativos(emprestimos: Iterable[Emprestimo]) -> Tuple[Emprestimo, ...]:
    return tuple(filter(lambda emprestimo: emprestimo.ativo, emprestimos))


def filtrar_emprestimos_atrasados(
    emprestimos: Iterable[Emprestimo], data_referencia: date
) -> Tuple[Emprestimo, ...]:
    return tuple(filter(lambda emprestimo: emprestimo.esta_atrasado(data_referencia), emprestimos))


def filtrar_emprestimos_do_usuario(
    emprestimos: Iterable[Emprestimo], usuario: Usuario
) -> Tuple[Emprestimo, ...]:
    return tuple(
        filter(
            lambda emprestimo: emprestimo.usuario.identificador == usuario.identificador,
            emprestimos,
        )
    )


def identificadores_de_livros_emprestados(emprestimos: Iterable[Emprestimo]) -> FrozenSet[int]:
    return frozenset(
        map(lambda emprestimo: emprestimo.livro.identificador, filtrar_emprestimos_ativos(emprestimos))
    )


def livro_esta_disponivel(livro: Livro, emprestimos: Iterable[Emprestimo]) -> bool:
    return livro.identificador not in identificadores_de_livros_emprestados(emprestimos)


def filtrar_livros_disponiveis(
    livros: Iterable[Livro], emprestimos: Iterable[Emprestimo]
) -> Tuple[Livro, ...]:
    emprestados = identificadores_de_livros_emprestados(emprestimos)
    return tuple(filter(lambda livro: livro.identificador not in emprestados, livros))
