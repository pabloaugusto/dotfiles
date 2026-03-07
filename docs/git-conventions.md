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
<emoji> <type>(<scope opcional>): <descricao>
```

Regras obrigatorias:

- emoji semantico obrigatorio
- `type` precisa existir na biblioteca oficial do repo
- `scope` e opcional, mas recomendado quando melhora clareza
- titulo/subject com maximo recomendado de `72` caracteres
- descricao curta, objetiva e sem ponto final
- commit e PR title seguem exatamente o mesmo contrato

Exemplos validos:

```text
✨ feat(test-harness): add branch and commit validators
🐛 fix(bootstrap): preserve canonical projects path
📝 docs(git): document semantic emoji policy
♻️ refactor(taskfile): split conventions checks by platform
✅ test(python): cover conventional emoji validator
💚 ci(github): validate pr title and commit range
🔧 chore(hooks): install local git hooks path
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
<type>/<slug>
```

Tipos aceitos para branch:

- `feat`
- `fix`
- `docs`
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
feat/test-harness-hybrid
fix/windows-relink-regression
docs/bootstrap-config-reference
refactor/bootstrap-path-normalization
release/governance-foundation
```

Excecoes aceitas:

- `dependabot/*`
- `renovate/*`

## Regra de contexto

- cada branch deve carregar um unico contexto coerente
- nao misturar temas independentes na mesma branch
- commits devem ser pequenos e semanticamente coesos
- se o contexto mudar de forma relevante, abra outra branch

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
task pr:title:check TITLE="✨ feat(git): add governance"
```

## CI

O repo valida automaticamente:

- PR title
- branch name
- commits do PR
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
