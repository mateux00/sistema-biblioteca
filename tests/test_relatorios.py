import unittest
from datetime import date
from decimal import Decimal

from sistema_biblioteca.relatorios import gerar_relatorio_multas
from tests.fabrica import criar_emprestimo

DATA_REFERENCIA = date(2026, 11, 23)


class RelatorioMultasTest(unittest.TestCase):
    def setUp(self):
        self.emprestimos = [
            criar_emprestimo(1, data_prevista=date(2026, 11, 3)),
            criar_emprestimo(2, data_prevista=date(2026, 11, 30)),
            criar_emprestimo(3, data_prevista=date(2026, 11, 5), data_devolucao=date(2026, 11, 20)),
            criar_emprestimo(4, data_prevista=date(2026, 11, 19)),
        ]

    def test_inclui_somente_emprestimos_ativos_e_atrasados(self):
        relatorio = gerar_relatorio_multas(self.emprestimos, DATA_REFERENCIA)

        self.assertEqual(tuple(map(lambda item: item.emprestimo_id, relatorio.itens)), (1, 4))

    def test_calcula_multa_de_dois_reais_por_dia(self):
        relatorio = gerar_relatorio_multas(self.emprestimos, DATA_REFERENCIA)

        self.assertEqual(relatorio.itens[0].dias_de_atraso, 20)
        self.assertEqual(relatorio.itens[0].valor, Decimal("40.00"))
        self.assertEqual(relatorio.itens[1].dias_de_atraso, 4)
        self.assertEqual(relatorio.itens[1].valor, Decimal("8.00"))

    def test_soma_o_total_das_multas(self):
        relatorio = gerar_relatorio_multas(self.emprestimos, DATA_REFERENCIA)

        self.assertEqual(relatorio.total, Decimal("48.00"))
        self.assertEqual(relatorio.data_referencia, DATA_REFERENCIA)

    def test_nao_modifica_os_dados_originais(self):
        copia_antes = list(self.emprestimos)

        gerar_relatorio_multas(self.emprestimos, DATA_REFERENCIA)

        self.assertEqual(self.emprestimos, copia_antes)
        self.assertTrue(all(map(lambda emprestimo: emprestimo.data_devolucao is None, copia_antes[:2])))

    def test_sem_atrasos_o_total_e_zero(self):
        relatorio = gerar_relatorio_multas(self.emprestimos, date(2026, 11, 1))

        self.assertEqual(relatorio.itens, ())
        self.assertEqual(relatorio.total, Decimal("0.00"))

    def test_mesma_entrada_gera_o_mesmo_relatorio(self):
        primeiro = gerar_relatorio_multas(self.emprestimos, DATA_REFERENCIA)
        segundo = gerar_relatorio_multas(self.emprestimos, DATA_REFERENCIA)

        self.assertEqual(primeiro, segundo)


if __name__ == "__main__":
    unittest.main()
