# Test Strategy

## Objetivo

Construir uma estrategia de qualidade para este repo de dotfiles com foco em:

- reprodutibilidade
- baixo custo de execucao
- isolamento
- evidencias reais de funcionamento
- paridade entre Windows e Linux

## Arquitetura recomendada

### Camada A - unit tests

- PowerShell: `Pester`
- Bash: `Bats`
- Python: `pytest` como runner canonico da camada Python, preservando
  `unittest` como task de compatibilidade para a suite historica

Escopo:

- parse e merge de config
- canonicalizacao de paths
- precedence `_dir` vs `_path`
- resolucao de layout de links
- flags e comportamento deterministico

### Camada B - integration tests

- Linux: container OCI
- Windows: runner Windows hospedado e efemero

Escopo:

- criacao de diretorios
- symlinks e junctions
- arquivos derivados
- refresh e relink
- idempotencia
- conflitos previsiveis

### Camada C - protected E2E

- secrets reais
- auth real
- eventualmente WSL real
- approval obrigatorio

Escopo:

- smoke de ponta a ponta
- captura completa de logs e artifacts

### Camada D - local lab

- Windows Sandbox para smoke local descartavel
- container local para Linux

Escopo:

- depuracao rapida
- reproducao local de regressao
- validacao manual de cenarios pesados

## Decisoes de plataforma

### Linux

Linux continua container-first.

Motivos:

- custo baixo
- execucao rapida
- isolamento forte
- boa aderencia ao bootstrap Linux

### Windows

Windows nao sera container-first.

Motivos:

- o bootstrap mexe com perfil de usuario
- ha manipulacao de symlink/junction
- ha dependencia de registry e layout de desktop
- ha cenarios com OneDrive, auth e WSL que ficam mais proximos da realidade em Windows real

Uso recomendado:

- PR CI: `windows-latest` para smoke/integration sem secrets reais
- local: `Windows Sandbox`
- E2E protegido: runner Windows dedicado e descartavel

## Requisitos de testabilidade

Antes de expandir o harness, o bootstrap precisa aceitar contexto injetavel.

Contrato inicial recomendado:

- `RepoRoot`
- `HomeDir`
- `ConfigRoot`
- `StateDir`
- `UserConfigPath`
- `CI`
- `DisableOneDrive`
- `Disable1Password`
- `DisableGhAuth`

Primeiros pontos de injecao efetivamente adotados nesta worktree:

- Linux: `DOTFILES_REPO_ROOT_UNIX`, `DOTFILES_BOOTSTRAP_ASSUME_POLO`
- Windows: `DOTFILES_REPO_ROOT_WINDOWS`, `DOTFILES_WINDOWS_DOCUMENTS_PATH`, `DOTFILES_WINDOWS_CODE_USER_PATH`, `DOTFILES_WINDOWS_TERMINAL_SETTINGS_PATH`

## Requisitos formais

- idempotencia obrigatoria para `refresh` e `relink`
- teste do estado final, nao so do exit code
- fixtures de CI independentes do host do desenvolvedor
- PR CI sem secrets reais
- E2E real somente em workflow protegido

## Sequencia de implementacao

1. governanca de naming de commits e PRs
2. documentacao da estrategia
3. testes unitarios de PowerShell
4. testes unitarios de Bash
5. integration Linux em container
6. integration Windows em runner hospedado
7. protected E2E com approvals

Estado atual desta worktree:

- governance/worklog/roadmap: camada formal entregue com worklog, roadmap, licoes aprendidas, smoke eval e gates de sincronismo
- integration Linux: harness de relink em container com Bats
- integration Windows: harness de relink em runner Windows real com perfil temporario
- AI routing/delegation: backend Python declarativo com smoke eval e gate de sincronismo workflow-task-doc
- quality stack Python: `uv`, [`pyproject.toml`](pyproject.toml), [`uv.lock`](uv.lock), `ruff`, `ty`,
  `pytest`, `pymarkdownlnt`, `yamllint`, `actionlint` e `gitleaks`
- worktree compartilhada Windows/WSL: `.venv/windows` e `.venv/linux` para
  evitar colisao entre runtimes
