import unittest
from datetime import date
from decimal import Decimal

from sistema_biblioteca.estatisticas import (
    contar_emprestimos_ativos,
    contar_emprestimos_atrasados,
    contar_emprestimos_por_usuario,
    contar_livros_por_categoria,
    gerar_estatisticas,
    incrementar_contagem,
)
from tests.fabrica import criar_emprestimo, criar_livro, criar_usuario

DATA_REFERENCIA = date(2026, 11, 23)


class EstatisticasTest(unittest.TestCase):
    def setUp(self):
        self.ana = criar_usuario(1)
        self.bruno = criar_usuario(2)
        self.carla = criar_usuario(3)
        self.livros = (
            criar_livro(1, "Literatura"),
            criar_livro(2, "Programação"),
            criar_livro(3, "Programação"),
        )
        self.emprestimos = (
            criar_emprestimo(1, data_prevista=date(2026, 11, 3), usuario=self.ana),
            criar_emprestimo(2, data_prevista=date(2026, 11, 30), usuario=self.ana),
            criar_emprestimo(
                3,
                data_prevista=date(2026, 11, 5),
                data_devolucao=date(2026, 11, 6),
                usuario=self.bruno,
            ),
        )

    def test_incrementar_contagem_cria_um_novo_dicionario(self):
        original = {"Literatura": 1}

        novo = incrementar_contagem(original, "Literatura")

        self.assertEqual(original, {"Literatura": 1})
        self.assertEqual(novo, {"Literatura": 2})

    def test_conta_livros_por_categoria(self):
        self.assertEqual(
            dict(contar_livros_por_categoria(self.livros)), {"Literatura": 1, "Programação": 2}
        )

    def test_conta_emprestimos_por_usuario_incluindo_quem_nao_pegou_livros(self):
        contagem = contar_emprestimos_por_usuario((self.ana, self.bruno, self.carla), self.emprestimos)

        self.assertEqual(dict(contagem), {self.ana: 2, self.bruno: 1, self.carla: 0})

    def test_resultado_das_contagens_e_somente_leitura(self):
        contagem = contar_livros_por_categoria(self.livros)

        with self.assertRaises(TypeError):
            contagem["História"] = 1

    def test_conta_ativos_e_atrasados(self):
        self.assertEqual(contar_emprestimos_ativos(self.emprestimos), 2)
        self.assertEqual(contar_emprestimos_atrasados(self.emprestimos, DATA_REFERENCIA), 1)

    def test_gera_todas_as_estatisticas(self):
        estatisticas = gerar_estatisticas(
            self.livros, (self.ana, self.bruno, self.carla), iter(self.emprestimos), DATA_REFERENCIA
        )

        self.assertEqual(estatisticas.data_referencia, DATA_REFERENCIA)
        self.assertEqual(estatisticas.livros_por_categoria["Programação"], 2)
        self.assertEqual(estatisticas.emprestimos_por_usuario[self.ana], 2)
        self.assertEqual(estatisticas.emprestimos_ativos, 2)
        self.assertEqual(estatisticas.emprestimos_atrasados, 1)
        self.assertEqual(estatisticas.total_multas, Decimal("40.00"))


if __name__ == "__main__":
    unittest.main()
