import threading
import unittest
from datetime import date
from decimal import Decimal

from sistema_biblioteca.biblioteca import Biblioteca
from sistema_biblioteca.excecoes import (
    EmprestimoJaDevolvidoError,
    EmprestimoNaoEncontradoError,
    LivroIndisponivelError,
    LivroNaoEncontradoError,
    MatriculaDuplicadaError,
    UsuarioNaoEncontradoError,
)


class BibliotecaTest(unittest.TestCase):
    def setUp(self):
        self.biblioteca = Biblioteca("Biblioteca Teste")
        self.dom_casmurro = self.biblioteca.cadastrar_livro(
            "Dom Casmurro", "Machado de Assis", "Literatura"
        )
        self.codigo_limpo = self.biblioteca.cadastrar_livro(
            "Código Limpo", "Robert C. Martin", "Programação"
        )
        self.ana = self.biblioteca.cadastrar_usuario("Ana Souza", "2024001")
        self.bruno = self.biblioteca.cadastrar_usuario("Bruno Lima", "2024002")

    def emprestar_dom_casmurro_para_ana(self):
        return self.biblioteca.registrar_emprestimo(
            self.dom_casmurro.identificador, self.ana.identificador, date(2026, 11, 1)
        )

    def test_cadastra_e_consulta_livros_e_usuarios(self):
        self.assertEqual(self.biblioteca.livros, (self.dom_casmurro, self.codigo_limpo))
        self.assertEqual(self.biblioteca.usuarios, (self.ana, self.bruno))
        self.assertEqual(self.biblioteca.buscar_livro(2), self.codigo_limpo)
        self.assertEqual(self.biblioteca.buscar_usuario(1), self.ana)

    def test_gera_identificadores_sequenciais(self):
        self.assertEqual((self.dom_casmurro.identificador, self.codigo_limpo.identificador), (1, 2))
        self.assertEqual((self.ana.identificador, self.bruno.identificador), (1, 2))

    def test_consulta_livros_por_categoria(self):
        self.assertEqual(
            self.biblioteca.consultar_livros_por_categoria("programação"), (self.codigo_limpo,)
        )

    def test_erros_de_consulta(self):
        with self.assertRaises(LivroNaoEncontradoError):
            self.biblioteca.buscar_livro(99)
        with self.assertRaises(UsuarioNaoEncontradoError):
            self.biblioteca.buscar_usuario(99)
        with self.assertRaises(EmprestimoNaoEncontradoError):
            self.biblioteca.buscar_emprestimo(99)

    def test_nao_aceita_matricula_repetida(self):
        with self.assertRaises(MatriculaDuplicadaError):
            self.biblioteca.cadastrar_usuario("Outra Ana", "2024001")

    def test_registra_emprestimo_com_prazo_padrao_de_quatorze_dias(self):
        emprestimo = self.emprestar_dom_casmurro_para_ana()

        self.assertEqual(emprestimo.livro, self.dom_casmurro)
        self.assertEqual(emprestimo.usuario, self.ana)
        self.assertEqual(emprestimo.data_prevista_devolucao, date(2026, 11, 15))
        self.assertTrue(emprestimo.ativo)
        self.assertFalse(self.biblioteca.livro_disponivel(self.dom_casmurro.identificador))

    def test_livro_nao_pode_ser_emprestado_para_dois_usuarios(self):
        self.emprestar_dom_casmurro_para_ana()

        with self.assertRaises(LivroIndisponivelError):
            self.biblioteca.registrar_emprestimo(
                self.dom_casmurro.identificador, self.bruno.identificador, date(2026, 11, 2)
            )

    def test_usuario_pode_ter_varios_emprestimos(self):
        self.emprestar_dom_casmurro_para_ana()
        self.biblioteca.registrar_emprestimo(
            self.codigo_limpo.identificador, self.ana.identificador, date(2026, 11, 2)
        )

        self.assertEqual(len(self.biblioteca.emprestimos_do_usuario(self.ana.identificador)), 2)
        self.assertEqual(self.biblioteca.emprestimos_do_usuario(self.bruno.identificador), ())

    def test_devolucao_registra_a_data_e_libera_o_livro(self):
        emprestimo = self.emprestar_dom_casmurro_para_ana()

        devolvido = self.biblioteca.registrar_devolucao(emprestimo.identificador, date(2026, 11, 10))

        self.assertEqual(devolvido.data_devolucao, date(2026, 11, 10))
        self.assertEqual(self.biblioteca.buscar_emprestimo(emprestimo.identificador), devolvido)
        self.assertTrue(self.biblioteca.livro_disponivel(self.dom_casmurro.identificador))
        self.assertIsNone(emprestimo.data_devolucao)

        novo = self.biblioteca.registrar_emprestimo(
            self.dom_casmurro.identificador, self.bruno.identificador, date(2026, 11, 11)
        )
        self.assertEqual(novo.usuario, self.bruno)

    def test_nao_permite_devolver_duas_vezes(self):
        emprestimo = self.emprestar_dom_casmurro_para_ana()
        self.biblioteca.registrar_devolucao(emprestimo.identificador, date(2026, 11, 10))

        with self.assertRaises(EmprestimoJaDevolvidoError):
            self.biblioteca.registrar_devolucao(emprestimo.identificador, date(2026, 11, 12))

    def test_colecoes_expostas_sao_copias_somente_leitura(self):
        livros = self.biblioteca.livros
        lista_externa = list(livros)
        lista_externa.clear()

        self.assertIsInstance(livros, tuple)
        self.assertEqual(len(self.biblioteca.livros), 2)
        self.assertFalse(hasattr(self.biblioteca, "__livros"))
        with self.assertRaises(AttributeError):
            self.biblioteca.livros = ()

    def test_livros_disponiveis_e_emprestimos_ativos(self):
        self.emprestar_dom_casmurro_para_ana()

        self.assertEqual(self.biblioteca.livros_disponiveis(), (self.codigo_limpo,))
        self.assertEqual(len(self.biblioteca.emprestimos_ativos()), 1)

    def test_relatorio_e_estatisticas_usam_a_data_de_referencia(self):
        self.emprestar_dom_casmurro_para_ana()

        relatorio = self.biblioteca.relatorio_multas(date(2026, 11, 20))
        estatisticas = self.biblioteca.estatisticas(date(2026, 11, 20))

        self.assertEqual(relatorio.total, Decimal("10.00"))
        self.assertEqual(len(self.biblioteca.emprestimos_atrasados(date(2026, 11, 20))), 1)
        self.assertEqual(estatisticas.total_multas, Decimal("10.00"))
        self.assertEqual(estatisticas.emprestimos_por_usuario[self.ana], 1)

    def test_emprestimos_simultaneos_do_mesmo_livro_geram_apenas_um_emprestimo(self):
        usuarios = tuple(
            map(
                lambda numero: self.biblioteca.cadastrar_usuario(f"Aluno {numero}", f"9{numero:03d}"),
                range(8),
            )
        )
        largada = threading.Barrier(len(usuarios))
        resultados = []

        def tentar_emprestar(usuario):
            largada.wait()
            try:
                self.biblioteca.registrar_emprestimo(
                    self.dom_casmurro.identificador, usuario.identificador, date(2026, 11, 1)
                )
                resultados.append("emprestado")
            except LivroIndisponivelError:
                resultados.append("bloqueado")

        threads = tuple(
            map(lambda usuario: threading.Thread(target=tentar_emprestar, args=(usuario,)), usuarios)
        )
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertEqual(resultados.count("emprestado"), 1)
        self.assertEqual(resultados.count("bloqueado"), len(usuarios) - 1)
        self.assertEqual(len(self.biblioteca.emprestimos_ativos()), 1)


if __name__ == "__main__":
    unittest.main()
