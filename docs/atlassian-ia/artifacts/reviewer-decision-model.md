# Reviewer decision model

Artefato canonico do modelo de decisao usado pelos reviewers especializados.
Ele complementa o catalogo de standards em
[`reviewer-standards-catalog.md`](reviewer-standards-catalog.md) e define como
um reviewer deixa de ser apenas um comentador e passa a operar como sistema
formal de decisao tecnica.

A fonte declarativa correspondente fica em
[`../../../config/ai/reviewer-policies.yaml`](../../../config/ai/reviewer-policies.yaml).
O schema portavel da saida estruturada fica em
[`../../../config/ai/review-output.schema.json`](../../../config/ai/review-output.schema.json).

## Principio central

Um reviewer especializado nao existe para deixar um comentario generico de PR.
Ele existe para responder, com base em evidencias:

- o que esta correto
- o que falhou
- por que falhou
- qual e o impacto
- qual e a melhor correcao
- o que bloqueia
- o que pode virar backlog tecnico
- se houve regressao de performance, I/O ou eficiencia
- qual decisao tomar
- qual comentario publicar no Jira
- para qual status a issue deve ser movida

## Missao operacional

Cada reviewer especializado atua como:

- reviewer tecnico
- quality gate
- parecerista auditavel
- executor de workflow no Jira

Isso significa que ele nao apenas opina. Ele:

- classifica severidade
- toma decisao
- recomenda correcao
- diferencia blocker de debt
- sustenta o handoff ou retorno do fluxo

## Blocos estruturais do modelo

### 1. Prompt base unico com policies variaveis

Em vez de dezenas de prompts desconectados, o modelo ideal usa uma base comum e
liga policies especificas por especialidade. Isso reduz drift e facilita
avaliacao sistematica.

### 2. Tools pequenas com contrato claro

O reviewer precisa de ferramentas pequenas, com input e output explicitos, para:

- ler diff e arquivos
- executar lint, testes e checagens
- comentar no Jira
- transicionar issue

Esse desenho se alinha a:

- [OpenAI function calling](https://platform.openai.com/docs/guides/function-calling)
- [OpenAI structured outputs](https://platform.openai.com/docs/guides/structured-outputs)

### 3. Saida estruturada e avaliavel

O parecer precisa sair em forma estruturada, para permitir:

- evals
- auditoria
- replay
- analytics por severidade e categoria

### 4. Integracao governada

O reviewer deve operar conectado a:

- repositorio
- policies
- docs
- Jira
- Confluence

Protocolos como `MCP` ou camada equivalente ajudam a manter tools, resources,
logging e reporting padronizados.

## Taxonomia de severidade

### Blocker

Impede aprovacao. Exemplos:

- bug funcional provavel
- falha de seguranca
- regressao seria de performance
- aumento critico de I/O
- perda de dados
- violacao arquitetural relevante

### Major

Normalmente exige correcao antes de avancar. Exemplos:

- piora relevante de eficiencia
- design fragil
- logging inadequado
- tipagem ruim em area central
- aumento de complexidade sem justificativa

### Minor

Melhoria recomendada sem bloquear.

### Backlog debt

Nao bloqueia agora, mas deve virar backlog tecnico rastreavel.

### Nit

Ajuste cosmetico ou de microclareza.

## Decisoes formais de review

- `approved`
- `approved_with_debt`
- `changes_required`
- `blocked`

Mapeamento padrao para workflow:

- `approved` -> `Done`
- `approved_with_debt` -> `Done`
- `changes_required` -> `Changes Requested`
- `blocked` -> `Paused`

## Perguntas obrigatorias de regressao

Todo reviewer deve perguntar:

- a mudanca ficou mais lenta?
- a mudanca introduziu mais I/O?
- a complexidade aumentou sem ganho proporcional?
- a seguranca piorou?
- a clareza piorou?
- a testabilidade piorou?
- a correcao trocou um bug atual por uma divida estrutural maior?

## Exemplo aplicado: reviewer Python

O perfil Python recebe alguns reforcos adicionais:

- typing como dimensao obrigatoria
- leitura de [`pyproject.toml`](../../../pyproject.toml) quando afetar a stack Python
- analise de `Any`, contratos de retorno e interfaces
- foco em subprocess, path traversal, segredos, hot paths e custo de I/O
- missao explicita de atuar como gate absoluto de qualidade Python
- postura formal de decisao, nao apenas de comentario

Dimensoes obrigatorias no caso Python:

- corretude
- seguranca
- performance
- eficiencia e I/O
- legibilidade
- manutenibilidade
- testabilidade
- observabilidade
- robustez
- convencoes
- typing

## Contrato de saida

O payload minimo do parecer precisa conter:

- `review_scope`
- `decision`
- `confidence`
- `summary`
- `findings`
- `quality_regression`
- `required_changes`
- `technical_debt_backlog`
- `validation_needed`
- `jira_action`

O contrato completo e portavel fica em
[`../../../config/ai/review-output.schema.json`](../../../config/ai/review-output.schema.json).

Cada finding precisa conter:

- `severity`
- `category`
- `title`
- `evidence`
- `impact`
- `best_fix`
- `blocking`

## Referencias oficiais relacionadas

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [OpenAI function calling](https://platform.openai.com/docs/guides/function-calling)
- [JSON Schema](https://json-schema.org/)
- [Python Language Reference](https://docs.python.org/3/reference/)
- [PEP 8](https://peps.python.org/pep-0008/)
- [PEP 20](https://peps.python.org/pep-0020/)
- [PEP 257](https://peps.python.org/pep-0257/)
- [PEP 484](https://peps.python.org/pep-0484/)

## Recomendacao para este projeto

Adotar o reviewer especializado como sistema formal de decisao tecnica, sempre
amarrado a:

- standards oficiais
- policy declarativa versionada
- comentario estruturado no Jira
- evidencia objetiva
- transicao coerente de status

## Pacote de artefatos recomendado

- blueprint por especialidade, como
  [`python-quality-review-agent.md`](python-quality-review-agent.md)
- standards catalog:
  [`reviewer-standards-catalog.md`](reviewer-standards-catalog.md)
- severity policy:
  [`reviewer-severity-policy.md`](reviewer-severity-policy.md)
- workflow Jira:
  [`reviewer-jira-workflow-policy.md`](reviewer-jira-workflow-policy.md)
- schema de saida:
  [`../../../config/ai/review-output.schema.json`](../../../config/ai/review-output.schema.json)

## Relacionados

- [`python-quality-review-agent.md`](python-quality-review-agent.md)
- [`reviewer-severity-policy.md`](reviewer-severity-policy.md)
- [`reviewer-jira-workflow-policy.md`](reviewer-jira-workflow-policy.md)
- [`reviewer-standards-catalog.md`](reviewer-standards-catalog.md)
- [`universal-engineering-standards-stack.md`](universal-engineering-standards-stack.md)
- [`agent-operations.md`](agent-operations.md)
