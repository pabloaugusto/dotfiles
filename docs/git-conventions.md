# Git Conventions

Este repo adota governanca obrigatoria para:

- commits
- titulos de PR
- nomes de branch
- hooks locais
- validacoes de CI

Fonte de verdade tecnica:

- [`.githooks/conventional_emoji.py`](../.githooks/conventional_emoji.py)

## Commits e PR titles

Formato obrigatorio:

```text
<emoji> <type>(<scope opcional>): <jira-key> <descricao>
```

Regras obrigatorias:

- emoji semantico obrigatorio
- `type` precisa existir na biblioteca oficial do repo
- `scope` e opcional, mas recomendado quando melhora clareza
- quando o diff tocar [`.agents/prompts/`](../.agents/prompts/), `scope`
  passa a ser obrigatorio e deve ser `prompt`
- o subject precisa carregar uma unica chave Jira real
- titulo/subject com maximo recomendado de `72` caracteres
- descricao curta, objetiva e sem ponto final
- commit e PR title seguem exatamente o mesmo contrato
- cada commit deve representar uma unica **issue** Jira real
- quando possivel, cada commit deve ser auto-testavel

Exemplos validos:

```text
✨ feat(test-harness): DOT-81 add branch and commit validators
📝 docs(prompt): DOT-179 document prompt namespace governance
🐛 fix(bootstrap): DOT-24 preserve canonical projects path
📝 docs(git): DOT-130 document semantic Jira policy
♻️ refactor(taskfile): DOT-130 split governance checks by platform
✅ test(python): DOT-130 cover git governance validator
💚 ci(github): DOT-117 validate PR title and commit range
🔧 chore(hooks): DOT-130 install local git hooks path
```

## Biblioteca de tipos e emojis

| Type | Emoji | Uso esperado |
| --- | --- | --- |
| `feat` | `✨` | nova funcionalidade |
| `fix` | `🐛` | correcao de bug |
| `docs` | `📝` | documentacao |
| `style` | `💄` | estilo visual/formatacao sem mudanca logica |
| `refactor` | `♻️` | refactor sem mudar comportamento esperado |
| `perf` | `⚡` | melhoria de performance |
| `test` | `✅` | testes |
| `build` | `👷` | build, empacotamento ou tooling de build |
| `ci` | `💚` | workflow, CI/CD e checks automatizados |
| `chore` | `🔧` | manutencao geral |
| `revert` | `⏪` | reversao |
| `wip` | `🚧` | trabalho em progresso controlado |
| `hotfix` | `🚑` | correcao urgente |
| `security` | `🔒` | hardening e seguranca |
| `deps` | `⬆️` | atualizacao de dependencias |
| `i18n` | `🌐` | internacionalizacao/localizacao |
| `init` | `🎉` | inicializacao de projeto/fluxo |
| `release` | `🔖` | release e versionamento |
| `merge` | `🔀` | fluxo controlado de merge |

## Branches

Branches nao usam emoji.

Formato obrigatorio:

```text
<type>/<jira-key>-<slug>
```

Tipos aceitos para branch:

- `feat`
- `fix`
- `docs`
- `prompt`
- `refactor`
- `perf`
- `test`
- `ci`
- `chore`
- `build`
- `hotfix`
- `deps`
- `security`
- `i18n`
- `wip`
- `init`
- `release`

Exemplos validos:

```text
feat/DOT-81-test-harness-hybrid
prompt/DOT-179-agnostic-sync-outbox-foundation
fix/DOT-24-windows-relink-regression
docs/DOT-130-bootstrap-config-reference
refactor/DOT-130-bootstrap-path-normalization
release/DOT-130-governance-foundation
```

Excecoes aceitas:

- `dependabot/*`
- `renovate/*`
- branches legadas pre-integracao com Jira so permanecem enquanto trilha historica; retomada nova deve nascer de `main` no padrao canonico

## Regra de contexto

- cada branch deve carregar um unico contexto coerente
- nao misturar temas independentes na mesma branch
- commits devem ser pequenos, semanticamente coesos e ligados a uma unica **issue**
- quando a rodada tocar [`.agents/prompts/`](../.agents/prompts/), a branch deve
  usar tipo `prompt`, commit/`PR title` devem usar `scope` `prompt` e a issue
  Jira dona deve usar titulo `PROMPT: ...` com label `prompt`
- quando a demanda antiga precisar ser retomada, abrir branch nova a partir de `main`, salvo evidencia objetiva de que a branch anterior ainda e a trilha correta
- apos merge ou absorcao em `main`, podar branches e worktrees desnecessarias o quanto antes

## Validacao local

Instalar hooks do repo:

```bash
task conventions:hooks:install
```

Validacoes manuais:

```bash
task conventions:check:branch
task conventions:check:commit
task conventions:check:commits
task pr:title:check TITLE="✨ feat(git): DOT-130 add governance"
task git:governance:check
```

## CI

O repo valida automaticamente:

- PR title
- branch name
- commits do PR
- chave Jira unica em commit e PR
- subjects no range de push para `main`
- testes unitarios Python da governanca
- close gate de WIP de IA quando aplicavel

## Hooks locais

Os hooks em [`.githooks/`](.githooks/) aplicam:

- injecao automatica de emoji semantico no commit local
- validacao do subject no `commit-msg`
- bloqueio de push direto para branches protegidas no `pre-push`
- validacao local do titulo do PR aberto, quando `gh` estiver autenticado

## Motivo

Essas convencoes deixam historico, changelog, revisao e automacao mais previsiveis e com menos drift entre humano, hooks locais e GitHub Actions.
