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
- `op://secrets/github/api/token` (fallback)
- `op://secrets/dotfiles/age/age.key`
- `git-signing.automation-public-key` em [`app/df/secrets/secrets-ref.yaml`](../app/df/secrets/secrets-ref.yaml) quando o signer tecnico estiver configurado

## Fronteira runtime x dev-time

Nem todo ref do repo pertence ao runtime do bootstrap.

- [`app/df/secrets/secrets-ref.yaml`](../app/df/secrets/secrets-ref.yaml): runtime do
  ambiente materializado na maquina
- [`config/platforms.yaml`](../config/platforms.yaml): control plane
  dev-time da camada de IA, desacoplada de [`app/bootstrap/`](../app/bootstrap/) e de
  [`app/df/`](../app/df/)
- o overlay local derivado de
  [`config/platforms.local.yaml.tpl`](../config/platforms.local.yaml.tpl)
  fica ignorado no Git e guarda refs reais de `Jira`/`Confluence` sem acoplar
  o contrato base do repo

No corte Atlassian, `Jira` e `Confluence` entram nesta segunda categoria.
Esses refs servem a adapters, migracao de backlog, comentarios, evidencias e
documentacao operacional, nao ao bootstrap do workstation.

Referencia canonica de scopes/permissoes e rotacao Atlassian:

- [`docs/atlassian-ia/2026-03-07-atlassian-auth-scopes-and-permissions.md`](atlassian-ia/2026-03-07-atlassian-auth-scopes-and-permissions.md)

## Service accounts Atlassian por agente

O runtime Atlassian da camada de IA agora aceita service account propria por
agente. A camada declarativa canonica passa a ser descoberta por
[`.agents/config/config.toml`](../.agents/config/config.toml); enquanto a
drenagem nao termina, os detalhes operacionais de `atlassian_actor` continuam
materializados em
[`.agents/config/agents.toml`](../.agents/config/agents.toml) como ponte
legada.

Regra canonica:

1. se o agente tiver `atlassian_actor.enabled=true` para a surface pedida, usar
   a service account propria dele
2. se nao tiver service account propria para a surface, usar a service account
   global definida em [`config/platforms.yaml`](../config/platforms.yaml)
3. se a service account propria falhar por identidade, permissao ou escrita, o
   runtime pode cair para a conta global quando
   `fallback_to_global_on_error=true`
4. todo fallback relevante vira incidente rastreavel em `Jira`; fallback
   silencioso e drift

Superficies suportadas hoje:

- `jira-comment`
- `jira-assignee`
- `confluence-comment`
- `confluence-page`

Cada agente declara capacidades separadas por surface. O runtime nao assume que
uma conta que comenta tambem pode atribuir issue.

### Naming canonico dos secrets por agente

Padrao recomendado:

- `op://secrets/dotfiles/atlassian-service-accounts/<agent>-api-token`
- `op://secrets/dotfiles/atlassian-service-accounts/<agent>-email`
- `op://secrets/dotfiles/atlassian-service-accounts/<agent>-id`

Exemplo do piloto atual do `PO`:

- `op://secrets/dotfiles/atlassian-service-accounts/ai-product-owner-api-token`
- `op://secrets/dotfiles/atlassian-service-accounts/ai-product-owner-email`
- `op://secrets/dotfiles/atlassian-service-accounts/ai-product-owner-id`

### Como obter o service account ID

Fluxo manual rapido:

