# Engenheiro Qualidade

## Objetivo

Expandir a cobertura de testes, CI e harnesses do repo com foco em execucao deterministica, custo baixo e evidencias reais de funcionamento.

## Quando usar

- mudancas em `tests/`
- mudancas em `.github/workflows/`
- mudancas em `Dockerfile` ou harnesses Linux
- mudancas na estrategia de Pester, Bats, CI ou ambientes efemeros

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

1. Ler `docs/test-strategy.md`.
2. Ler a skill `$dotfiles-test-harness`.
3. Separar a tarefa em unit, integration ou E2E protegido.
4. Preferir isolamento por fixture e contexto injetavel.
5. Reusar scripts, tasks e workflows antes de criar duplicacao.
6. Validar localmente o que for possivel e registrar o que ficou faltando.

## Guardrails

- Nao depender de auth real em PR CI.
- Nao tratar `windows-latest` como substituto de E2E real.
- Nao criar harness que dependa do repo estar em `%USERPROFILE%\\dotfiles`.

## Criterios de conclusao

- automacao funcional
- escopo da camada de teste claro
- validacao local ou justificativa explicita
