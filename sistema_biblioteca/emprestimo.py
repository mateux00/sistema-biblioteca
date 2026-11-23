from dataclasses import dataclass, replace
from datetime import date
from typing import Optional

from sistema_biblioteca.excecoes import DadosInvalidosError, EmprestimoJaDevolvidoError
from sistema_biblioteca.livro import Livro
from sistema_biblioteca.usuario import Usuario
from sistema_biblioteca.validacao import validar_identificador


@dataclass(frozen=True)
class Emprestimo:
    identificador: int
    livro: Livro
    usuario: Usuario
    data_emprestimo: date
    data_prevista_devolucao: date
    data_devolucao: Optional[date] = None

    def __post_init__(self) -> None:
        validar_identificador(self.identificador, "identificador do empréstimo")
        if self.data_prevista_devolucao < self.data_emprestimo:
            raise DadosInvalidosError(
                "A data prevista de devolução não pode ser anterior à data do empréstimo."
            )
        if self.data_devolucao is not None and self.data_devolucao < self.data_emprestimo:
            raise DadosInvalidosError(
                "A data de devolução não pode ser anterior à data do empréstimo."
            )

    @property
    def ativo(self) -> bool:
        return self.data_devolucao is None

    def dias_de_atraso(self, data_referencia: date) -> int:
        if not self.ativo:
            return 0
        return max((data_referencia - self.data_prevista_devolucao).days, 0)

    def esta_atrasado(self, data_referencia: date) -> bool:
        return self.dias_de_atraso(data_referencia) > 0

    def com_devolucao(self, data_devolucao: date) -> "Emprestimo":
        if not self.ativo:
            raise EmprestimoJaDevolvidoError(
                f"O empréstimo {self.identificador} já foi devolvido."
            )
        return replace(self, data_devolucao=data_devolucao)
