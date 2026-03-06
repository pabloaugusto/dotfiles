---
name: dotfiles-repo-governance
description: Aplicar convencoes operacionais, higiene de versionamento, prompts, skills e regras de manutencao deste repo de dotfiles. Use quando a tarefa tocar `AGENTS.md`, `ai/`, naming de commit/PR, worktrees, organizacao de docs, `.gitignore` ou decisao sobre versionar arquivos locais de ferramentas.
---

# Dotfiles Repo Governance

## Objetivo

Guiar mudancas de governanca do repo sem burocracia excessiva e com automacao minima suficiente para evitar drift.

## Fluxo

1. Ler `AGENTS.md` e `docs/ai-operating-model.md`.
2. Ler `references/conventions.md` desta skill.
3. Consolidar a menor regra que resolva o problema sem abrir excecoes opacas.
4. Quando uma regra merecer permanencia, automatizar sua verificacao.
5. Tratar runtime local de ferramentas como nao versionavel, salvo excecao declarativa e portavel.

## Regras

- Commits e PRs seguem `emoji + conventional commits`.
- Branches seguem naming limpo, sem emoji.
- Skills e prompts devem ser curtos, especificos e versionados.
- Estado local de ferramenta nao entra no Git.
- Workflows, tasks e docs precisam apontar para a mesma regra.

## Validacao minima

- `task conventions:check:pr-title TITLE="..."` quando a regra tocar naming
- `task ai:validate`
- workflow de governanca quando o escopo tocar `AGENTS.md`, `ai/` ou `.gitignore`

## Referencias

- `references/conventions.md`
