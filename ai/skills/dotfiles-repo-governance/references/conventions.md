# Conventions

## Naming

- commit: `emoji + conventional commit`
- PR title: mesmo padrao do commit
- branch: sem emoji

## Fonte de verdade

- `AGENTS.md` para guardrails globais
- `docs/ai-operating-model.md` para politica de IA
- `docs/git-conventions.md` para naming
- `Taskfile.yml` e workflows para validacao automatica

## Runtime local

Nao versionar:

- `.codex/`
- `.gemini/`
- `.agents/`
- caches, sessoes, sqlite, browser profile, auth e tokens
