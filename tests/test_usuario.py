import unittest
from dataclasses import FrozenInstanceError

from sistema_biblioteca.excecoes import DadosInvalidosError
from sistema_biblioteca.usuario import Usuario


class UsuarioTest(unittest.TestCase):
    def test_cria_usuario_com_os_dados_informados(self):
        usuario = Usuario(1, "Ana Souza", "2024001")

        self.assertEqual(usuario.identificador, 1)
        self.assertEqual(usuario.nome, "Ana Souza")
        self.assertEqual(usuario.matricula, "2024001")

    def test_usuario_e_imutavel(self):
        usuario = Usuario(1, "Ana Souza", "2024001")

        with self.assertRaises(FrozenInstanceError):
            usuario.nome = "Outro nome"

    def test_rejeita_nome_vazio(self):
        with self.assertRaises(DadosInvalidosError):
            Usuario(1, "", "2024001")

    def test_rejeita_matricula_vazia(self):
        with self.assertRaises(DadosInvalidosError):
            Usuario(1, "Ana Souza", " ")


if __name__ == "__main__":
    unittest.main()
