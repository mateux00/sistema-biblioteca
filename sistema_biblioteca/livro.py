from dataclasses import dataclass

from sistema_biblioteca.validacao import validar_identificador, validar_texto


@dataclass(frozen=True)
class Livro:
    identificador: int
    titulo: str
    autor: str
    categoria: str

    def __post_init__(self) -> None:
        validar_identificador(self.identificador, "identificador do livro")
        validar_texto(self.titulo, "título")
        validar_texto(self.autor, "autor")
        validar_texto(self.categoria, "categoria")

    def pertence_a_categoria(self, categoria: str) -> bool:
        return self.categoria.strip().casefold() == categoria.strip().casefold()
