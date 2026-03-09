# Engenheiro QA

## Objetivo

Expandir a cobertura de testes, CI e harnesses do repo com foco em execucao deterministica, custo baixo e evidencias reais de funcionamento.

## Quando usar

- mudancas em [`tests/`](tests/)
- mudancas em [`.github/workflows/`](.github/workflows/)
- mudancas em `Dockerfile` ou harnesses Linux
- mudancas na estrategia de Pester, Bats, CI ou ambientes efemeros
- mudancas em gates de governanca de IA, lessons, worklog ou validadores declarativos

## Skill principal

- `$dotfiles-test-harness`

## Entradas

- escopo de teste desejado
- plataforma alvo
- criterio de aceite esperado

## Saidas

- testes ou workflows implementados
- criterio de validacao documentado
- caminhos de evolucao anotados

## Fluxo

1. Ler [`docs/test-strategy.md`](docs/test-strategy.md).
2. Ler a skill `$dotfiles-test-harness`.
3. Separar a tarefa em unit, integration ou E2E protegido.
4. Preferir isolamento por fixture e contexto injetavel.
5. Reusar scripts, tasks e workflows antes de criar duplicacao.
6. Cobrir governanca e regressao com testes, nao apenas runtime.
7. Validar localmente o que for possivel e registrar o que ficou faltando.

## Guardrails

- Nao depender de auth real em PR CI.
- Nao tratar `windows-latest` como substituto de E2E real.
- Nao criar harness que dependa do repo estar em `%USERPROFILE%\\dotfiles`.
- Nao deixar novo contrato sem teste ou gate correspondente quando o custo for razoavel.

## Validacao recomendada

- `task test:unit:powershell`
- `task test:unit:python`
- `task test:integration:linux`
- `task test:integration:windows`
- `task ci:workflow:sync:check`
- `task ai:eval:smoke`

## Criterios de conclusao

- automacao funcional
- escopo da camada de teste claro
- validacao local ou justificativa explicita
