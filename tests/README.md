# Tests

Camada de testes atual do repositorio.

## Estrutura

- [`tests/powershell/`](tests/powershell/): testes Pester para parser de config, helpers e logica
  PowerShell.
- [`tests/python/`](tests/python/): testes da camada Python do repo, incluindo governanca Git,
  worklog, lessons, roadmap, validadores, roteamento, delegacao, sincronismo
  workflow-task-doc e wrappers de tooling.
- [`tests/bash/`](tests/bash/): testes Bats para harnesses Linux do bootstrap.
- [`tests/fixtures/`](tests/fixtures/): fixtures auxiliares para cenarios de teste que nao devem
  viver em [`df/`](df/).

## Camadas em uso

### Unitario

- PowerShell: `task test:unit:powershell`
- Python legado/compatibilidade: `task test:unit:python`
- Python canonico de qualidade: `task test:python`

Escopo atual:

- parser e normalizacao de config
- validadores de governanca
- tracker de WIP, roadmap e lessons
- roteamento, delegacao e smoke eval da camada de IA
- wrappers de ferramentas auxiliares (`actionlint`, `gitleaks`, `cspell`)
- validacao documental e contratos da toolchain Python

### Integracao

- Linux: `task test:integration:linux`
- Windows: `task test:integration:windows`

Harnesses atuais:

- [`tests/bash/bootstrap_relink_integration.bats`](tests/bash/bootstrap_relink_integration.bats)
  - valida o script [`bootstrap/bootstrap-ubuntu-wsl.sh`](../bootstrap/bootstrap-ubuntu-wsl.sh) com o argumento `relink`
  - usa `HOME` temporario e repo injetado por `DOTFILES_REPO_ROOT_UNIX`
- [`scripts/run-windows-bootstrap-integration.ps1`](scripts/run-windows-bootstrap-integration.ps1)
  - valida o script [`bootstrap/bootstrap-windows.ps1`](../bootstrap/bootstrap-windows.ps1) com a flag `-RelinkOnly`
  - usa perfil temporario, `Documents` isolado e repo injetado no Windows real

### CI canonico

- `task ci:quality:linux`
- `task ci:quality:windows`
- `task ci:bootstrap:integration:linux`
- `task ci:bootstrap:integration:windows`
- `task ci:ai:check:linux`

## Regras do repositorio

- Primeiro testar funcao pura.
- Depois validar harness de integracao.
- E2E sensivel com segredos reais fica fora do PR CI.
- [`df/`](df/) nao deve receber fixtures, scratch ou material de teste.

## Comandos uteis

Windows:

```powershell
task install:dev:windows
task test:python:windows
task test:unit:powershell
task test:unit:python:windows
task test:integration:windows
```

Linux/WSL:

```bash
task install:dev:linux
task test:python:linux
task test:unit:python:linux
task test:integration:linux
```
