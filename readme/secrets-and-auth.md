# Secrets, Auth e Assinatura

Guia de como os dotfiles usam 1Password, GitHub CLI e `sops+age`.

## Objetivo do desenho atual

1. Evitar segredos em texto puro no repositório.
2. Usar `op` para segredos de runtime (login e tokens).
3. Usar `sops+age` para arquivos versionados que precisam ficar cifrados.
4. Forçar Git + SSH + assinatura via 1Password.

## Refs de segredo

Arquivo canônico: [df/secrets/secrets-ref.yaml](../df/secrets/secrets-ref.yaml)

Origem dos valores:

- Durante bootstrap Windows, o arquivo central `bootstrap/user-config.yaml` é tratado como fonte única.
- `df/secrets/secrets-ref.yaml` é sincronizado automaticamente a partir dele.

Refs principais:

- `op://secrets/dotfiles/1password/service-account`
- `op://secrets/dotfiles/github/token` (preferencial)
- `op://secrets/github/api/token` (fallback)
- `op://secrets/dotfiles/age/age.key`

## Runtime secrets (`.env.local.sops`)

Template: [bootstrap/secrets/.env.local.tpl](../bootstrap/secrets/.env.local.tpl)

Processo:

1. Bootstrap roda `op inject`.
2. Gera um buffer temporário em memória/arquivo temporário.
3. Criptografa para `~/.env.local.sops` com `sops+age`.
4. Remove qualquer `~/.env.local` legado em texto puro.
5. Carrega variáveis no processo via decrypt on-demand.

Variáveis esperadas no template:

- `OP_SERVICE_ACCOUNT_TOKEN`
- `GH_TOKEN` (e `GITHUB_TOKEN` por compatibilidade)
- `SOPS_AGE_KEY`

## GitHub CLI (`gh`)

Fluxo implementado:

1. Tenta reaproveitar sessão `gh` existente.
2. Se não existir, resolve token de:
   - `GH_TOKEN`
   - `GITHUB_TOKEN`
   - `op://secrets/dotfiles/github/token`
   - `op://secrets/github/api/token`
3. Executa login com token:
   - `gh auth login --hostname github.com --git-protocol ssh --with-token`
4. Ajusta:
   - `gh auth setup-git --hostname github.com`
   - `gh config set git_protocol ssh --host github.com`

## SSH Agent 1Password

Arquivos:

- Base: [df/ssh/config](../df/ssh/config)
- Windows: [df/ssh/config.windows](../df/ssh/config.windows)
- Unix/WSL: [df/ssh/config.unix](../df/ssh/config.unix)

Políticas relevantes:

- `IdentityFile none` para prevenir fallback para `id_*` locais.
- Include do arquivo gerado pelo 1Password:
  - `Include ~/.ssh/1Password/config`

## Assinatura Git via SSH (1Password)

Arquivos Git por ambiente:

- [df/git/.gitconfig-base](../df/git/.gitconfig-base)
- [df/git/.gitconfig-windows](../df/git/.gitconfig-windows)
- [df/git/.gitconfig-wsl-windowsfs](../df/git/.gitconfig-wsl-windowsfs)
- [df/git/.gitconfig-linux](../df/git/.gitconfig-linux)

Requisitos esperados:

- `gpg.format=ssh`
- `commit.gpgsign=true`
- `user.signingkey=ssh-...`
- `gpg.ssh.program` apontando para `op-ssh-sign` (binário válido do 1Password)

Identidade Git:

- O repositório usa placeholders em `df/git/.gitconfig-base`.
- Configure valores reais em `~/.config/git/.gitconfig.local` usando o sample:
  - [df/git/.gitconfig.local.sample](../df/git/.gitconfig.local.sample)

## Papel do sops+age

`sops+age` complementa o fluxo de runtime:

- Runtime auth/token: `op` e `.env.local.sops` (não versionado e cifrado).
- Arquivos versionados com segredo: cifrados via `sops` com chave `age`.

`SOPS_AGE_KEY` em variável de ambiente é suficiente no fluxo atual (env-only).

## Recomendações de segurança

1. Manter o token dedicado (`op://secrets/dotfiles/github/token`) como padrão para bootstrap.
2. Manter o token amplo (`op://secrets/github/api/token`) apenas como fallback de contingência.
3. Rotacionar imediatamente qualquer token já exposto.
4. Não commitar `~/.env.local` nem `~/.env.local.sops`.
5. Manter `1Password SSH Agent` habilitado somente quando necessário.
6. Rodar `checkEnv` após mudanças em auth/ssh/git.
