from dataclasses import dataclass

from sistema_biblioteca.validacao import validar_identificador, validar_texto


@dataclass(frozen=True)
class Usuario:
    identificador: int
    nome: str
    matricula: str

    def __post_init__(self) -> None:
        validar_identificador(self.identificador, "identificador do usuário")
        validar_texto(self.nome, "nome")
        validar_texto(self.matricula, "matrícula")
