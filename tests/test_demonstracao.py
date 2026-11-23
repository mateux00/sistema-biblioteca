import io
import unittest
from contextlib import redirect_stdout
from datetime import date

from main import DATA_REFERENCIA_PADRAO, ler_data_referencia, main


class DemonstracaoTest(unittest.TestCase):
    def executar(self, argumentos):
        saida = io.StringIO()
        with redirect_stdout(saida):
            codigo = main(argumentos)
        return codigo, saida.getvalue()

    def test_le_a_data_de_referencia(self):
        self.assertEqual(ler_data_referencia([]), DATA_REFERENCIA_PADRAO)
        self.assertEqual(ler_data_referencia(["2026-12-01"]), date(2026, 12, 1))

    def test_demonstracao_completa(self):
        codigo, texto = self.executar([])

        self.assertEqual(codigo, 0)
        self.assertIn('O livro "Dom Casmurro" já está emprestado.', texto)
        self.assertIn("Total das multas: R$ 64,00", texto)
        self.assertIn("Resultados equivalentes: sim", texto)

    def test_data_invalida_encerra_com_erro(self):
        codigo, texto = self.executar(["23/11/2026"])

        self.assertEqual(codigo, 2)
        self.assertIn("Data inválida", texto)


if __name__ == "__main__":
    unittest.main()
