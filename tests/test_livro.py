import unittest
from dataclasses import FrozenInstanceError

from sistema_biblioteca.excecoes import DadosInvalidosError
from sistema_biblioteca.livro import Livro


class LivroTest(unittest.TestCase):
    def test_cria_livro_com_os_dados_informados(self):
        livro = Livro(1, "Dom Casmurro", "Machado de Assis", "Literatura")

        self.assertEqual(livro.identificador, 1)
        self.assertEqual(livro.titulo, "Dom Casmurro")
        self.assertEqual(livro.autor, "Machado de Assis")
        self.assertEqual(livro.categoria, "Literatura")

    def test_livro_e_imutavel(self):
        livro = Livro(1, "Dom Casmurro", "Machado de Assis", "Literatura")

        with self.assertRaises(FrozenInstanceError):
            livro.titulo = "Outro título"

    def test_rejeita_titulo_vazio(self):
        with self.assertRaises(DadosInvalidosError):
            Livro(1, "   ", "Machado de Assis", "Literatura")

    def test_rejeita_identificador_invalido(self):
        with self.assertRaises(DadosInvalidosError):
            Livro(0, "Dom Casmurro", "Machado de Assis", "Literatura")

    def test_compara_categoria_sem_diferenciar_maiusculas(self):
        livro = Livro(1, "Código Limpo", "Robert C. Martin", "Programação")

        self.assertTrue(livro.pertence_a_categoria(" programação "))
        self.assertFalse(livro.pertence_a_categoria("Literatura"))


if __name__ == "__main__":
    unittest.main()
