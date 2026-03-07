# Conventions

## Naming

- commit: `emoji + conventional commit`
- PR title: mesmo padrao do commit
- branch: sem emoji

## Fonte de verdade

- [`AGENTS.md`](AGENTS.md) para guardrails globais
- [`docs/ai-operating-model.md`](docs/ai-operating-model.md) para politica de IA
- [`docs/git-conventions.md`](docs/git-conventions.md) para naming
- [`Taskfile.yml`](Taskfile.yml) e workflows para validacao automatica

## Runtime local

Nao versionar:

- `.gemini/`
- runtime local fora da arvore canonica [`.agents/`](.agents/)
- caches, sessoes, sqlite, browser profile, auth e tokens
