# Dotfiles

Repositorio de dotfiles com bootstrap multiambiente para Windows host e Ubuntu
WSL, focado em repetibilidade, seguranca operacional, testes reais e governanca
de IA versionada.

## O que este repo entrega hoje

### Bootstrap e ambiente

- Bootstrap oficial para Windows host e Ubuntu WSL.
- Modos `new`, `refresh` e `relink`, incluindo reparo idempotente de links.
- Config central versionada por template em `bootstrap/user-config.yaml.tpl`.
- Normalizacao de caminhos canonicos e sincronismo de artefatos derivados.
- Suporte a OneDrive no Windows com layout canonico, links de perfil e health
  check pos-bootstrap.
- `checkEnv` em PowerShell e Bash para validar auth, signer, SSH, Git, `op`,
  `gh`, `sops`, `age` e integracoes criticas.

### Operacao diaria do repo

- `task sync` como fluxo canonico de sincronizacao Git.
- Gate local Windows -> WSL com `task sync:wsl-gate`.
- Aliases canonicos por ambiente:
  - Unix/WSL em `df/.aliases`
  - PowerShell em `df/powershell/aliases.ps1`
  - Git aliases em `df/git/.gitconfig-base`
- Config Git por ambiente com overlays dedicados para Windows, Linux, WSL e
  devcontainer.

### Segredos, auth e seguranca

- Refs `op://...` como fonte de verdade para segredos.
- Runtime local cifrado em `~/.env.local.sops`, sem plaintext versionado.
- Assinatura Git via SSH com 1Password signer.
- Politica de seguranca documentada em `SECURITY.md` e `docs/secrets-and-auth.md`.

### Qualidade, testes e CI/CD

- Lint sintatico para PowerShell e shell scripts.
- Suite unitaria em:
  - Pester para PowerShell
  - unittest Python para governanca e automacao de IA
  - Bats para harnesses Linux
- Harnesses reais de integracao para `relink`:
  - Linux em container OCI
  - Windows em ambiente temporario real
- Workflows ativos:
  - AI Governance
  - PR Validate
  - Quality Foundation
  - Bootstrap Integration
- Paridade formal entre workflows e tasks canonicas.

### Governanca de IA

- Fonte canonica da camada de IA em `.agents/`.
- Skills, cartoes, registry, orchestration, rules e evals versionados.
- Tracker de WIP, roadmap, decisions e licoes aprendidas.
- Gates para:
  - continuidade de worklog
  - revisao obrigatoria de licoes
  - sincronismo entre workflows, tasks e catalogos
  - smoke eval de roteamento e delegacao
- Convencoes de branch, PR e commit com `emoji + conventional commits`.

## Estrutura do repositorio

- `bootstrap/`: bootstrap, parser de config, scripts de provisionamento e guia
  operacional.
- `df/`: dotfiles e assets reais que vao para a maquina apos o bootstrap.
- `.agents/`: camada canonica de IA e governanca declarativa.
- `docs/`: documentacao tecnica, catalogos operacionais e referencia.
- `tests/`: suites de teste, harnesses e fixtures.
- `scripts/`: CLIs e validadores reutilizaveis do repo.
- `docker/`: harnesses e imagens auxiliares de integracao.
- `archive/`: legado e historico que nao deve contaminar os caminhos ativos.

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
```

### Sincronizacao entre ambientes

```powershell
task sync
task sync:wsl-gate
```

### Validacao local de qualidade

```powershell
task ci:validate
task test:integration:windows
```

```bash
task ci:validate
task test:integration:linux
```

## Config central do bootstrap

Arquivos principais:

- template versionado: `bootstrap/user-config.yaml.tpl`
- arquivo local ignorado: `bootstrap/user-config.yaml`

Derivados sincronizados automaticamente:

- `df/secrets/secrets-ref.yaml`
- `bootstrap/secrets/.env.local.tpl`
- `df/git/.gitconfig.local`

Principio atual:

- caminhos absolutos canonicos sao a fonte de verdade
- `_path` representa destino absoluto explicito
- `_dir` continua aceito por compatibilidade, mas nao e o formato preferido

## Tasks oficiais

O `Taskfile.yml` e a interface oficial de automacao do projeto.

Grupos principais:

- operacao do repo: `sync`, `repo:*`, `env:check`
- bootstrap: `bootstrap:*`
- qualidade e PR local: `ci:*`, `pr:*`, `test:*`
- governanca de IA: `ai:*`

Catalogos atualizados:

- `docs/TASKS.md`
- `docs/WORKFLOWS.md`

## Documentacao principal

Comece por estes arquivos:

- `CONTEXT.md`
- `docs/README.md`
- `bootstrap/README.md`
- `docs/bootstrap-flow.md`
- `docs/config-reference.md`
- `docs/checkenv.md`
- `docs/test-strategy.md`
- `tests/README.md`
- `docs/ai-operating-model.md`
- `SECURITY.md`

## Estado atual da camada de IA

- `.agents/` e a fonte canonica.
- `.codex/README.md` existe apenas como ponte de compatibilidade.
- Runtime local de assistentes, sessoes, caches, auth e historico nao entra no
  Git.

## Convenções operacionais

- Tasks e workflows devem permanecer em paridade.
- Toda rodada de IA precisa atualizar o worklog e fechar revisao de licoes.
- Commits e PRs seguem `emoji + conventional commits`.
- Branches seguem naming limpo, sem emoji.
