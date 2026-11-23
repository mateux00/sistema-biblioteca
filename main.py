import sys
from datetime import date
from typing import Callable, Iterable, Sequence

from sistema_biblioteca.biblioteca import Biblioteca
from sistema_biblioteca.emprestimo import Emprestimo
from sistema_biblioteca.excecoes import BibliotecaError
from sistema_biblioteca.formatacao import (
    formatar_data,
    formatar_emprestimo,
    formatar_estatisticas,
    formatar_livro,
    formatar_moeda,
    formatar_relatorio_multas,
    formatar_usuario,
)
from sistema_biblioteca.funcional import filtrar_livros_por_categoria
from sistema_biblioteca.paradigmas import (
    calcular_total_multas_funcional,
    calcular_total_multas_imperativo,
)

DATA_REFERENCIA_PADRAO = date(2026, 11, 23)


def ler_data_referencia(argumentos: Sequence[str]) -> date:
    if not argumentos:
        return DATA_REFERENCIA_PADRAO
    return date.fromisoformat(argumentos[0])


def exibir_secao(titulo: str) -> None:
    print()
    print(titulo)
    print("=" * len(titulo))


def exibir_linhas(linhas: Iterable[str]) -> None:
    print("\n".join(linhas))


def exibir_acervo(biblioteca: Biblioteca) -> None:
    exibir_linhas(
        map(
            lambda livro: formatar_livro(livro, biblioteca.livro_disponivel(livro.identificador)),
            biblioteca.livros,
        )
    )


def cadastrar_acervo(biblioteca: Biblioteca) -> None:
    biblioteca.cadastrar_livro("Dom Casmurro", "Machado de Assis", "Literatura")
    biblioteca.cadastrar_livro("O Cortiço", "Aluísio Azevedo", "Literatura")
    biblioteca.cadastrar_livro("Código Limpo", "Robert C. Martin", "Programação")
    biblioteca.cadastrar_livro("Entendendo Algoritmos", "Aditya Bhargava", "Programação")
    biblioteca.cadastrar_livro(
        "Introdução à Programação com Python", "Nilo Ney Coutinho Menezes", "Programação"
    )
    biblioteca.cadastrar_livro("Sapiens", "Yuval Noah Harari", "História")


def cadastrar_usuarios(biblioteca: Biblioteca) -> None:
    biblioteca.cadastrar_usuario("Ana Souza", "2024001")
    biblioteca.cadastrar_usuario("Bruno Lima", "2024002")
    biblioteca.cadastrar_usuario("Carla Mendes", "2024003")


def tentar(descricao: str, operacao: Callable[[], Emprestimo]) -> None:
    try:
        resultado = operacao()
        print(f"OK: {descricao} → empréstimo #{resultado.identificador}")
    except BibliotecaError as erro:
        print(f"Bloqueado: {descricao} → {erro}")


def emprestar(biblioteca: Biblioteca, livro: int, usuario: int, data: date) -> Callable[[], Emprestimo]:
    return lambda: biblioteca.registrar_emprestimo(livro, usuario, data)


def devolver(biblioteca: Biblioteca, emprestimo: int, data: date) -> Callable[[], Emprestimo]:
    return lambda: biblioteca.registrar_devolucao(emprestimo, data)


def demonstrar_emprestimos(biblioteca: Biblioteca, data_referencia: date) -> None:
    tentar("Ana pega Dom Casmurro", emprestar(biblioteca, 1, 1, date(2026, 10, 20)))
    tentar("Bruno pega Código Limpo", emprestar(biblioteca, 3, 2, date(2026, 11, 1)))
    tentar("Carla pega Sapiens", emprestar(biblioteca, 6, 3, date(2026, 11, 15)))
    tentar("Ana pega Entendendo Algoritmos", emprestar(biblioteca, 4, 1, date(2026, 10, 1)))
    tentar("Bruno pega O Cortiço", emprestar(biblioteca, 2, 2, date(2026, 11, 10)))
    tentar("Carla tenta pegar Dom Casmurro", emprestar(biblioteca, 1, 3, date(2026, 11, 2)))
    tentar("Ana devolve Entendendo Algoritmos", devolver(biblioteca, 4, date(2026, 10, 30)))
    tentar("Ana tenta devolver de novo o empréstimo #4", devolver(biblioteca, 4, date(2026, 11, 1)))
    tentar("Carla pega Entendendo Algoritmos", emprestar(biblioteca, 4, 3, date(2026, 11, 5)))

    print()
    print("Empréstimos registrados:")
    exibir_linhas(
        map(
            lambda emprestimo: formatar_emprestimo(emprestimo, data_referencia),
            biblioteca.emprestimos,
        )
    )


def demonstrar_filtragem(biblioteca: Biblioteca) -> None:
    acervo = biblioteca.livros
    programacao = filtrar_livros_por_categoria(acervo, "Programação")
    exibir_linhas(map(lambda livro: f"{livro.titulo} — {livro.autor}", programacao))
    print(f"Encontrados: {len(programacao)} | o acervo original continua com {len(acervo)} livros")


def demonstrar_comparacao(biblioteca: Biblioteca, data_referencia: date) -> None:
    imperativo = calcular_total_multas_imperativo(biblioteca.emprestimos, data_referencia)
    funcional = calcular_total_multas_funcional(biblioteca.emprestimos, data_referencia)
    print(f"Versão imperativa (for + if + acumulador): {formatar_moeda(imperativo)}")
    print(f"Versão funcional (filter + map + reduce):  {formatar_moeda(funcional)}")
    print(f"Resultados equivalentes: {'sim' if imperativo == funcional else 'não'}")


def executar_demonstracao(data_referencia: date) -> None:
    biblioteca = Biblioteca("Biblioteca Universitária")
    print(f"{biblioteca.nome} | data de referência: {formatar_data(data_referencia)}")

    exibir_secao("1. Cadastro de livros e usuários")
    cadastrar_acervo(biblioteca)
    cadastrar_usuarios(biblioteca)
    exibir_acervo(biblioteca)
    exibir_linhas(map(formatar_usuario, biblioteca.usuarios))

    exibir_secao("2. Empréstimos e devoluções")
    demonstrar_emprestimos(biblioteca, data_referencia)

    exibir_secao("3. Disponibilidade do acervo")
    exibir_acervo(biblioteca)

    exibir_secao("4. Filtragem por categoria (filter): Programação")
    demonstrar_filtragem(biblioteca)

    exibir_secao("5. Empréstimos ativos em atraso (filter)")
    atrasados = biblioteca.emprestimos_atrasados(data_referencia)
    exibir_linhas(
        map(lambda emprestimo: formatar_emprestimo(emprestimo, data_referencia), atrasados)
    )

    exibir_secao("6. Relatório de multas (filter → map → reduce)")
    print(formatar_relatorio_multas(biblioteca.relatorio_multas(data_referencia)))

    exibir_secao("7. Estatísticas")
    print(formatar_estatisticas(biblioteca.estatisticas(data_referencia)))

    exibir_secao("8. Comparação entre paradigmas: total de multas")
    demonstrar_comparacao(biblioteca, data_referencia)


def main(argumentos: Sequence[str]) -> int:
    try:
        data_referencia = ler_data_referencia(argumentos)
    except ValueError:
        print("Data inválida. Use o formato AAAA-MM-DD, por exemplo: python3 main.py 2026-12-01")
        return 2
    executar_demonstracao(data_referencia)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
