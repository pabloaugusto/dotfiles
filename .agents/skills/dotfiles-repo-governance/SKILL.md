---
name: dotfiles-repo-governance
description: Aplicar convencoes operacionais, higiene de versionamento, prompts, skills, agents, catalogos, rules e regras de manutencao deste repo de dotfiles. Use quando a tarefa tocar [`AGENTS.md`](AGENTS.md), [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md), [`.agents/`](.agents/), [`.codex/README.md`](.codex/README.md), naming de commit/PR, worktrees, organizacao de docs, [`.gitignore`](.gitignore) ou decisao sobre versionar arquivos locais de ferramentas.
---

# Dotfiles Repo Governance

## Objetivo

Guiar mudancas de governanca do repo sem burocracia excessiva e com automacao minima suficiente para evitar drift.

## Fluxo

1. Ler [`AGENTS.md`](AGENTS.md), [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md) e [`docs/ai-operating-model.md`](docs/ai-operating-model.md).
2. Ler [`references/conventions.md`](references/conventions.md) desta skill.
3. Se houver reuso ou importacao de outro repo, concluir auditoria estrutural exaustiva e registrar o resultado em [`docs/AI-SOURCE-AUDIT.md`](docs/AI-SOURCE-AUDIT.md).
4. Consolidar a menor regra que resolva o problema sem abrir excecoes opacas.
5. Quando uma regra merecer permanencia, automatizar sua verificacao.
6. Manter [`.agents/`](.agents/) como fonte canonica e os catalogos, docs e gates em paridade com essa arvore.
7. Tratar runtime local de ferramentas como nao versionavel, salvo excecao declarativa e portavel.

## Regras

- Commits e PRs seguem `emoji + conventional commits`.
- Branches seguem naming limpo, sem emoji.
- Skills e prompts devem ser curtos, especificos e versionados.
- Estado local de ferramenta nao entra no Git.
- Workflows, tasks e docs precisam apontar para a mesma regra.
- Em Markdown e comentarios documentais, referencias internas viaveis ao repo e
  referencias externas viaveis devem ser links explicitos para o alvo.
- Importacao cross-repo sem auditoria completa e proibida.
- [`.codex/`](.codex/) no repo deve permanecer apenas como ponte de compatibilidade.
- [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md) tambem e contrato operacional e nao pode ficar fora do fluxo de fechamento.

## Entregas esperadas

- contratos e catalogos em paridade
- regra consolidada com fonte de verdade unica
- validacao automatica correspondente quando o custo for razoavel

## Validacao

- `task conventions:check:pr-title TITLE="..."` quando a regra tocar naming
- `task ai:validate`
- `task ai:eval:smoke`
- `task ci:workflow:sync:check`
- `task docs:check`
- `task ai:lessons:check`
- workflow de governanca quando o escopo tocar [`AGENTS.md`](AGENTS.md), [`.agents/`](.agents/), [`.codex/README.md`](.codex/README.md), [`docs/TASKS.md`](docs/TASKS.md), [`docs/WORKFLOWS.md`](docs/WORKFLOWS.md) ou [`.gitignore`](.gitignore)
- auditoria versionada atualizada quando houver importacao ou adaptacao de outro repo

## Referencias

- [`references/conventions.md`](references/conventions.md)
