# Dotfiles

Repositorio de dotfiles com bootstrap multiambiente para Windows host e Ubuntu
WSL, focado em repetibilidade, seguranca operacional, testes reais e governanca
de IA versionada.

## O que este repo entrega hoje

### Bootstrap e ambiente

- Bootstrap oficial para Windows host e Ubuntu WSL.
- Modos `new`, `refresh` e `relink`, incluindo reparo idempotente de links.
- Config central versionada por template em [`bootstrap/user-config.yaml.tpl`](bootstrap/user-config.yaml.tpl).
- Normalizacao de caminhos canonicos e sincronismo de artefatos derivados.
- Suporte a OneDrive no Windows com layout canonico, links de perfil e health
  check pos-bootstrap.
- `checkEnv` em PowerShell e Bash para validar auth, signer, SSH, Git, `op`,
  `gh`, `sops`, `age` e integracoes criticas.

### Operacao diaria do repo

- `task sync` como fluxo canonico de sincronizacao Git.
- Gate local Windows -> WSL com `task sync:wsl-gate`.
- Aliases canonicos por ambiente:
  - Unix/WSL em [`df/.aliases`](df/.aliases)
  - PowerShell em [`df/powershell/aliases.ps1`](df/powershell/aliases.ps1)
  - Git aliases em [`df/git/.gitconfig-base`](df/git/.gitconfig-base)
- Config Git por ambiente com overlays dedicados para Windows, Linux, WSL e
  devcontainer.

### Segredos, auth e seguranca

