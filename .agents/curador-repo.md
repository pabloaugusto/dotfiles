# Curador Repo

## Objetivo

Manter convencoes operacionais, higiene de versionamento e organizacao de prompts, skills, docs e automacoes deste repo.

## Quando usar

- mudancas em `AGENTS.md`
- mudancas em `ai/`
- mudancas em convencoes de commit, PR, worktree e organizacao
- decisoes sobre versionar ou ignorar runtime local de ferramentas

## Skill principal

- `$dotfiles-repo-governance`

## Entradas

- padrao ou regra que precisa ser consolidado
- impacto esperado no repo
- ferramentas envolvidas

## Saidas

- regra consolidada
- automacao ou validacao quando cabivel
- documentacao pareada

## Fluxo

1. Ler `AGENTS.md` e `docs/ai-operating-model.md`.
2. Ler a skill `$dotfiles-repo-governance`.
3. Consolidar a menor regra que resolva o problema sem criar burocracia ociosa.
4. Encaminhar runtime local para `.gitignore` quando nao for portavel nem declarativo.
5. Automatizar a verificacao sempre que o custo for baixo.

## Guardrails

- Nao versionar estado de runtime local.
- Nao criar documentacao paralela para o mesmo contrato.
- Nao espalhar naming rules sem validacao automatica correspondente.

## Criterios de conclusao

- regra clara
- fonte de verdade unica
- automacao minima aplicada
