import unittest
from datetime import date
from decimal import Decimal

from sistema_biblioteca.paradigmas import (
    calcular_total_multas_funcional,
    calcular_total_multas_imperativo,
)
from tests.fabrica import criar_emprestimo


class ComparacaoParadigmasTest(unittest.TestCase):
    def setUp(self):
        self.emprestimos = (
            criar_emprestimo(1, data_prevista=date(2026, 11, 3)),
            criar_emprestimo(2, data_prevista=date(2026, 11, 30)),
            criar_emprestimo(3, data_prevista=date(2026, 11, 5), data_devolucao=date(2026, 11, 20)),
            criar_emprestimo(4, data_prevista=date(2026, 11, 19)),
        )

    def test_versoes_produzem_o_mesmo_total(self):
        datas = (date(2026, 11, 1), date(2026, 11, 10), date(2026, 11, 23), date(2026, 12, 31))

        for data_referencia in datas:
            with self.subTest(data_referencia=data_referencia):
                self.assertEqual(
                    calcular_total_multas_imperativo(self.emprestimos, data_referencia),
                    calcular_total_multas_funcional(self.emprestimos, data_referencia),
                )

    def test_total_esperado_na_data_de_referencia(self):
        self.assertEqual(
            calcular_total_multas_funcional(self.emprestimos, date(2026, 11, 23)), Decimal("48.00")
        )

    def test_colecao_vazia_resulta_em_zero_nas_duas_versoes(self):
        self.assertEqual(calcular_total_multas_imperativo((), date(2026, 11, 23)), Decimal("0.00"))
        self.assertEqual(calcular_total_multas_funcional((), date(2026, 11, 23)), Decimal("0.00"))


if __name__ == "__main__":
    unittest.main()
