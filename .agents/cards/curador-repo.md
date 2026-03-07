# Curador Repo

## Objetivo

Manter convencoes operacionais, higiene de versionamento e organizacao de prompts, skills, docs e automacoes deste repo.

## Quando usar

- mudancas em `AGENTS.md`
- mudancas em `.agents/`, `.codex/README.md`, `docs/TASKS.md` ou `docs/WORKFLOWS.md`
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
3. Quando houver reuso ou adaptacao de outro repo, concluir auditoria estrutural exaustiva e registrar o gap analysis em `docs/AI-SOURCE-AUDIT.md`.
4. Manter `.agents/` como fonte canonica e os catalogos/docs em paridade com essa estrutura.
5. Manter `Taskfile.yml`, `.github/workflows/`, `docs/TASKS.md` e `docs/WORKFLOWS.md` em sincronismo.
6. Consolidar a menor regra que resolva o problema sem criar burocracia ociosa.
7. Encaminhar runtime local para `.gitignore` quando nao for portavel nem declarativo.
8. Automatizar a verificacao sempre que o custo for baixo.
9. Preferir commits checkpoint por rodada para evitar acumulacao de contextos nao commitados.

## Guardrails

- Nao versionar estado de runtime local.
- Nao criar documentacao paralela para o mesmo contrato.
- Nao espalhar naming rules sem validacao automatica correspondente.
- Nao importar regras de outro repo por amostragem.
- Nao permitir que `.codex/` volte a acumular contratos declarativos; a fonte de verdade e `.agents/`.
- Nao deixar `LICOES-APRENDIDAS.md` fora do fluxo de fechamento e validacao.
- Nao permitir que rodadas concluidas se acumulem sem commit checkpoint quando a worktree estiver dirty.

## Validacao recomendada

- `task ai:validate`
- `task ai:eval:smoke`
- `task ci:workflow:sync:check`
- `task conventions:check:branch`
- `task conventions:check:pr-title TITLE="✨ feat(repo): exemplo"`

## Criterios de conclusao

- regra clara
- fonte de verdade unica
- automacao minima aplicada
- auditoria versionada quando houver fonte cross-repo
