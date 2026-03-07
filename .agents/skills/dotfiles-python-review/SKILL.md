---
name: dotfiles-python-review
description: Revisar mudancas Python do repo com foco em corretude, portabilidade Windows/WSL, typing, cobertura de validacao e qualidade de manutencao. Use quando a tarefa tocar scripts Python, testes Python, hooks Python ou pyproject.
---

# dotfiles-python-review

## Objetivo

Atuar como revisor tecnico de codigo Python do repo.

## Fluxo

1. Ler o diff Python e mapear impacto funcional e de runtime.
2. Verificar imports, caminhos, side effects, contracts de CLI e tratamento de erro.
3. Revisar portabilidade Windows/WSL, coesao e testabilidade.
4. Conferir se a rodada acionou Pascoalete para textos, docs, mensagens,
   comentarios e identificadores legiveis alterados.
5. Exigir validacoes Python coerentes com o escopo antes da aprovacao.

## Regras

- Nao aprovar mudanca Python sem revisar lint, formatacao, typing e testes.
- Nao aceitar path hardcoded ou contrato de script ambíguo.
- Priorizar clareza, modularidade e cobertura de regressao.
- Sempre incluir `cspell` via `task spell:review` quando a mudanca alterar
  textos, comentarios, docs, help ou mensagens legiveis ao usuario.

## Entregas esperadas

- parecer de revisao Python
- riscos objetivos
- lista de validacoes obrigatorias

## Validacao

- `task lint:python`
- `task format:python:check`
- `task type:check`
- `task test:unit:python`
- `task spell:review`

## Referencias

- [`references/checklist.md`](references/checklist.md)
- [`../../../pyproject.toml`](../../../pyproject.toml)
- [`../../../tests/python/`](../../../tests/python/)
- [`../../../docs/AI-ORTHOGRAPHY-LEDGER.md`](../../../docs/AI-ORTHOGRAPHY-LEDGER.md)
