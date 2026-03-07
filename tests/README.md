# Tests

Camada de testes atual do repositorio.

## Estrutura

- `tests/powershell/`: testes Pester para parser de config, helpers e logica
  PowerShell.
- `tests/python/`: testes unitarios da governanca Git, worklog, lessons,
  roadmap, validadores, roteamento, delegacao e sincronismo workflow-task-doc.
- `tests/bash/`: testes Bats para harnesses Linux do bootstrap.
- `tests/fixtures/`: fixtures auxiliares para cenarios de teste que nao devem
  viver em `df/`.

## Camadas em uso

### Unitario

- PowerShell: `task test:unit:powershell`
- Python: `task test:unit:python`

Escopo atual:

- parser e normalizacao de config
- validadores de governanca
- tracker de WIP, roadmap e lessons
- roteamento, delegacao e smoke eval da camada de IA

### Integracao

- Linux: `task test:integration:linux`
- Windows: `task test:integration:windows`

Harnesses atuais:

- `tests/bash/bootstrap_relink_integration.bats`
  - valida `bootstrap/bootstrap-ubuntu-wsl.sh relink`
  - usa `HOME` temporario e repo injetado por `DOTFILES_REPO_ROOT_UNIX`
- `scripts/run-windows-bootstrap-integration.ps1`
  - valida `bootstrap/bootstrap-windows.ps1 -RelinkOnly`
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
- `df/` nao deve receber fixtures, scratch ou material de teste.

## Comandos uteis

Windows:

```powershell
task test:unit:powershell
task test:unit:python:windows
task test:integration:windows
```

Linux/WSL:

```bash
task test:unit:python:linux
task test:integration:linux
```
