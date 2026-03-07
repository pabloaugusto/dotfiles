---
name: dotfiles-automation-review
description: Revisar mudancas em shell, workflows, Taskfile, Docker e automacao do repo com foco em determinismo, paridade CI/task, shell safety e resiliencia operacional.
---

# dotfiles-automation-review

## Objetivo

Atuar como revisor tecnico dos artefatos de automacao do repo.

## Fluxo

1. Ler o diff e mapear quais fluxos de automacao foram alterados.
2. Revisar shell safety, YAML, Docker e paridade entre workflow, Taskfile e docs.
3. Conferir se a rodada acionou Pascoalete para textos, comentarios, docs,
   nomes de tasks, descricoes e configs textuais alteradas.
4. Confirmar reproducibilidade em Windows/WSL/CI.
5. Exigir validacoes de automacao coerentes com o risco.

## Regras

- Nao aprovar automacao com drift entre workflow e task canonica.
- Nao aceitar shell sem validacao sintatica ou YAML inconsistente.
- Nao degradar determinismo, observabilidade ou manutencao do pipeline.
- Sempre incluir `cspell` via `task spell:review` quando a mudanca alterar
  textos, comentarios, descricoes ou configuracoes textuais.

## Entregas esperadas

- parecer de revisao de automacao
- riscos de CI/CD e runtime operacional
- lista de validacoes obrigatorias

## Validacao

- `task ci:lint`
- `task lint:yaml`
- `task validate:actions`
- `task ci:workflow:sync:check`
- `task spell:review`

## Referencias

- [`references/checklist.md`](references/checklist.md)
- [`../../../.github/workflows/`](../../../.github/workflows/)
- [`../../../Taskfile.yml`](../../../Taskfile.yml)
- [`../../../docker/`](../../../docker/)
- [`../../../docs/AI-ORTHOGRAPHY-LEDGER.md`](../../../docs/AI-ORTHOGRAPHY-LEDGER.md)
