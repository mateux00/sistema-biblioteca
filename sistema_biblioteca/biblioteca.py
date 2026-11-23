from datetime import date
from threading import Lock
from typing import Dict, Tuple

from sistema_biblioteca.emprestimo import Emprestimo
from sistema_biblioteca.estatisticas import Estatisticas, gerar_estatisticas
from sistema_biblioteca.excecoes import (
    EmprestimoNaoEncontradoError,
    LivroIndisponivelError,
    LivroNaoEncontradoError,
    MatriculaDuplicadaError,
    UsuarioNaoEncontradoError,
)
from sistema_biblioteca.funcional import (
    calcular_data_prevista,
    filtrar_emprestimos_ativos,
    filtrar_emprestimos_atrasados,
    filtrar_emprestimos_do_usuario,
    filtrar_livros_disponiveis,
    filtrar_livros_por_categoria,
    livro_esta_disponivel,
    proximo_identificador,
)
from sistema_biblioteca.livro import Livro
from sistema_biblioteca.relatorios import RelatorioMultas, gerar_relatorio_multas
from sistema_biblioteca.usuario import Usuario
from sistema_biblioteca.validacao import validar_texto

PRAZO_PADRAO_EM_DIAS = 14


class Biblioteca:
    def __init__(self, nome: str) -> None:
        validar_texto(nome, "nome da biblioteca")
        self.__nome = nome
        self.__livros: Dict[int, Livro] = {}
        self.__usuarios: Dict[int, Usuario] = {}
        self.__emprestimos: Dict[int, Emprestimo] = {}
        self.__trava = Lock()

    @property
    def nome(self) -> str:
        return self.__nome

    @property
    def livros(self) -> Tuple[Livro, ...]:
        return tuple(self.__livros.values())

    @property
    def usuarios(self) -> Tuple[Usuario, ...]:
        return tuple(self.__usuarios.values())

    @property
    def emprestimos(self) -> Tuple[Emprestimo, ...]:
        return tuple(self.__emprestimos.values())

    def cadastrar_livro(self, titulo: str, autor: str, categoria: str) -> Livro:
        with self.__trava:
            livro = Livro(proximo_identificador(self.__livros), titulo, autor, categoria)
            self.__livros[livro.identificador] = livro
            return livro

    def cadastrar_usuario(self, nome: str, matricula: str) -> Usuario:
        with self.__trava:
            if any(map(lambda usuario: usuario.matricula == matricula, self.__usuarios.values())):
                raise MatriculaDuplicadaError(f"Já existe um usuário com a matrícula {matricula}.")
            usuario = Usuario(proximo_identificador(self.__usuarios), nome, matricula)
            self.__usuarios[usuario.identificador] = usuario
            return usuario

    def buscar_livro(self, identificador: int) -> Livro:
        livro = self.__livros.get(identificador)
        if livro is None:
            raise LivroNaoEncontradoError(f"Livro {identificador} não encontrado.")
        return livro

    def buscar_usuario(self, identificador: int) -> Usuario:
        usuario = self.__usuarios.get(identificador)
        if usuario is None:
            raise UsuarioNaoEncontradoError(f"Usuário {identificador} não encontrado.")
        return usuario

    def buscar_emprestimo(self, identificador: int) -> Emprestimo:
        emprestimo = self.__emprestimos.get(identificador)
        if emprestimo is None:
            raise EmprestimoNaoEncontradoError(f"Empréstimo {identificador} não encontrado.")
        return emprestimo

    def consultar_livros_por_categoria(self, categoria: str) -> Tuple[Livro, ...]:
        return filtrar_livros_por_categoria(self.livros, categoria)

    def livros_disponiveis(self) -> Tuple[Livro, ...]:
        return filtrar_livros_disponiveis(self.livros, self.emprestimos)

    def livro_disponivel(self, identificador_livro: int) -> bool:
        return livro_esta_disponivel(self.buscar_livro(identificador_livro), self.emprestimos)

    def registrar_emprestimo(
        self,
        identificador_livro: int,
        identificador_usuario: int,
        data_emprestimo: date,
        prazo_em_dias: int = PRAZO_PADRAO_EM_DIAS,
    ) -> Emprestimo:
        with self.__trava:
            livro = self.buscar_livro(identificador_livro)
            usuario = self.buscar_usuario(identificador_usuario)
            if not livro_esta_disponivel(livro, self.emprestimos):
                raise LivroIndisponivelError(f'O livro "{livro.titulo}" já está emprestado.')
            emprestimo = Emprestimo(
                identificador=proximo_identificador(self.__emprestimos),
                livro=livro,
                usuario=usuario,
                data_emprestimo=data_emprestimo,
                data_prevista_devolucao=calcular_data_prevista(data_emprestimo, prazo_em_dias),
            )
            self.__emprestimos[emprestimo.identificador] = emprestimo
            return emprestimo

    def registrar_devolucao(self, identificador_emprestimo: int, data_devolucao: date) -> Emprestimo:
        with self.__trava:
            emprestimo = self.buscar_emprestimo(identificador_emprestimo)
            emprestimo_devolvido = emprestimo.com_devolucao(data_devolucao)
            self.__emprestimos[emprestimo_devolvido.identificador] = emprestimo_devolvido
            return emprestimo_devolvido

    def emprestimos_do_usuario(self, identificador_usuario: int) -> Tuple[Emprestimo, ...]:
        usuario = self.buscar_usuario(identificador_usuario)
        return filtrar_emprestimos_do_usuario(self.emprestimos, usuario)

    def emprestimos_ativos(self) -> Tuple[Emprestimo, ...]:
        return filtrar_emprestimos_ativos(self.emprestimos)

    def emprestimos_atrasados(self, data_referencia: date) -> Tuple[Emprestimo, ...]:
        return filtrar_emprestimos_atrasados(self.emprestimos, data_referencia)

    def relatorio_multas(self, data_referencia: date) -> RelatorioMultas:
        return gerar_relatorio_multas(self.emprestimos, data_referencia)

    def estatisticas(self, data_referencia: date) -> Estatisticas:
        return gerar_estatisticas(self.livros, self.usuarios, self.emprestimos, data_referencia)
