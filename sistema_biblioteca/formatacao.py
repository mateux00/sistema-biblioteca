from datetime import date
from decimal import Decimal

from sistema_biblioteca.emprestimo import Emprestimo
from sistema_biblioteca.estatisticas import Estatisticas
from sistema_biblioteca.funcional import CENTAVOS, MULTA_DIARIA
from sistema_biblioteca.livro import Livro
from sistema_biblioteca.relatorios import ItemMulta, RelatorioMultas
from sistema_biblioteca.usuario import Usuario


def formatar_moeda(valor: Decimal) -> str:
    texto_com_ponto = f"{valor.quantize(CENTAVOS):,.2f}"
    return "R$ " + texto_com_ponto.translate(str.maketrans(",.", ".,"))


def formatar_data(data: date) -> str:
    return data.strftime("%d/%m/%Y")


def formatar_livro(livro: Livro, disponivel: bool) -> str:
    situacao = "disponível" if disponivel else "emprestado"
    return f"[{livro.identificador}] {livro.titulo} — {livro.autor} ({livro.categoria}): {situacao}"


def formatar_usuario(usuario: Usuario) -> str:
    return f"[{usuario.identificador}] {usuario.nome} — matrícula {usuario.matricula}"


def descrever_situacao(emprestimo: Emprestimo, data_referencia: date) -> str:
    if not emprestimo.ativo:
        return f"devolvido em {formatar_data(emprestimo.data_devolucao)}"
    if emprestimo.esta_atrasado(data_referencia):
        return f"atrasado há {emprestimo.dias_de_atraso(data_referencia)} dia(s)"
    return "ativo, dentro do prazo"


def formatar_emprestimo(emprestimo: Emprestimo, data_referencia: date) -> str:
    return (
        f"#{emprestimo.identificador} {emprestimo.livro.titulo} → {emprestimo.usuario.nome} | "
        f"{formatar_data(emprestimo.data_emprestimo)} a "
        f"{formatar_data(emprestimo.data_prevista_devolucao)} | "
        f"{descrever_situacao(emprestimo, data_referencia)}"
    )


def formatar_item_multa(item: ItemMulta) -> str:
    return (
        f"#{item.emprestimo_id} {item.titulo_livro} ({item.nome_usuario}): "
        f"{item.dias_de_atraso} dia(s) × {formatar_moeda(MULTA_DIARIA)} = {formatar_moeda(item.valor)}"
    )


def formatar_relatorio_multas(relatorio: RelatorioMultas) -> str:
    cabecalho = f"Data de referência: {formatar_data(relatorio.data_referencia)}"
    linhas = tuple(map(formatar_item_multa, relatorio.itens)) or ("Nenhum empréstimo em atraso.",)
    rodape = f"Total das multas: {formatar_moeda(relatorio.total)}"
    return "\n".join((cabecalho, *linhas, rodape))


def formatar_estatisticas(estatisticas: Estatisticas) -> str:
    categorias = tuple(
        map(
            lambda par: f"  {par[0]}: {par[1]} livro(s)",
            estatisticas.livros_por_categoria.items(),
        )
    )
    usuarios = tuple(
        map(
            lambda par: f"  {par[0].nome}: {par[1]} empréstimo(s)",
            estatisticas.emprestimos_por_usuario.items(),
        )
    )
    return "\n".join(
        (
            "Livros por categoria:",
            *categorias,
            "Empréstimos por usuário:",
            *usuarios,
            f"Empréstimos ativos: {estatisticas.emprestimos_ativos}",
            f"Empréstimos ativos em atraso: {estatisticas.emprestimos_atrasados}",
            f"Valor total das multas: {formatar_moeda(estatisticas.total_multas)}",
        )
    )
