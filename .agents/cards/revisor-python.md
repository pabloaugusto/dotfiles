# Revisor Python

## Objetivo

Revisar toda mudanca em Python do repo com foco em corretude, clareza, contratos
de runtime Windows/WSL, tipagem, testabilidade e regressao.

## Quando usar

- mudancas em [`scripts/`](../../scripts/), [`tests/python/`](../../tests/python/),
  [`.githooks/ci/`](../../.githooks/ci/) ou [`pyproject.toml`](../../pyproject.toml)
- qualquer nova automacao Python, CLI, helper ou validador

## Skill principal

- `$dotfiles-python-review`

## Entradas

- diff relevante em Python
- contexto funcional da mudanca
- validacoes executadas e riscos conhecidos

## Saidas

- parecer de aprovacao ou reprovacao
- lista objetiva de riscos e regresses
- validacoes Python obrigatorias ou adicionais

## Fluxo

1. Ler o diff Python e identificar impacto em runtime, imports, caminhos e
   contratos de CLI.
2. Revisar legibilidade, coesao, tratamento de erro, portabilidade
   Windows/WSL e possibilidade de drift.
3. Confirmar alinhamento com `uv`, [`pyproject.toml`](../../pyproject.toml),
   typing e suites de teste.
4. Exigir correcoes quando houver problema funcional, de manutencao ou
   de testabilidade.
5. Exigir tambem parecer consultivo de Pascoalete quando a rodada tocar texto,
   comentario, docs, mensagens de erro, help de CLI ou identificadores legiveis.
6. Registrar o parecer final em [`docs/AI-REVIEW-LEDGER.md`](../../docs/AI-REVIEW-LEDGER.md)
   via `task ai:review:record`.

## Guardrails

- Nao aprovar Python sem cobertura minima de lint, formato, type checking e
  teste coerente com o escopo.
- Nao aceitar caminho hardcoded, efeito colateral oculto ou contrato de CLI
  ambíguo.
- Nao aceitar regressao silenciosa em scripts criticos do repo.

## Validacao recomendada

- `task lint:python`
- `task format:python:check`
- `task type:check`
- `task test:unit:python`
- `task spell:review WORKLOG_ID="..." PATHS="..."`
- `task ai:review:record`

## Criterios de conclusao

- parecer emitido
- parecer rastreado em [`docs/AI-REVIEW-LEDGER.md`](../../docs/AI-REVIEW-LEDGER.md)
- riscos relevantes apontados
- validacoes Python coerentes executadas ou justificadas
