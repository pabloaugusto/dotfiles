# Secrets, Auth e Assinatura

Este guia descreve o modelo de segurança/autenticação usado pelos dotfiles.

## Princípios

1. Não versionar secrets plaintext.
2. Usar 1Password (`op`) como fonte de segredos de runtime.
3. Usar `sops+age` para dados sensíveis em arquivo.
4. Priorizar SSH agent do 1Password.
5. Garantir assinatura Git SSH por padrão.

## Refs de segredo

Fonte canônica: [`df/secrets/secrets-ref.yaml`](../df/secrets/secrets-ref.yaml) (gerado do YAML central).

Refs principais:

- `op://secrets/dotfiles/1password/service-account`
- `op://secrets/dotfiles/github/token` (preferencial)
- `op://secrets/github/api/token` (fallback)
- `op://secrets/dotfiles/age/age.key`
- `git-signing.automation-public-key` em [`df/secrets/secrets-ref.yaml`](../df/secrets/secrets-ref.yaml) quando o signer tecnico estiver configurado

## Runtime env cifrado

Template: [`bootstrap/secrets/.env.local.tpl`](../bootstrap/secrets/.env.local.tpl)

Fluxo:

1. `op inject` resolve refs para buffer temporário.
2. bootstrap cifra conteúdo para `~/.env.local.sops`.
3. bootstrap remove `~/.env.local` plaintext legado.
4. perfil carrega runtime env via decrypt on-demand.

Variáveis relevantes:

- `OP_SERVICE_ACCOUNT_TOKEN`
- `GH_TOKEN` (e `GITHUB_TOKEN` por compatibilidade)
- `SOPS_AGE_KEY`

## Persistência segura

- Persistido por padrão: `SOPS_AGE_KEY` em env de usuário.
- Não persistido por padrão: `OP_SERVICE_ACCOUNT_TOKEN`, `GH_TOKEN`, `GITHUB_TOKEN`.
- `SOPS_AGE_KEY_FILE` fica vazio (modelo env-only).

No WSL, o bootstrap grava `~/.config/dotfiles/runtime.env` com permissão restrita.

## GitHub CLI

Estratégia:

1. reaproveitar sessão existente (`gh auth status`)
2. se necessário, resolver token em ordem:
   - `GH_TOKEN`
   - `GITHUB_TOKEN`
   - ref dedicado do projeto
   - ref fallback
3. `gh auth login --with-token` + `git_protocol=ssh`

## SSH Agent e Git signing

Arquivos:

- [`df/ssh/config`](../df/ssh/config)
- [`df/ssh/config.windows`](../df/ssh/config.windows)
- [`df/ssh/config.unix`](../df/ssh/config.unix)
- [diretorio `df/git/`](../df/git/)

Políticas:

- `IdentityFile none` para evitar fallback em chaves locais
- `gpg.format=ssh`
- `commit.gpgsign=true`
- `gpg.ssh.program=op-ssh-sign`

## Modo humano vs automação

O repo passa a operar com dois perfis de assinatura:

- Humano: chave pública padrão em `~/.config/git/.gitconfig.local`.
- Automação: chave pública técnica aplicada só na worktree atual via
  `config.worktree`, sem exportar chave privada.

Fluxo recomendado para automação local:

1. guardar a chave privada técnica no 1Password SSH Agent
2. registrar a ref da chave pública em `git.automation_signing_key_ref` no
   bootstrap local
3. sincronizar os derivados do bootstrap
4. aplicar `task git:signing:mode:automation`
5. validar com `task env:check SIGN_MODE=automation`

Observações:

- a chave pública técnica não é segredo; a rotação continua simples porque a
  ref no 1Password é a fonte de verdade
- o GitHub é sincronizado via `gh`, sem manter material em plaintext no repo
- o `op` só resolve a chave pública e os tokens; a chave privada continua no
  1Password SSH Agent

## `user.signingkey` é segredo?

Não. É material público (chave pública SSH).

- Pode ficar em `~/.config/git/.gitconfig.local`
- A worktree de automação pode sobrescrevê-lo localmente sem tocar no perfil
  humano
- Não precisa de `sops+age`
- O segredo real é a chave privada, mantida no 1Password

## Operação recomendada

1. usar token dedicado do projeto como padrão
2. manter token amplo só como contingência
3. rodar `checkEnv` após mudanças em auth/SSH/Git
4. rotacionar imediatamente qualquer credencial exposta

## Rotacao canonica

Arquitetura de referencia:

- [`docs/reference/secrets-rotation-architecture.md`](reference/secrets-rotation-architecture.md)

Interface oficial:

- [`scripts/secrets-rotation.py`](../scripts/secrets-rotation.py)

Tasks:

- `task secrets:rotation:preflight`
- `task secrets:rotation:plan`
- `task secrets:rotation:validate`

Contrato:

1. `preflight` primeiro
2. `plan` antes de qualquer substituicao
3. `validate` depois da mudanca, sem pular `checkEnv`
4. nenhuma revogacao e valida sem substituta ja validada
