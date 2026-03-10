# AI Startup Governance Manifest

## Objetivo

Definir a fonte canonica de leitura obrigatoria para toda sessao de IA que
precise retomar o trabalho sem continuidade confiavel de contexto.

## Contrato perene

- toda retomada sem continuidade confiavel exige releitura integral deste
  manifest e dos arquivos textuais que ele resolve
- isso inclui queda de energia, travamento, limpeza de cache, limpeza de
  sessoes, troca de app, troca de modelo, troca de worktree ou qualquer perda
  de contexto verificavel
- e proibido operar nessas retomadas por amostragem, memoria parcial, suposicao
  ou presuncao
- ao tentar drenar uma worktree suja, a IA deve recalcular tambem o inventario
  de branches e worktrees abertas e cruzar cada trilha com o contexto Jira real
- arquivos binarios e efemeros de runtime ficam fora da leitura normativa

## Escopo canonico

### Raiz

- [`AGENTS.md`](../AGENTS.md)
- [`CONTEXT.md`](../CONTEXT.md)
- [`LICOES-APRENDIDAS.md`](../LICOES-APRENDIDAS.md)
- [`Taskfile.yml`](../Taskfile.yml)
- [`ROADMAP.md`](../ROADMAP.md)

### Control plane e contratos

- todos os arquivos em [`config/ai/`](../config/ai/)
- [`.jira/config.yml`](../.jira/config.yml)

### Agents, cards, registry e orquestracao

- [`.agents/config.toml`](../.agents/config.toml)
- todos os arquivos em [`.agents/orchestration/`](../.agents/orchestration/)
- todos os arquivos em [`.agents/registry/`](../.agents/registry/)
- todos os arquivos em [`.agents/cards/`](../.agents/cards/)

### Docs de governanca do repo

- todos os arquivos `AI-*` em [`docs/`](./)
- [`docs/TASKS.md`](./TASKS.md)
- [`docs/WORKFLOWS.md`](./WORKFLOWS.md)
- [`docs/git-conventions.md`](./git-conventions.md)
- [`docs/checkenv.md`](./checkenv.md)
- [`docs/secrets-and-auth.md`](./secrets-and-auth.md)
- [`docs/ROADMAP-DECISIONS.md`](./ROADMAP-DECISIONS.md)
- [`docs/test-strategy.md`](./test-strategy.md)
- [`docs/bootstrap-flow.md`](./bootstrap-flow.md)
- [`docs/config-reference.md`](./config-reference.md)
- [`docs/ai-operating-model.md`](./ai-operating-model.md)

### Jira, Confluence, agilidade e artifacts normativos

- todos os arquivos em [`docs/atlassian-ia/`](./atlassian-ia/)

### Git, hooks, PR e workflows de governanca

- todos os arquivos em [`.githooks/`](../.githooks/)
- [`.github/pull_request_template.md`](../.github/pull_request_template.md)
- [`.github/workflows/ai-governance.yml`](../.github/workflows/ai-governance.yml)
- [`.github/workflows/pr-validate.yml`](../.github/workflows/pr-validate.yml)
- [`.github/workflows/quality-foundation.yml`](../.github/workflows/quality-foundation.yml)
- [`.github/workflows/jira-deployment-marker.yml`](../.github/workflows/jira-deployment-marker.yml)

## Regra de manutencao

- quando nascer nova fonte normativa de operacao, ela precisa entrar neste
  manifest ou ficar explicitamente fora com justificativa
- este manifest lista classes canonicas de leitura; a resolucao final dos
  caminhos deve ser recalculada a cada startup ou restart
- atualizar este manifest faz parte da governanca; nao e opcional
