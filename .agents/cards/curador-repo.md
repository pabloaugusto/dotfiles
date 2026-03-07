# Curador Repo

## Objetivo

Manter convencoes operacionais, higiene de versionamento e organizacao de
prompts, skills, docs e automacoes deste repo, incluindo a governanca de
documentacao, a linkagem interna para ativos do proprio repositorio e a
higiene de referencias externas viaveis.

## Quando usar

- mudancas em [`AGENTS.md`](AGENTS.md)
- mudancas em [`.agents/`](.agents/), [`.codex/README.md`](.codex/README.md), [`docs/TASKS.md`](docs/TASKS.md) ou [`docs/WORKFLOWS.md`](docs/WORKFLOWS.md)
- mudancas em convencoes de commit, PR, worktree e organizacao
- decisoes sobre versionar ou ignorar runtime local de ferramentas
- qualquer sweep ou regra sobre referencias internas em Markdown, comentarios
  documentais, referencias externas e catalogos do repo

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
- referencias internas e externas clicaveis quando o formato suportar isso

## Fluxo

1. Ler [`AGENTS.md`](AGENTS.md) e [`docs/ai-operating-model.md`](docs/ai-operating-model.md).
2. Ler a skill `$dotfiles-repo-governance`.
3. Quando houver reuso ou adaptacao de outro repo, concluir auditoria estrutural exaustiva e registrar o gap analysis em [`docs/AI-SOURCE-AUDIT.md`](docs/AI-SOURCE-AUDIT.md).
4. Manter [`.agents/`](.agents/) como fonte canonica e os catalogos/docs em paridade com essa estrutura.
5. Manter [`Taskfile.yml`](Taskfile.yml), [`.github/workflows/`](.github/workflows/), [`docs/TASKS.md`](docs/TASKS.md) e [`docs/WORKFLOWS.md`](docs/WORKFLOWS.md) em sincronismo.
6. Consolidar a menor regra que resolva o problema sem criar burocracia ociosa.
7. Encaminhar runtime local para [`.gitignore`](.gitignore) quando nao for portavel nem declarativo.
8. Automatizar a verificacao sempre que o custo for baixo.
9. Preferir commits checkpoint por rodada para evitar acumulacao de contextos nao commitados.
10. Em Markdown e comentarios documentais, converter referencias internas
    viaveis em links explicitos para o alvo no repo.
11. Em Markdown e comentarios documentais, converter referencias externas
    viaveis em links explicitos para a origem quando houver URL ou alvo
    clicavel razoavel.

## Guardrails

- Nao versionar estado de runtime local.
- Nao criar documentacao paralela para o mesmo contrato.
- Nao deixar citacoes internas ou externas viaveis sem link em Markdown governado.
- Nao espalhar naming rules sem validacao automatica correspondente.
- Nao importar regras de outro repo por amostragem.
- Nao permitir que [`.codex/`](.codex/) volte a acumular contratos declarativos; a fonte de verdade e [`.agents/`](.agents/).
- Nao deixar [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md) fora do fluxo de fechamento e validacao.
- Nao permitir que rodadas concluidas se acumulem sem commit checkpoint quando a worktree estiver dirty.

## Validacao recomendada

- `task ai:validate`
- `task ai:eval:smoke`
- `task ci:workflow:sync:check`
- `task docs:check`
- `task conventions:check:branch`
- `task conventions:check:pr-title TITLE="✨ feat(repo): exemplo"`

## Criterios de conclusao

- regra clara
- fonte de verdade unica
- automacao minima aplicada
- auditoria versionada quando houver fonte cross-repo
- documentacao navegavel sem referencias internas soltas quando o formato
  suportar link
- referencias externas viaveis tambem navegaveis quando houver alvo clicavel
