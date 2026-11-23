# Sistema de Gerenciamento de Biblioteca

Atividade prática da disciplina **Linguagens de Programação** (Orientação a Objetos e Programação
Funcional). O sistema gerencia livros, usuários e empréstimos de uma biblioteca universitária,
controla a disponibilidade dos livros, calcula multas por atraso e gera relatórios e estatísticas.
A **POO** organiza as entidades e responsabilidades; a **Programação Funcional** filtra, transforma,
calcula e agrega os dados. Tudo fica em memória, sem banco de dados.

## Integrante

- Mateus Carvalho

## Linguagem e requisitos

- **Python 3.9 ou superior** (testado em 3.9 e 3.12)
- Apenas a biblioteca padrão: nenhuma dependência para instalar

## Como executar

```bash
git clone https://github.com/mateux00/sistema-biblioteca.git
cd sistema-biblioteca
python3 main.py
```

A demonstração usa a data de referência **23/11/2026**. Para calcular atrasos e multas em outra
data, passe a data no formato `AAAA-MM-DD`:

```bash
python3 main.py 2026-12-01
```

## Como rodar os testes

```bash
python3 -m unittest discover -s tests -v
```

São 68 testes cobrindo entidades, funções puras, relatório, estatísticas, regras de negócio da
`Biblioteca`, comparação de paradigmas, formatação, demonstração e empréstimos simultâneos.

## Funcionalidades

- Cadastro e consulta de livros e usuários (por identificador e por categoria)
- Registro de empréstimos (prazo padrão de 14 dias) e devoluções
- Controle de disponibilidade: um livro emprestado não pode ser emprestado de novo até ser devolvido
- Consulta de empréstimos: todos, por usuário, ativos e atrasados
- Multa de **R$ 2,00 por dia de atraso**, apenas para empréstimos ativos e atrasados
- Relatório de multas com `filter`, `map` e `reduce`, a partir de uma data de referência
- Estatísticas: livros por categoria, empréstimos por usuário, empréstimos ativos, ativos em atraso
  e valor total das multas
- Comparação entre uma versão imperativa e uma funcional do cálculo do total de multas
- Proteção contra dois empréstimos simultâneos do mesmo livro

## Estrutura do projeto

```
sistema-biblioteca/
├── main.py                      demonstração executável (entrada e saída: parte impura)
├── sistema_biblioteca/
│   ├── livro.py                 classe Livro (imutável)
│   ├── usuario.py               classe Usuario (imutável)
│   ├── emprestimo.py            classe Emprestimo (imutável, regras de atraso)
│   ├── biblioteca.py            classe Biblioteca (estado e operações de gerenciamento)
│   ├── funcional.py             funções puras: multa, filtros, disponibilidade
│   ├── relatorios.py            relatório de multas (filter → map → reduce)
│   ├── estatisticas.py          estatísticas (reduce)
│   ├── paradigmas.py            total de multas: versão imperativa x funcional
│   ├── formatacao.py            funções puras que transformam dados em texto
│   ├── validacao.py             validação dos dados das entidades
│   └── excecoes.py              exceções do domínio
└── tests/                       testes com unittest
```

## Modelagem orientada a objetos

| Classe | Atributos | Principais métodos | Responsabilidade |
|---|---|---|---|
| `Livro` | `identificador`, `titulo`, `autor`, `categoria` | `pertence_a_categoria(categoria)` | Representar um exemplar do acervo |
| `Usuario` | `identificador`, `nome`, `matricula` | — | Representar uma pessoa cadastrada |
| `Emprestimo` | `identificador`, `livro`, `usuario`, `data_emprestimo`, `data_prevista_devolucao`, `data_devolucao` | `ativo`, `dias_de_atraso(data)`, `esta_atrasado(data)`, `com_devolucao(data)` | Representar a retirada de um livro e saber se está atrasada |
| `Biblioteca` | `nome` e as coleções privadas `__livros`, `__usuarios`, `__emprestimos` | `cadastrar_livro`, `cadastrar_usuario`, `buscar_*`, `registrar_emprestimo`, `registrar_devolucao`, `emprestimos_do_usuario`, `emprestimos_ativos`, `emprestimos_atrasados`, `relatorio_multas`, `estatisticas` | Gerenciar o estado e aplicar as regras de negócio |

**Relacionamentos e multiplicidades**

