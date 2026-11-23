import unittest
from datetime import date
from decimal import Decimal

from sistema_biblioteca.excecoes import DadosInvalidosError
from sistema_biblioteca.funcional import (
    MULTA_DIARIA,
    calcular_data_prevista,
    calcular_multa,
    filtrar_emprestimos_ativos,
    filtrar_emprestimos_atrasados,
    filtrar_livros_disponiveis,
    filtrar_livros_por_categoria,
    livro_esta_disponivel,
    proximo_identificador,
)
from tests.fabrica import criar_emprestimo, criar_livro


class CalcularMultaTest(unittest.TestCase):
    def test_multiplica_os_dias_pelo_valor_diario(self):
        self.assertEqual(calcular_multa(5, MULTA_DIARIA), Decimal("10.00"))

    def test_sem_atraso_nao_ha_multa(self):
        self.assertEqual(calcular_multa(0, MULTA_DIARIA), Decimal("0.00"))
        self.assertEqual(calcular_multa(-3, MULTA_DIARIA), Decimal("0.00"))

    def test_entradas_iguais_produzem_saidas_iguais(self):
        resultados = {calcular_multa(7, Decimal("2.00")) for _ in range(100)}

        self.assertEqual(resultados, {Decimal("14.00")})


class DataPrevistaTest(unittest.TestCase):
    def test_soma_o_prazo_a_data_do_emprestimo(self):
        self.assertEqual(calcular_data_prevista(date(2026, 11, 20), 14), date(2026, 12, 4))

    def test_rejeita_prazo_menor_que_um_dia(self):
        with self.assertRaises(DadosInvalidosError):
            calcular_data_prevista(date(2026, 11, 20), 0)


class ProximoIdentificadorTest(unittest.TestCase):
    def test_comeca_em_um_e_segue_o_maior_identificador(self):
        self.assertEqual(proximo_identificador({}), 1)
        self.assertEqual(proximo_identificador({1: "a", 2: "b"}), 3)


class FiltrarLivrosTest(unittest.TestCase):
    def setUp(self):
        self.livros = [
            criar_livro(1, "Literatura"),
            criar_livro(2, "Programação"),
            criar_livro(3, "Programação"),
        ]

    def test_retorna_apenas_livros_da_categoria(self):
        resultado = filtrar_livros_por_categoria(self.livros, "Programação")

        self.assertEqual(tuple(map(lambda livro: livro.identificador, resultado)), (2, 3))

    def test_nao_altera_a_colecao_original(self):
        copia_antes = list(self.livros)

        filtrar_livros_por_categoria(self.livros, "Programação")

        self.assertEqual(self.livros, copia_antes)

    def test_retorna_tupla_vazia_quando_nao_ha_livros_da_categoria(self):
        self.assertEqual(filtrar_livros_por_categoria(self.livros, "História"), ())


class FiltrarEmprestimosTest(unittest.TestCase):
    def setUp(self):
        self.atrasado = criar_emprestimo(1, data_prevista=date(2026, 11, 10))
        self.no_prazo = criar_emprestimo(2, data_prevista=date(2026, 11, 30))
        self.devolvido = criar_emprestimo(
            3, data_prevista=date(2026, 11, 5), data_devolucao=date(2026, 11, 20)
        )
        self.emprestimos = (self.atrasado, self.no_prazo, self.devolvido)

    def test_seleciona_somente_ativos(self):
        self.assertEqual(
            filtrar_emprestimos_ativos(self.emprestimos), (self.atrasado, self.no_prazo)
        )

    def test_seleciona_somente_ativos_em_atraso(self):
        self.assertEqual(
            filtrar_emprestimos_atrasados(self.emprestimos, date(2026, 11, 23)), (self.atrasado,)
        )

    def test_livro_com_emprestimo_ativo_fica_indisponivel(self):
        self.assertFalse(livro_esta_disponivel(self.atrasado.livro, self.emprestimos))

    def test_livro_devolvido_volta_a_ficar_disponivel(self):
        self.assertTrue(livro_esta_disponivel(self.devolvido.livro, self.emprestimos))

    def test_filtra_livros_disponiveis(self):
        livros = (self.atrasado.livro, self.no_prazo.livro, self.devolvido.livro, criar_livro(9))

        disponiveis = filtrar_livros_disponiveis(livros, self.emprestimos)

        self.assertEqual(tuple(map(lambda livro: livro.identificador, disponiveis)), (3, 9))


if __name__ == "__main__":
    unittest.main()
