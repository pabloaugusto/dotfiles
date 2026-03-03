# Dotfiles

Repositório de dotfiles com bootstrap para Windows (host) e Ubuntu WSL, com foco em:

- Autenticação Git via SSH usando 1Password SSH Agent.
- `gh` autenticado automaticamente com token vindo do 1Password.
- Commits Git assinados com SSH (`gpg.format=ssh`) via binário do 1Password.
- Health-check padronizado (`checkEnv`) para validar conformidade do ambiente.

![Test Status](https://github.com/pabloaugusto/dotfiles/actions/workflows/check-scripts.yml/badge.svg)

## Escopo

- `bootstrap/_start.ps1`: entrypoint do bootstrap no Windows.
- `bootstrap/bootstrap-windows.ps1`: execução de bootstrap/refresh no Windows.
- `bootstrap/bootstrap-ubuntu-wsl.sh`: bootstrap no Ubuntu WSL.
- `df/powershell/_functions.ps1`: funções utilitárias PowerShell, inclusive `checkEnv`.
- `df/bash/.inc/check-env.sh`: `checkEnv` no Bash.
- `df/ssh/*`: configuração SSH base e por ambiente.
- `bootstrap/secrets/.env.local.tpl`: template de segredos runtime injetados via `op inject`.

## Pré-requisitos

### Windows (host)

1. Windows 10/11 com PowerShell 7.
2. `winget` disponível (o `_start.ps1` tenta instalar se ausente).
3. Diretório `D:\` e OneDrive configurado (fluxo atual depende disso).
4. Repositório clonado em `C:\Users\<user>\dotfiles`.
5. 1Password Desktop instalado e com SSH Agent habilitado no app.
6. Opcional (OneDrive custom): `DOTFILES_ONEDRIVE_PROJECTS_PATH`.

### Ubuntu WSL

1. Distribuição Ubuntu funcional.
2. Acesso a internet para `apt`/Homebrew.
3. Repositório clonado em `~/dotfiles`.
4. 1Password CLI (`op`) com token de Service Account disponível.
5. Opcional (OneDrive custom):
   - `DOTFILES_ONEDRIVE_ROOT`
   - `DOTFILES_ONEDRIVE_CLIENTS_DIR`
   - `DOTFILES_ONEDRIVE_PROJECTS_DIR`
6. Opcional (provisionar usuário extra):
   - `DOTFILES_ADD_USER`
   - `DOTFILES_ADD_USER_PASS_HASH` (saída de `openssl passwd -1`)
   - Use quando quiser separar usuario pessoal de automacao/deploy no WSL.

## Secrets esperados no 1Password

Referência central em [df/secrets/secrets-ref.yaml](df/secrets/secrets-ref.yaml):

- `op://secrets/dotfiles/1password/service-account`
- `op://secrets/dotfiles/github/token` (preferencial para bootstrap/dotfiles)
- `op://secrets/github/api/token`
- `op://secrets/dotfiles/age/age.key`

Template runtime em [bootstrap/secrets/.env.local.tpl](bootstrap/secrets/.env.local.tpl):

- `OP_SERVICE_ACCOUNT_TOKEN`
- `GITHUB_TOKEN` (apontando para o token dedicado do projeto)
- `SOPS_AGE_KEY`

## Config Central (YAML)

- Template versionado: [bootstrap/user-config.yaml.tpl](bootstrap/user-config.yaml.tpl)
- Arquivo local (não versionado): `bootstrap/user-config.yaml`
- O `_start.ps1` valida esse arquivo antes de continuar:
  - se estiver preenchido: pergunta se usa como está ou sobrescreve em modo guiado.
  - se estiver incompleto: pergunta se preenche via wizard agora ou aborta para preenchimento manual.

Esse YAML centraliza personalizações (Git, paths e refs de segredo) e sincroniza automaticamente:

- `df/secrets/secrets-ref.yaml`
- `bootstrap/secrets/.env.local.tpl`
- `df/git/.gitconfig.local`

Nota sobre `git.signing_key`:

- É a chave **pública** de assinatura SSH (não é segredo).
- Não precisa ser protegida com `sops+age`.
- O segredo é a chave privada, que deve permanecer no 1Password SSH Agent.

## Quick Start

### Novo ambiente Windows

1. Clone o repositório:
```powershell
git clone https://github.com/pabloaugusto/dotfiles.git $env:USERPROFILE\dotfiles
```
2. Rode o bootstrap:
```powershell
sudo $env:USERPROFILE\dotfiles\bootstrap\_start.ps1
```
3. No menu:
   - `1` para instalação completa.
   - `2` para refresh de dotfiles.

### Novo ambiente Ubuntu WSL

1. Clone:
```bash
git clone https://github.com/pabloaugusto/dotfiles.git ~/dotfiles
```
2. Execute:
```bash
bash ~/dotfiles/bootstrap/bootstrap-ubuntu-wsl.sh
```

## Bootstrap vs Refresh

### Bootstrap (Windows opção `1`)

Executa fluxo completo:

- Symlinks de dotfiles.
- Instalação de softwares e módulos.
- Ajustes de preferências do Windows.
- Setup runtime auth/signing (`.env.local.sops`, `gh` auth, `SOPS_AGE_KEY` em env).
- `checkEnv` final obrigatório.

### Refresh (Windows opção `2`)

Executa fluxo enxuto:

- Reaplica symlinks/configuração.
- Pula instalação de software/fontes.
- Pula ajustes de preferências do sistema.
- Mantém validação auth/signing e `checkEnv` final.

## checkEnv

`checkEnv` existe em ambos shells:

- PowerShell: função em [df/powershell/_functions.ps1](df/powershell/_functions.ps1).
- Bash: função em [df/bash/.inc/check-env.sh](df/bash/.inc/check-env.sh).

### Como usar

PowerShell:
```powershell
checkEnv
```

Bash:
```bash
checkEnv
```

### O que valida

- Comandos essenciais (`op`, `gh`, `git`, `ssh`) e opcionais (`sops`, `age`).
- Sessão do 1Password (`op whoami`).
- Leitura dos refs em `df/secrets/secrets-ref.yaml`.
- Status de autenticação do `gh` e protocolo SSH.
- Política Git de assinatura SSH (`gpg.format`, `commit.gpgsign`, `user.signingkey`, `gpg.ssh.program`).
- Política SSH (`identityagent`, `identityfile none`, socket 1Password no Unix/WSL).
- Handshake SSH com GitHub (`ssh -T git@github.com`).
- Commit assinado de teste em repositório temporário.

### Resultado

Cada item retorna:

- `SUCCESS`
- `FAIL`
- `INCONCLUSIVE`

No final, o relatório lista sugestões de correção para os itens não conformes.

## Rotina multi-ambiente (obrigatória antes de testes no WSL)

Sempre que houver mudança no Windows e você for testar no WSL:

1. Commit e push no Windows.
2. No PowerShell do Windows, rode:
```powershell
dfsync
```
3. Só então execute comandos/testes no WSL.

`dfsync` valida o seguinte:

- Repositório do Windows está limpo.
- Push da branch atual para `origin`.
- Repositório do WSL está limpo.
- Pull no WSL com `--ff-only`.
- HEAD final igual entre Windows e WSL.

## Fluxo de segurança adotado

### Runtime auth (op/gh/ssh signing)

Usa 1Password (`op`) para resolver segredos em tempo de execução.

### Segredos versionados em arquivo

Usa `sops+age` para conteúdos que precisam estar no repositório de forma cifrada.

### Chave age no runtime

O fluxo atual é env-only por padrão:

- `SOPS_AGE_KEY` carregada no ambiente do usuário.
- `SOPS_AGE_KEY_FILE` mantida vazia, sem materializar `keys.txt` automaticamente.

## Documentação complementar

- Guia do bootstrap: [bootstrap/README.md](bootstrap/README.md)
- Guia do health-check: [readme/checkenv.md](readme/checkenv.md)
- Guia de secrets e segurança: [readme/secrets-and-auth.md](readme/secrets-and-auth.md)
- Guia de segurança para repo público: [SECURITY.md](SECURITY.md)

## Troubleshooting rápido

1. `gh` não logado: valide o ref `op://secrets/dotfiles/github/token` no `op` e rode `checkEnv` (fallback aceito: `op://secrets/github/api/token`).
2. SSH falhando no GitHub: confirme chave pública no GitHub e SSH Agent do 1Password ativo.
3. Assinatura de commit falhando: revise `gpg.ssh.program` e `user.signingkey`.
   - `user.signingkey` é pública; o ponto crítico é disponibilidade do `op-ssh-sign` e do agent.
4. `checkEnv` inconclusivo em rede: reexecute após garantir conectividade.