- `Biblioteca` 1 ◆── 0..* `Livro`, 1 ◆── 0..* `Usuario` e 1 ◆── 0..* `Emprestimo` (composição:
  a biblioteca cria e guarda esses objetos)
- `Usuario` 1 ── 0..* `Emprestimo`: um usuário pode ter vários empréstimos
- `Livro` 1 ── 0..* `Emprestimo`: um livro tem histórico de vários empréstimos, mas no máximo um ativo
- Cada `Emprestimo` referencia exatamente 1 `Livro` e 1 `Usuario`

**Encapsulamento**

- `Livro`, `Usuario` e `Emprestimo` são `@dataclass(frozen=True)`: os atributos podem ser lidos, mas
  não alterados depois da criação. A validação acontece em `__post_init__`, então nunca existe um
  objeto em estado inválido (título vazio, devolução antes do empréstimo etc.).
- A `Biblioteca` guarda suas coleções em atributos privados (`self.__livros`, com *name mangling*)
  e só as expõe como **tuplas** (cópias somente leitura) pelas propriedades `livros`, `usuarios` e
  `emprestimos`. O estado só muda pelos métodos que aplicam as regras de negócio.
- A disponibilidade do livro **não é um campo**: é calculada a partir dos empréstimos ativos. Assim
  não existe risco de o campo "disponível" ficar diferente do que realmente está emprestado.

## Regras de negócio e onde estão implementadas

| Regra | Implementação |
|---|---|
| Um usuário pode ter vários empréstimos; cada empréstimo tem um único livro e um único usuário | Atributos `livro` e `usuario` de `Emprestimo`; `Biblioteca.emprestimos_do_usuario` |
| Um livro não pode estar emprestado para dois usuários ao mesmo tempo | `Biblioteca.registrar_emprestimo` verifica `livro_esta_disponivel` e lança `LivroIndisponivelError` |
| Cada livro é um exemplar único | Disponibilidade calculada por identificador do livro em `identificadores_de_livros_emprestados` |
| A devolução registra a data e libera o livro | `Emprestimo.com_devolucao` cria o empréstimo devolvido; `Biblioteca.registrar_devolucao` o guarda |
| Atrasado = data prevista ultrapassada e livro não devolvido | `Emprestimo.dias_de_atraso` e `Emprestimo.esta_atrasado` |
| Multa de R$ 2,00 por dia; sem atraso, sem multa | `MULTA_DIARIA` e `calcular_multa` em `funcional.py` |
| Relatório só com empréstimos ativos e atrasados, numa data de referência | `gerar_relatorio_multas(emprestimos, data_referencia)` |
| Sem multa para empréstimos devolvidos | `dias_de_atraso` retorna 0 quando o empréstimo não está ativo |

## Programação funcional

### Funções puras

Recebem tudo o que precisam por parâmetro, não leem nem alteram estado externo e sempre retornam
o mesmo resultado para as mesmas entradas (transparência referencial). Exemplos:

| Função | Arquivo | O que faz |
|---|---|---|
| `calcular_multa(dias_de_atraso, valor_diario)` | `funcional.py` | `max(dias, 0) × valor_diario` |
| `calcular_data_prevista(data, prazo)` | `funcional.py` | Data do empréstimo + prazo em dias |
| `filtrar_livros_por_categoria(livros, categoria)` | `funcional.py` | `filter` por categoria, retorna nova tupla |
| `filtrar_emprestimos_atrasados(emprestimos, data)` | `funcional.py` | `filter` dos ativos em atraso |
| `livro_esta_disponivel(livro, emprestimos)` | `funcional.py` | Usa `map` para montar um `frozenset` dos livros emprestados |
| `gerar_relatorio_multas(emprestimos, data)` | `relatorios.py` | `filter` → `map` → `reduce` |
| `contar_livros_por_categoria(livros)` | `estatisticas.py` | `reduce` montando a contagem |
| `incrementar_contagem(contagem, chave)` | `estatisticas.py` | Retorna um **novo** dicionário com a chave incrementada |
| `formatar_moeda`, `formatar_relatorio_multas` | `formatacao.py` | Transformam dados em texto, sem imprimir |

Os métodos `dias_de_atraso` e `esta_atrasado` de `Emprestimo` também são puros: o objeto é
imutável, então o resultado depende só dele e da data recebida.

### map, filter e reduce

