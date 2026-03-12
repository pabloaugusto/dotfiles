# Secrets, Auth e Assinatura

Este guia descreve o modelo de segurança/autenticação usado pelos dotfiles.

## Princípios

1. Não versionar secrets plaintext.
2. Usar 1Password (`op`) como fonte de segredos de runtime.
3. Usar `sops+age` para dados sensíveis em arquivo.
4. Priorizar SSH agent do 1Password.
5. Garantir assinatura Git SSH por padrão.

## Refs de segredo

Fonte canônica: [`app/df/secrets/secrets-ref.yaml`](../app/df/secrets/secrets-ref.yaml) (gerado do YAML central).

Refs principais:

- `op://secrets/dotfiles/1password/service-account`
- `op://secrets/dotfiles/github/token` (preferencial)
- `op://secrets/github/api/token` (primeiro fallback)
- `op://Personal/github/token-full-access` (contingencia final humana)
- `op://secrets/dotfiles/age/age.key`
- `git-signing.automation-public-key` em [`app/df/secrets/secrets-ref.yaml`](../app/df/secrets/secrets-ref.yaml) quando o signer tecnico estiver configurado

## Fronteira runtime x dev-time

Nem todo ref do repo pertence ao runtime do bootstrap.

- [`app/df/secrets/secrets-ref.yaml`](../app/df/secrets/secrets-ref.yaml): runtime do
  ambiente materializado na maquina
- [`config/ai/platforms.yaml`](../config/ai/platforms.yaml): control plane
  dev-time da camada de IA, desacoplada de [`app/bootstrap/`](../app/bootstrap/) e de
  [`app/df/`](../app/df/)
- o overlay local derivado de
  [`config/ai/platforms.local.yaml.tpl`](../config/ai/platforms.local.yaml.tpl)
  fica ignorado no Git e guarda refs reais de `Jira`/`Confluence` sem acoplar
  o contrato base do repo

No corte Atlassian, `Jira` e `Confluence` entram nesta segunda categoria.
Esses refs servem a adapters, migracao de backlog, comentarios, evidencias e
documentacao operacional, nao ao bootstrap do workstation.

Referencia canonica de scopes/permissoes e rotacao Atlassian:

- [`docs/atlassian-ia/2026-03-07-atlassian-auth-scopes-and-permissions.md`](atlassian-ia/2026-03-07-atlassian-auth-scopes-and-permissions.md)

Para `service-account-api-token`, o acesso REST oficial usa o gateway
`api.atlassian.com` com `cloud_id`. Nessa modalidade:

- `ATLASSIAN_SITE_URL` continua util para links navegaveis e automacao de UI
- `ATLASSIAN_CLOUD_ID` passa a ser obrigatorio para chamadas REST
- o token pode ser enviado como `Bearer`, sem depender do e-mail humano

## Resolucao em lote no 1Password

Para evitar `rate limit`, latencia desnecessaria e erros por leituras
consecutivas, a regra do control plane e:

1. preferir `op run` para resolver refs `op://...` em lote na borda do processo
2. usar `op item get --format json` como fallback por item, nunca como loop por
   campo
3. proibir `op read` repetitivo espalhado pelo codigo de dominio
4. carregar os valores uma vez por execucao e manter cache apenas em memoria

Aplicacao pratica na trilha Atlassian:

- `resolve_atlassian_platform()` tenta primeiro resolver os refs do item
  Atlassian em lote com `op run`
- se o batch falhar, o resolver cai para leitura por item com `op item get`
- `op read` fica reservado a fallback pontual, nao ao fluxo-base

Regra perene:

- `1Password` entra apenas na borda do processo; depois disso, scripts e
  adapters trabalham com cache local em memoria
- fallback de service account so ajuda quando o bloqueio estiver no token ou na
  identidade especifica; se o cap estourado for `account.read_write`, um segundo
  token da mesma conta nao resolve sozinho

## Runtime env cifrado

Template: [`app/bootstrap/secrets/.env.local.tpl`](../app/bootstrap/secrets/.env.local.tpl)

Fluxo:

1. `op inject` resolve refs para buffer temporário.
2. bootstrap cifra conteúdo para `~/.env.local.sops`.
3. bootstrap remove `~/.env.local` plaintext legado.
4. perfil carrega runtime env via decrypt on-demand.

Variáveis relevantes:

- `OP_SERVICE_ACCOUNT_TOKEN`
- `GH_TOKEN` (e `GITHUB_TOKEN` por compatibilidade)
- `SOPS_AGE_KEY`
- `ATLASSIAN_SITE_URL`
- `ATLASSIAN_EMAIL`
- `ATLASSIAN_API_TOKEN`
- `ATLASSIAN_SERVICE_ACCOUNT`
- `ATLASSIAN_CLOUD_ID`
- `ATLASSIAN_PROJECT_KEY`
- `ATLASSIAN_SPACE_KEY`

Quando o overlay local derivado do template existir, ele pode apontar
diretamente para refs `op://...` e elimina a necessidade de exportar essas
variaveis manualmente no shell.

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
   - primeiro fallback full-access
   - contingencia final full-access
3. `gh auth login --with-token` + `git_protocol=ssh`

## SSH Agent e Git signing

Arquivos:

- [`app/df/ssh/config`](../app/df/ssh/config)
- [`app/df/ssh/config.windows`](../app/df/ssh/config.windows)
- [`app/df/ssh/config.unix`](../app/df/ssh/config.unix)
- [diretorio `app/df/git/`](../app/df/git/)

Políticas:

- no Windows, `~/.ssh` deve ser um diretorio real no perfil do usuario, com
  arquivos canonicos materializados a partir de [`app/df/ssh/`](../app/df/ssh/)
  e ACL segura para o OpenSSH
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

No modo de automação, a worktree também pode materializar um `core.sshCommand`
scoped para o próprio checkout, apontando para a chave técnica local derivada
no diretório Git comum da worktree. Nesse mesmo modo, `user.signingkey` passa
a referenciar a chave privada técnica local e `gpg.ssh.program` e sobrescrito
para `ssh-keygen`, permitindo assinatura Git sem depender do prompt biométrico
do 1Password fora do fluxo humano padrão. A resolução desses caminhos fica
centralizada em [`scripts/git_signing_lib.py`](../scripts/git_signing_lib.py),
evitando drift entre o contrato documental e a implementação real.

Observações:

- a chave pública técnica não é segredo; a rotação continua simples porque a
  ref no 1Password é a fonte de verdade
- o GitHub é sincronizado via `gh`, sem manter material em plaintext no repo
- o `op` só resolve a chave pública e os tokens; a chave privada continua no
  1Password SSH Agent

## `user.signingkey` é segredo?

Em modo humano, não. É material público (chave pública SSH).

- Pode ficar em `~/.config/git/.gitconfig.local`
- A worktree de automação pode sobrescrevê-lo localmente com o caminho da
  chave privada técnica, sem tocar no perfil humano
- Não precisa de `sops+age`
- O segredo real continua sendo a chave privada; no fluxo técnico ela fica fora
  do versionamento e restrita ao diretório Git comum da worktree

## Operação recomendada

1. usar token dedicado do projeto como padrão
2. usar `op://secrets/github/api/token` como primeiro fallback
3. usar `op://Personal/github/token-full-access` como contingencia final em
   sessao humana interativa
4. rodar `checkEnv` após mudanças em auth/SSH/Git
5. rotacionar imediatamente qualquer credencial exposta

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
