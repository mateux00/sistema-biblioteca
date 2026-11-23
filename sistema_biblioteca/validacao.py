from sistema_biblioteca.excecoes import DadosInvalidosError


def validar_texto(valor: str, campo: str) -> None:
    if not isinstance(valor, str) or not valor.strip():
        raise DadosInvalidosError(f"O campo {campo} é obrigatório.")


def validar_identificador(valor: int, campo: str) -> None:
    if isinstance(valor, bool) or not isinstance(valor, int) or valor <= 0:
        raise DadosInvalidosError(f"O {campo} deve ser um inteiro positivo.")
