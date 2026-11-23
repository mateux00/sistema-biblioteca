import unittest
from datetime import date
from decimal import Decimal

from sistema_biblioteca.formatacao import (
    descrever_situacao,
    formatar_data,
    formatar_moeda,
    formatar_relatorio_multas,
)
from sistema_biblioteca.relatorios import RelatorioMultas
from tests.fabrica import criar_emprestimo


class FormatacaoTest(unittest.TestCase):
    def test_formata_moeda_no_padrao_brasileiro(self):
        self.assertEqual(formatar_moeda(Decimal("2")), "R$ 2,00")
        self.assertEqual(formatar_moeda(Decimal("1234.5")), "R$ 1.234,50")

    def test_formata_data_no_padrao_brasileiro(self):
        self.assertEqual(formatar_data(date(2026, 11, 3)), "03/11/2026")

    def test_descreve_a_situacao_do_emprestimo(self):
        emprestimo = criar_emprestimo(data_prevista=date(2026, 11, 10))

        self.assertEqual(descrever_situacao(emprestimo, date(2026, 11, 5)), "ativo, dentro do prazo")
        self.assertEqual(descrever_situacao(emprestimo, date(2026, 11, 12)), "atrasado há 2 dia(s)")
        self.assertEqual(
            descrever_situacao(emprestimo.com_devolucao(date(2026, 11, 9)), date(2026, 11, 12)),
            "devolvido em 09/11/2026",
        )

    def test_relatorio_vazio_informa_que_nao_ha_atrasos(self):
        relatorio = RelatorioMultas(date(2026, 11, 23), (), Decimal("0.00"))

        texto = formatar_relatorio_multas(relatorio)

        self.assertIn("Nenhum empréstimo em atraso.", texto)
        self.assertIn("Total das multas: R$ 0,00", texto)


if __name__ == "__main__":
    unittest.main()
