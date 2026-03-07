# Tests

Estrutura inicial:

- `tests/powershell`: testes Pester para logica PowerShell
- `tests/python`: testes unitarios da governanca Git, do tracker de WIP de IA e dos validadores de governanca
- `tests/python`: tambem cobre roteamento/delegacao de IA, smoke eval e sincronismo workflow-task-doc
- `tests/bash`: testes Bats para harnesses Linux do bootstrap
- `tests/fixtures`: fixtures auxiliares para editores e cenarios manuais que nao pertencem ao runtime de `df/`

Regra:

- primeiro testar funcao pura
- depois testar harness de integracao
- E2E sensivel fica fora do PR CI

Harnesses atualmente implementados:

- `tests/bash/bootstrap_relink_integration.bats`: valida `bootstrap/bootstrap-ubuntu-wsl.sh relink` em `HOME` temporario e repo injetado por `DOTFILES_REPO_ROOT_UNIX`
- `scripts/run-windows-bootstrap-integration.ps1`: valida `bootstrap/bootstrap-windows.ps1 -RelinkOnly` em perfil temporario no Windows real

Tasks:

- `task test:integration:linux`
- `task test:integration:windows`