1. descobrir o e-mail da service account no 1Password
2. abrir a busca de usuarios do Jira com esse identificador, por exemplo:
   [user search do PO](https://pabloaugusto.atlassian.net/rest/api/3/user/search?query=ia-product-owner)
3. validar no resultado:
   - `active = true`
   - `accountType = app`
   - `displayName` esperado
   - `emailAddress` esperado quando a API devolver esse campo
4. registrar o `accountId` no secret `.../<agent>-id`

Fluxo automatizado do repo:

- [`scripts/ai-atlassian-actor.py`](../scripts/ai-atlassian-actor.py)
  resolve a identidade efetiva por agente e surface
- [`scripts/ai-atlassian-actor-backfill.py`](../scripts/ai-atlassian-actor-backfill.py)
  audita e aplica o backfill de comentarios Jira quando a autoria precisa migrar
  da conta global para a conta propria do agente

Exemplos:

```powershell
python scripts/ai-atlassian-actor.py resolve --role ai-product-owner --surface jira-comment
python scripts/ai-atlassian-actor.py resolve --role ai-product-owner --surface jira-assignee
python scripts/ai-atlassian-actor.py state
```

### Ordem canonica de resolucao

Para qualquer agente com service account propria:

1. ler `account_id` do secret `.../<agent>-id`
2. validar coerencia minima com `email` e `token` da mesma conta
3. se o `account_id` falhar, tentar busca no Jira
4. se a busca resolver com seguranca, usar o valor apenas em memoria na rodada
   atual
5. abrir ou comentar uma `Bug` deduplicada no Jira, porque o fallback indica
   defeito, drift ou rotacao incompleta
6. se a busca tambem falhar, usar a service account global quando o contrato da
   surface permitir

O fallback por busca e contingencia, nao fluxo-base.

### Backfill de comentarios

O piloto inicial cobre `Jira`.

Contrato do backfill:

- limitar a comentarios estruturados da automacao
- identificar comentarios do agente escritos pela conta global
- recriar com a service account propria do agente
- so depois remover o comentario legado, quando a escrita correta ficar
  comprovada

Exemplos:

```powershell
python scripts/ai-atlassian-actor-backfill.py --role ai-product-owner
python scripts/ai-atlassian-actor-backfill.py --role ai-product-owner --apply
```

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

- `IdentityFile none` para evitar fallback em chaves locais
- `gpg.format=ssh`
- `commit.gpgsign=true`
- `gpg.ssh.program=op-ssh-sign`

## Modo humano vs automação: a identidade `daneel`

O repo opera com dois perfis de assinatura, selecionados **pelo ator** — nunca
por hostname:

- Humano: `user.signingkey` global = `git.signing_key` da config, resolvido via
  1Password (`op-ssh-sign`), como antes.
- Automação: identidade única `daneel`, a **mesma para todas as máquinas**.
  `TARS_ACTOR=agent` faz o Git usar a chave e a identidade da `daneel` via
  `GIT_CONFIG_COUNT`/`GIT_CONFIG_KEY_n`/`GIT_CONFIG_VALUE_n`, que são herdados
  por qualquer `git` do shell (inclusive `task sync`). O global continua
  intocado — sem `TARS_ACTOR`, nada muda para o humano.

SSOT única, na seção `automation` de
[`app/bootstrap/user-config.yaml`](../app/bootstrap/user-config.yaml):

| campo | default |
| --- | --- |
| `automation.signing_key_ref` | `op://secrets/daneel-bot/private key?ssh-format=openssh` |
| `automation.signing_public_key_ref` | `op://secrets/daneel-bot/public key` |
| `automation.op_token_ref` | `op://secrets/daneel-bot/1password/service-account` |
| `automation.allowed_signers_ref` | `op://secrets/dotfiles/git/allowed_signers` |
| `automation.git_name` / `automation.git_email` | `Daneel` / `daneel@pabloaugusto.com` |

Materialização (bootstrap, idempotente):

1. `op read --out-file` para `${XDG_CONFIG_HOME:-~/.config}/tars/automation/`
   (Windows: `%APPDATA%\tars\automation\`), com `daneel_ed25519` 600 (ACL só do
   usuário), `daneel_ed25519.pub` 644 e `op-sa.token` 600. O valor **nunca**
   passa por stdout nem por variável.
2. só regrava quando o conteúdo difere (lê para um temporário e compara).
3. `allowed_signers` (SSOT no 1Password) vai para
   `~/.config/git/allowed_signers` e o bootstrap grava
   `gpg.ssh.allowedSignersFile` de forma idempotente. Não existe mais
   `allowed_signers` gerado localmente.
4. se o item não existir no 1Password: falha clara com a instrução. O bootstrap
   **não** gera chave sozinho.

Trailer: commits do agente ganham `Machine: <hostname>` via
[`.githooks/prepare-commit-msg`](../.githooks/prepare-commit-msg), apenas
quando `TARS_ACTOR=agent` e de forma idempotente.

Observações:

- a chave pública não é segredo; a rotação continua simples porque a ref no
  1Password é a fonte de verdade
- o GitHub é sincronizado via `gh` (auth próprio), sem material em plaintext
- o `op` da automação usa a service account cujo token vive só em
  `~/.config/tars/automation/op-sa.token` (600); o shell não exporta token

## `user.signingkey` é segredo?

Em modo humano, não. É material público (chave pública SSH).

- SSOT: campo `git.signing_key` em
  [`app/bootstrap/user-config.yaml`](../app/bootstrap/user-config.yaml). O default no
  repositório é vazio de propósito; o dono preenche no wizard do bootstrap.
- O bootstrap (`configureGitSigningKey` no Bash, `Set-GitGlobalSigningKey` no
  PowerShell) grava `git config --global user.signingkey` a partir desse campo,
  de forma idempotente. Não usa `op read` — a chave pública não é segredo e a
  service account do bootstrap não enxerga o cofre `Personal`.
- Com o campo vazio, o bootstrap apenas avisa e preserva o
  `user.signingkey` global existente; o restante do bootstrap não quebra.
- Ainda pode ficar em `~/.config/git/.gitconfig.local`
- A worktree de automação pode sobrescrevê-lo localmente com o caminho da
  chave privada técnica, sem tocar no perfil humano
- Não precisa de `sops+age`
- O segredo real continua sendo a chave privada; no fluxo técnico ela fica fora
  do versionamento e restrita ao diretório Git comum da worktree

## Operação recomendada

1. usar token dedicado do projeto como padrão
2. usar `op://secrets/github/api/token` como fallback
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