- **filter**: `filtrar_livros_por_categoria`, `filtrar_emprestimos_ativos`,
  `filtrar_emprestimos_atrasados`, `filtrar_livros_disponiveis` e no relatório de multas
- **map**: no relatório (cada empréstimo atrasado vira um `ItemMulta`), em
  `identificadores_de_livros_emprestados` e na formatação
- **reduce**: soma das multas no relatório e contagens das estatísticas
  (`contar_livros_por_categoria` e `contar_emprestimos_por_usuario`)

### Relatório de multas

```
Biblioteca.relatorio_multas(data)          impura: lê o estado atual da biblioteca
  └─ gerar_relatorio_multas(emprestimos, data)          pura
       ├─ filter(esta_atrasado)            empréstimos ativos e atrasados
       ├─ map(criar_item_multa)            ItemMulta com dias e valor (usa calcular_multa)
       └─ reduce(soma + item.valor)        total das multas
     → RelatorioMultas(data_referencia, itens, total)   objeto imutável
formatar_relatorio_multas(relatorio)       pura: monta o texto
print(...)                                 impura: saída no terminal (main.py)
```

### Imutabilidade

- Entidades congeladas (`frozen=True`): devolver um livro **não altera** o empréstimo original;
  `com_devolucao` usa `dataclasses.replace` e cria um novo objeto.
- As funções recebem coleções e retornam **novas** tuplas, sem modificar a entrada.
- As contagens das estatísticas criam um dicionário novo a cada passo do `reduce`
  (`{**contagem, chave: valor + 1}`) e são retornadas como `MappingProxyType` (somente leitura).
- Os resultados (`ItemMulta`, `RelatorioMultas`, `Estatisticas`) também são `frozen`.
- Valores em dinheiro usam `Decimal`, evitando erros de arredondamento de `float`.

### Separação entre puro e impuro

| Impuro (efeitos colaterais) | Puro |
|---|---|
| `Biblioteca.cadastrar_*`, `registrar_emprestimo`, `registrar_devolucao`: alteram o estado da biblioteca | `funcional.py`, `relatorios.py`, `estatisticas.py`, `paradigmas.py`, `formatacao.py` |
| Geração de identificadores sequenciais dentro da `Biblioteca` | Métodos de consulta das entidades imutáveis |
| `main.py`: leitura de argumentos e `print` | |

Os métodos de consulta da `Biblioteca` apenas repassam uma cópia do estado atual para as funções
puras; toda a lógica de cálculo fica fora da classe.

## Comparação entre paradigmas

`paradigmas.py` calcula o **total de multas** de duas formas, e os testes garantem que o resultado
é o mesmo para várias datas:

- `calcular_total_multas_imperativo`: laço `for`, `if` e um acumulador `total` que é alterado a
  cada volta.
- `calcular_total_multas_funcional`: `filter` (atrasados) → `map` (multa de cada um) → `reduce`
  (soma), sem variável alterada.

A versão funcional reaproveita as regras já testadas (`esta_atrasado`, `calcular_multa`) e descreve
*o que* é calculado; a imperativa repete a regra de atraso dentro do laço e descreve *como* calcular.

## Empréstimos simultâneos

Se dois usuários tentarem emprestar o mesmo livro ao mesmo tempo, as duas operações podem verificar
a disponibilidade antes de qualquer uma registrar o empréstimo (condição de corrida). Funções puras
e imutabilidade não resolvem isso sozinhas, porque o problema está no estado compartilhado da
`Biblioteca`. Por isso as operações que alteram o estado usam um `threading.Lock`: a verificação e
o registro acontecem juntos, de forma atômica. O teste
`test_emprestimos_simultaneos_do_mesmo_livro_geram_apenas_um_emprestimo` dispara 8 threads ao mesmo
tempo e confirma que só um empréstimo é criado.

## Exemplo de saída

```
6. Relatório de multas (filter → map → reduce)
==============================================
Data de referência: 23/11/2026
#1 Dom Casmurro (Ana Souza): 20 dia(s) × R$ 2,00 = R$ 40,00
#2 Código Limpo (Bruno Lima): 8 dia(s) × R$ 2,00 = R$ 16,00
#6 Entendendo Algoritmos (Carla Mendes): 4 dia(s) × R$ 2,00 = R$ 8,00
Total das multas: R$ 64,00
```
