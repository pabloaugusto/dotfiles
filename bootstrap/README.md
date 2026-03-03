# Bootstrap Guide

Este diretório contém os fluxos de bootstrap para configurar dotfiles e ambiente base.

## Arquivos principais

- [bootstrap/_start.ps1](_start.ps1): entrypoint Windows.
- [bootstrap/bootstrap-config.ps1](bootstrap-config.ps1): validação/wizard da config central YAML.
- [bootstrap/bootstrap-windows.ps1](bootstrap-windows.ps1): execução do bootstrap/refresh no Windows.
- [bootstrap/bootstrap-ubuntu-wsl.sh](bootstrap-ubuntu-wsl.sh): bootstrap Ubuntu WSL.
- [bootstrap/user-config.yaml.tpl](user-config.yaml.tpl): template da config central local.
- [bootstrap/software-list.ps1](software-list.ps1): catálogo de software.
- [bootstrap/secrets/.env.local.tpl](secrets/.env.local.tpl): template de segredos runtime (origem para `.env.local.sops`).

## Configuração central

Antes do bootstrap Windows, `_start.ps1` gerencia `bootstrap/user-config.yaml`:

1. Se não existir, cria a partir de `bootstrap/user-config.yaml.tpl`.
2. Se estiver preenchido, pergunta:
   - usar 100% do que já está no YAML
   - sobrescrever em modo guiado
3. Se estiver incompleto, pergunta:
   - preencher guiado no terminal
   - preencher manualmente e abortar (rodar bootstrap depois)

Com isso, os arquivos derivados são sincronizados automaticamente:

- `df/secrets/secrets-ref.yaml`
- `bootstrap/secrets/.env.local.tpl`
- `df/git/.gitconfig.local` (não versionado)

Nota sobre `signingkey` em `df/git/.gitconfig.local`:

- É chave pública SSH de assinatura.
- Não é segredo e não precisa de `sops+age`.
- A chave privada deve ficar somente no 1Password SSH Agent.

## Modos de execução

### Windows

Executar:
```powershell
sudo $env:USERPROFILE\dotfiles\bootstrap\_start.ps1
```

Menu:

1. `Windows - new install`:
   - setup completo (software, fontes, preferências, auth/signing, check final).
2. `Windows - refresh dotfiles`:
   - re-aplica links/config, mantém setup auth/signing e check final.
3. Linux/Mac:
   - opções ainda não implementadas no `_start.ps1` (mantidas para evolução).

### Ubuntu WSL

Executar:
```bash
bash ~/dotfiles/bootstrap/bootstrap-ubuntu-wsl.sh
```

## Fases do bootstrap Windows

1. Validação de pré-requisitos:
   - elevação administrativa, diretórios base, carregamento de funções.
2. Symlinks:
   - home files, PowerShell profile, SSH, Git, VS Code e Windows Terminal.
3. Instalações (somente modo full):
   - módulos PowerShell, pacotes winget/choco/pip.
4. Auth/signing (full e refresh):
   - garante `1Password`, `op`, `gh`.
   - gera env temporário via `op inject` e persiste cifrado em `~/.env.local.sops`.
   - remove `~/.env.local` plaintext legado.
   - persiste `SOPS_AGE_KEY` para shells futuros (modo env-only).
   - autentica `gh` com token vindo do 1Password (preferencial: `op://secrets/dotfiles/github/token`).
5. Health-check final:
   - executa `checkEnv` e falha em caso de não conformidade.

## Fases do bootstrap Ubuntu WSL

1. Prompt de confirmação.
2. Instalação de ferramentas base (`apt` + Homebrew).
3. Symlinks de dotfiles.
4. Segredos runtime:
   - garante `OP_SERVICE_ACCOUNT_TOKEN`.
   - gera env temporário com `op inject` e persiste cifrado em `~/.env.local.sops`.
   - carrega variáveis por decrypt on-demand.
   - persiste `SOPS_AGE_KEY` em `~/.profile`/`~/.bashrc` (env-only).
5. Auth GitHub:
   - autentica `gh` por token e força protocolo `ssh` (preferencial: `op://secrets/dotfiles/github/token`).
6. Health-check final:
   - executa `checkEnv`.

## Pré-requisitos operacionais antes de rodar

### Windows

1. OneDrive configurado e variável `OneDrive` existente.
2. `D:\` disponível (fluxo atual depende desse layout).
3. Repositório em `C:\Users\<user>\dotfiles`.
4. 1Password Desktop com SSH Agent habilitado.
5. Opcional: `DOTFILES_ONEDRIVE_PROJECTS_PATH` para sobrescrever o destino `projects`.

### WSL

1. Repositório em `~/dotfiles`.
2. Conectividade de rede.
3. Permissão para instalar pacotes via `sudo`.
4. Segredos no 1Password conforme `df/secrets/secrets-ref.yaml`.
5. Opcional:
   - `DOTFILES_ONEDRIVE_ROOT`
   - `DOTFILES_ONEDRIVE_CLIENTS_DIR`
   - `DOTFILES_ONEDRIVE_PROJECTS_DIR`
6. Opcional (provisionar usuário extra):
   - `DOTFILES_ADD_USER`
   - `DOTFILES_ADD_USER_PASS_HASH` (saída de `openssl passwd -1`)

## Diferença prática entre bootstrap e refresh

- Bootstrap (new install):
  - aplica tudo.
  - tempo maior.
  - ideal para máquina nova.

- Refresh:
  - re-sincroniza dotfiles e fluxo auth/check sem reinstalar todo software.
  - tempo menor.
  - ideal para atualização cotidiana.

## Comandos úteis de operação

- Rodar check de conformidade manual:
  - PowerShell: `checkEnv`
  - Bash: `checkEnv`
- Recarregar profile PowerShell:
  - `. $PROFILE.CurrentUserAllHosts`
- Recarregar shell Bash:
  - `exec bash -l`
