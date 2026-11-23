import unittest
from dataclasses import FrozenInstanceError
from datetime import date

from sistema_biblioteca.emprestimo import Emprestimo
from sistema_biblioteca.excecoes import DadosInvalidosError, EmprestimoJaDevolvidoError
from tests.fabrica import criar_emprestimo, criar_livro, criar_usuario


class EmprestimoTest(unittest.TestCase):
    def test_emprestimo_novo_esta_ativo(self):
        self.assertTrue(criar_emprestimo().ativo)

    def test_conta_dias_de_atraso_apos_a_data_prevista(self):
        emprestimo = criar_emprestimo(data_prevista=date(2026, 11, 10))

        self.assertEqual(emprestimo.dias_de_atraso(date(2026, 11, 13)), 3)
        self.assertTrue(emprestimo.esta_atrasado(date(2026, 11, 13)))

    def test_nao_ha_atraso_ate_a_data_prevista(self):
        emprestimo = criar_emprestimo(data_prevista=date(2026, 11, 10))

        self.assertEqual(emprestimo.dias_de_atraso(date(2026, 11, 10)), 0)
        self.assertFalse(emprestimo.esta_atrasado(date(2026, 11, 10)))
        self.assertEqual(emprestimo.dias_de_atraso(date(2026, 11, 5)), 0)

    def test_emprestimo_devolvido_nao_tem_atraso(self):
        emprestimo = criar_emprestimo(
            data_prevista=date(2026, 11, 10), data_devolucao=date(2026, 11, 20)
        )

        self.assertFalse(emprestimo.ativo)
        self.assertEqual(emprestimo.dias_de_atraso(date(2026, 12, 1)), 0)
        self.assertFalse(emprestimo.esta_atrasado(date(2026, 12, 1)))

    def test_devolucao_cria_novo_objeto_sem_alterar_o_original(self):
        original = criar_emprestimo()

        devolvido = original.com_devolucao(date(2026, 11, 8))

        self.assertIsNot(devolvido, original)
        self.assertIsNone(original.data_devolucao)
        self.assertTrue(original.ativo)
        self.assertEqual(devolvido.data_devolucao, date(2026, 11, 8))
        self.assertFalse(devolvido.ativo)

    def test_nao_permite_devolver_duas_vezes(self):
        devolvido = criar_emprestimo().com_devolucao(date(2026, 11, 8))

        with self.assertRaises(EmprestimoJaDevolvidoError):
            devolvido.com_devolucao(date(2026, 11, 9))

    def test_emprestimo_e_imutavel(self):
        emprestimo = criar_emprestimo()

        with self.assertRaises(FrozenInstanceError):
            emprestimo.data_devolucao = date(2026, 11, 8)

    def test_rejeita_data_prevista_anterior_ao_emprestimo(self):
        with self.assertRaises(DadosInvalidosError):
            Emprestimo(1, criar_livro(), criar_usuario(), date(2026, 11, 10), date(2026, 11, 1))

    def test_rejeita_devolucao_anterior_ao_emprestimo(self):
        with self.assertRaises(DadosInvalidosError):
            criar_emprestimo().com_devolucao(date(2026, 10, 1))


if __name__ == "__main__":
    unittest.main()
