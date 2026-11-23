from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from functools import reduce
from typing import Iterable, Tuple

from sistema_biblioteca.emprestimo import Emprestimo
from sistema_biblioteca.funcional import MULTA_DIARIA, VALOR_ZERO, calcular_multa


@dataclass(frozen=True)
class ItemMulta:
    emprestimo_id: int
    titulo_livro: str
    nome_usuario: str
    dias_de_atraso: int
    valor: Decimal


@dataclass(frozen=True)
class RelatorioMultas:
    data_referencia: date
    itens: Tuple[ItemMulta, ...]
    total: Decimal


def criar_item_multa(emprestimo: Emprestimo, data_referencia: date) -> ItemMulta:
    dias_de_atraso = emprestimo.dias_de_atraso(data_referencia)
    return ItemMulta(
        emprestimo_id=emprestimo.identificador,
        titulo_livro=emprestimo.livro.titulo,
        nome_usuario=emprestimo.usuario.nome,
        dias_de_atraso=dias_de_atraso,
        valor=calcular_multa(dias_de_atraso, MULTA_DIARIA),
    )


def gerar_relatorio_multas(
    emprestimos: Iterable[Emprestimo], data_referencia: date
) -> RelatorioMultas:
    atrasados = filter(lambda emprestimo: emprestimo.esta_atrasado(data_referencia), emprestimos)
    itens = tuple(map(lambda emprestimo: criar_item_multa(emprestimo, data_referencia), atrasados))
    total = reduce(lambda soma, item: soma + item.valor, itens, VALOR_ZERO)
    return RelatorioMultas(data_referencia=data_referencia, itens=itens, total=total)