- Refs `op://...` como fonte de verdade para segredos.
- Runtime local cifrado em [`docs/secrets-and-auth.md`](docs/secrets-and-auth.md#runtime-env-local),
  materializado como `~/.env.local.sops`, sem plaintext versionado.
- Assinatura Git via SSH com 1Password signer.
- Modo humano e signer tecnico de automacao por worktree, ambos via SSH +
  1Password, com rotacao orientada por `op`/`gh`.
- Politica de seguranca documentada em [`SECURITY.md`](SECURITY.md) e [`docs/secrets-and-auth.md`](docs/secrets-and-auth.md).

### Qualidade, testes e CI/CD

- Toolchain Python gerenciada por `uv`, [`pyproject.toml`](pyproject.toml), [`uv.lock`](uv.lock) e
  [`.python-version`](.python-version).
- `.venv` segregada por plataforma para worktree compartilhada:
  - Windows: `.venv/windows`
  - Linux/WSL: `.venv/linux`
- Camada Python de qualidade com:
  - `ruff` para lint e formatacao
  - `ty` para type checking incremental
  - `pytest` com coverage para [`scripts/`](scripts/) e [`tests/python`](tests/python)
- Lint sintatico para PowerShell e shell scripts.
- Lint documental e estrutural com:
  - `pymarkdownlnt`
  - `yamllint`
  - `validate_docs.py`
- Validadores de tooling e seguranca com:
  - `actionlint` via wrapper pinado
  - `gitleaks` via wrapper pinado
- Suite unitaria em:
  - Pester para PowerShell
  - pytest para a stack Python de qualidade
  - unittest Python para governanca e automacao de IA
  - Bats para harnesses Linux
- Harnesses reais de integracao para `relink`:
  - Linux em container OCI
  - Windows em ambiente temporario real
- Pinagem declarativa de ferramentas auxiliares em
  [`config/tooling.releases.yaml`](config/tooling.releases.yaml).
- Spellcheck com `cspell` ja disponivel em task dedicada, ainda fora do gate
  canonico enquanto o dicionario tecnico PT-BR/EN e curado.
- Workflows ativos:
  - AI Governance
  - PR Validate
  - Quality Foundation
  - Bootstrap Integration
- Paridade formal entre workflows e tasks canonicas.

### Governanca de IA

- Fonte canonica da camada de IA em [`.agents/`](.agents/).
- Skills, cartoes, registry, orchestration, rules e evals versionados.
- Tracker de WIP, roadmap, decisions e licoes aprendidas.
- Gates para:
  - continuidade de worklog
  - revisao obrigatoria de licoes
  - sincronismo entre workflows, tasks e catalogos
  - smoke eval de roteamento e delegacao
- Convencoes de branch, PR e commit com `emoji + conventional commits`.

## Estrutura do repositorio

- [`bootstrap/`](bootstrap/): bootstrap, parser de config, scripts de provisionamento e guia
  operacional.
- [`df/`](df/): dotfiles e assets reais que vao para a maquina apos o bootstrap.
- [`.agents/`](.agents/): camada canonica de IA e governanca declarativa.
- [`docs/`](docs/): documentacao tecnica, catalogos operacionais e referencia.
- [`tests/`](tests/): suites de teste, harnesses e fixtures.
- [`scripts/`](scripts/): CLIs e validadores reutilizaveis do repo.
- [`config/`](config/): pinagem declarativa de ferramentas auxiliares e configuracoes de
  suporte ao repo.
- [`docker/`](docker/): harnesses e imagens auxiliares de integracao.
- [`archive/`](archive/): legado e historico que nao deve contaminar os caminhos ativos.

## Entrada rapida

### Bootstrap

Windows host:

```powershell
task bootstrap
```

Ubuntu WSL:

```bash
task bootstrap
```

Recriar links canonicos sem bootstrap completo:

```powershell
task bootstrap:relink
```

### Validacao de ambiente

```powershell
task env:check
task env:check SIGN_MODE=automation
task git:signing:status
task git:signing:mode:automation
```

### Sincronizacao entre ambientes

```powershell
task sync
task sync:wsl-gate
```

### Validacao local de qualidade

```powershell
task install:dev
task ci:quality
task ci:validate
task test:integration:windows
```

```bash
task install:dev
task ci:quality
task ci:validate
task test:integration:linux
```

## Config central do bootstrap

Arquivos principais:

- template versionado: [`bootstrap/user-config.yaml.tpl`](bootstrap/user-config.yaml.tpl)
- arquivo local ignorado documentado em [`docs/config-reference.md`](docs/config-reference.md#bootstrapuser-configyaml)
- template correspondente: [`bootstrap/user-config.yaml.tpl`](bootstrap/user-config.yaml.tpl)

Derivados sincronizados automaticamente:

- [`df/secrets/secrets-ref.yaml`](df/secrets/secrets-ref.yaml)
- [`bootstrap/secrets/.env.local.tpl`](bootstrap/secrets/.env.local.tpl)
- derivado local documentado em [`docs/secrets-and-auth.md`](docs/secrets-and-auth.md#ssh-agent-e-git-signing)

Principio atual:

- caminhos absolutos canonicos sao a fonte de verdade
- `_path` representa destino absoluto explicito
- `_dir` continua aceito por compatibilidade, mas nao e o formato preferido

## Tasks oficiais

O [`Taskfile.yml`](Taskfile.yml) e a interface oficial de automacao do projeto.

Grupos principais:

- operacao do repo: `sync`, `repo:*`, `env:check`
- signing Git por worktree: `git:signing:*`
- bootstrap: `bootstrap:*`
- qualidade e PR local: `ci:*`, `pr:*`, `test:*`
- governanca de IA: `ai:*`

Catalogos atualizados:

- [`docs/TASKS.md`](docs/TASKS.md)
- [`docs/WORKFLOWS.md`](docs/WORKFLOWS.md)

## Documentacao principal

Comece por estes arquivos:

- [`CONTEXT.md`](CONTEXT.md)
- [`docs/README.md`](docs/README.md)
- [`bootstrap/README.md`](bootstrap/README.md)
- [`docs/bootstrap-flow.md`](docs/bootstrap-flow.md)
- [`docs/config-reference.md`](docs/config-reference.md)
- [`docs/checkenv.md`](docs/checkenv.md)
- [`docs/test-strategy.md`](docs/test-strategy.md)
- [`tests/README.md`](tests/README.md)
- [`docs/ai-operating-model.md`](docs/ai-operating-model.md)
- [`SECURITY.md`](SECURITY.md)

## Estado atual da camada de IA

- [`.agents/`](.agents/) e a fonte canonica.
- [`.codex/README.md`](.codex/README.md) existe apenas como ponte de compatibilidade.
- Runtime local de assistentes, sessoes, caches, auth e historico nao entra no
  Git.

## Convenções operacionais

- Tasks e workflows devem permanecer em paridade.
- Toda rodada de IA precisa atualizar o worklog e fechar revisao de licoes.
- Commits e PRs seguem `emoji + conventional commits`.
- Branches seguem naming limpo, sem emoji.
