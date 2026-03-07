# PowerShell Dotfiles

Este diretório concentra o runtime PowerShell do repositório (perfil, plugins,
aliases, checks e helpers de bootstrap).

## Arquivos principais

- `profile.ps1`: ponto de entrada carregado no terminal.
- `_functions.ps1`: biblioteca utilitária (instalação, symlink, auth/secrets, `checkEnv`).
- `env-vars.ps1`: variáveis de ambiente persistidas em `HKCU:\Environment`.
- `env-check.ps1`: verificação rápida de ergonomia no startup.
- `plugins.ps1`: carregamento de módulos/prompt.
- `aliases.ps1`: aliases e funções de uso diário.
- `wsl.ps1`: integração opcional com comandos WSL via `WslInterop`.

## Ordem de carga

`profile.ps1` carrega os módulos nesta sequência:

1. `_functions.ps1`
2. runtime secrets (`~/.env.local.sops` via `Import-DotEnvFromSops`)
3. `env-vars.ps1`
4. `env-check.ps1`
5. `plugins.ps1`
6. `aliases.ps1`
7. `hotkeys.ps1`
8. autocomplete do kubectl
9. `wsl.ps1`

## Segurança e autenticação

- Segredos de runtime são carregados de `~/.env.local.sops` (não de `.env.local` plaintext).
- `GH_TOKEN` é normalizado a partir de `GITHUB_TOKEN` quando necessário.
- `checkEnv` valida:
  - sessão `op`,
  - auth do `gh`,
  - SSH agent/handshake GitHub,
  - assinatura de commit SSH via 1Password,
  - coerência entre signer humano e signer técnico de automação quando a
    worktree atual estiver nesse modo.

## Requisitos recomendados

- PowerShell 7+
- 1Password Desktop + 1Password CLI (`op`)
- GitHub CLI (`gh`)
- `sops` + `age`
- Módulos: `PSReadLine`, `Terminal-Icons`, `posh-git`, `posh-docker`, `WslInterop` (opcional)

## Arquivos de terceiros

`df/powershell/.inc/3rd/*` contém scripts vendorizados/externos e não deve ser
editado no fluxo normal de manutenção.
