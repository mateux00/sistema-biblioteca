from datetime import date
from decimal import Decimal
from functools import reduce
from typing import Iterable

from sistema_biblioteca.emprestimo import Emprestimo
from sistema_biblioteca.funcional import MULTA_DIARIA, VALOR_ZERO, calcular_multa


def calcular_total_multas_imperativo(
    emprestimos: Iterable[Emprestimo], data_referencia: date
) -> Decimal:
    total = VALOR_ZERO
    for emprestimo in emprestimos:
        nao_devolvido = emprestimo.data_devolucao is None
        if nao_devolvido and data_referencia > emprestimo.data_prevista_devolucao:
            dias_de_atraso = (data_referencia - emprestimo.data_prevista_devolucao).days
            total += MULTA_DIARIA * dias_de_atraso
    return total


def calcular_total_multas_funcional(
    emprestimos: Iterable[Emprestimo], data_referencia: date
) -> Decimal:
    atrasados = filter(lambda emprestimo: emprestimo.esta_atrasado(data_referencia), emprestimos)
    multas = map(
        lambda emprestimo: calcular_multa(emprestimo.dias_de_atraso(data_referencia), MULTA_DIARIA),
        atrasados,
    )
    return reduce(lambda total, multa: total + multa, multas, VALOR_ZERO)
