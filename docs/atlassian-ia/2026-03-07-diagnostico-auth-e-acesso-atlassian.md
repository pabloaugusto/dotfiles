# Diagnostico de Auth e Acesso Atlassian

- Status: `operacional-com-seed-concluido-e-gap-em-board`
- Data-base: `2026-03-07`
- Contexto relacionado:
  - [`2026-03-07-atlassian-auth-scopes-and-permissions.md`](2026-03-07-atlassian-auth-scopes-and-permissions.md)
  - [`2026-03-07-parecer-e-plano-inicial.md`](2026-03-07-parecer-e-plano-inicial.md)
  - [`../../config/ai/platforms.yaml`](../../config/ai/platforms.yaml)
  - [`../../config/ai/platforms.local.yaml.tpl`](../../config/ai/platforms.local.yaml.tpl)
  - [`../../docs/secrets-and-auth.md`](../../docs/secrets-and-auth.md)

## Achados validados

- o `cloud_id` resolvido do tenant em `2026-03-07` e
  `06fb26d7-284b-4ba7-b0c1-d3f0d6860d04`
- tokens com `service-account-api-token` exigem o gateway
  `api.atlassian.com/ex/{product}/{cloud_id}` com `Bearer token`
- `Jira core` esta operacional pelo gateway oficial:
  - leitura de projeto
  - leitura de statuses
  - leitura de components
  - leitura de fields
- endpoints administrativos de `Jira Platform` estao operacionais com o token
  amplo atual:
  - `GET /rest/api/3/workflow/search`
  - `GET /rest/api/3/issuetypescheme/project`
  - `GET /rest/api/3/field/search`
- `Confluence v2` esta operacional pelo gateway oficial:
  - leitura de spaces
  - leitura de pages
- o secret local resolve `space_key = DOT`, e o tenant responde esse alias para
  o `space` real com `key = DO` e `currentActiveAlias = DOT`
- a semeadura retroativa foi executada com sucesso em `2026-03-08`:
  - seed inicial no `Jira`: `64` issues reais criadas e verificadas por API
    (`DOT-1` a `DOT-64`)
  - total atual no tenant apos abertura dos backlogs residuais:
    `84` issues (`DOT-1` a `DOT-84`)
  - `Confluence`: `29` paginas oficiais sincronizadas e verificadas por API
    apos o docs sync dedicado
  - a pagina nativa `dotfiles Home` continua fora da arvore oficial do control
    plane
  - issue de migracao: [`DOT-1`](https://pabloaugusto.atlassian.net/browse/DOT-1)
    com bundle auditavel anexado e comentarios estruturados de evidencia
  - linkagem bidirecional validada por API:
    - a issue `DOT-1` comenta URLs do `Confluence`
    - a pagina hub do `Confluence` contem link navegavel para `DOT-1`
- a API de board do `Jira Software` continua falhando com `401 Unauthorized;
  scope does not match`
- probes adicionais de autenticacao para o board confirmaram que o problema
  nao e apenas base URL:
  - `gateway + Bearer`: `401 Unauthorized; scope does not match`
  - `gateway + Basic`: `401 Unauthorized`
  - `site + Basic`: `401 Client must be authenticated to access this resource`
  - `site + Bearer`: `403 Failed to parse Connect Session Auth Token`
- o workflow publicado do tenant foi atualizado com sucesso e agora inclui o
  status `Paused`
- o board visivel na UI do projeto `DOT` foi normalizado por browser
  autenticado:
  - as colunas canonicas do fluxo agora aparecem no board settings
  - o status `Paused` esta mapeado em coluna propria
  - a validacao browser do board retornou `PASS`
  - o board settings ficou com `warning_count = 0`
- o backlog oficial agora possui um item dedicado para esse gap:
  - [`DOT-65`](https://pabloaugusto.atlassian.net/browse/DOT-65) -
    normalizacao do layout do board ao workflow oficial
- a ativacao do browser validator ficou rastreada separadamente em:
  - [`DOT-66`](https://pabloaugusto.atlassian.net/browse/DOT-66) -
    validacao visual via `Playwright` apos estabilizacao da fase base
- o falso negativo residual do browser validator agora esta rastreado e
  concluido em:
  - [`DOT-77`](https://pabloaugusto.atlassian.net/browse/DOT-77) -
    fallback semantico para titulos genericos em telas SPA do Atlassian
- a frente de rastreabilidade `GitHub` + `Jira` + `Confluence` agora esta
  oficialmente aberta no backlog:
  - [`DOT-78`](https://pabloaugusto.atlassian.net/browse/DOT-78) - epic da
    frente
  - [`DOT-79`](https://pabloaugusto.atlassian.net/browse/DOT-79) - story em
    `Refinement`
  - [`DOT-80`](https://pabloaugusto.atlassian.net/browse/DOT-80) ->
    [`DOT-84`](https://pabloaugusto.atlassian.net/browse/DOT-84) - subtasks de
    execucao
- a pagina oficial da frente nova ja foi publicada no `Confluence`:
  - [`DOT - GitHub Jira Confluence Traceability`](https://pabloaugusto.atlassian.net/wiki/spaces/DOT/pages/254739915)
  - [`DOT - GitHub Atlassian Runbook`](https://pabloaugusto.atlassian.net/wiki/spaces/DOT/pages/254740135)
- o bootstrap humano inicial do `Playwright` foi concluido com `storageState`
  persistido localmente
- a primeira validacao browser positiva desta trilha ja foi executada:
  - board settings do `DOT` validado com `PASS`
  - criterios confirmados: `PAUSED` presente e `Map statuses to columns`
  - evidencias locais e anexos remotos ficaram ligados a
    [`DOT-66`](https://pabloaugusto.atlassian.net/browse/DOT-66)
- a segunda validacao browser positiva desta trilha confirmou que:
  - o validator agora aceita `title_match_mode = body-fallback` quando o
    titulo do navegador for generico
  - a URL, a sessao autenticada e o conteudo esperado continuam obrigatorios
  - os anexos e comentarios de aceite ficaram centralizados em
    [`DOT-77`](https://pabloaugusto.atlassian.net/browse/DOT-77)
- a validacao de uma pagina do `Confluence` tambem confirmou sessao
  autenticada; o unico drift restante foi de criterio textual esperado, nao de
  acesso browser

## Diagnostico atual do signer tecnico

- a worktree atual ainda esta em `mode = human` no retorno real de
  `task git:signing:status`
- o problema ativo ja nao e o wrapper da task:
  `task git:signing:mode:automation` agora falha cedo por configuracao ausente
  de `git.automation_signing_key_ref`
- o `checkEnv` em `SIGN_MODE=automation` mostrou que:
  - o signer humano ainda consegue produzir commit assinado
  - a worktree continua sem `dotfiles.signing.automationPublicKeyRef`
  - refs de `op://...` ligadas a service account ainda aparecem como nao
    legiveis nesse contexto
- quando a task foi forçada com
  `PUBLIC_KEY_REF=op://secrets/dotfiles/git-automation/public key`, a falha
  real mudou para rate limit do `1Password CLI` (`Too many requests`)
- implicacao pratica:
  - o bloqueio residual do signer tecnico agora esta concentrado em
    configuracao local da ref publica + leitura do `1Password` na borda
  - o wrapper PowerShell deixou de ser o gargalo principal desta trilha
- backlog oficial relacionado:
  - [`DOT-12`](https://pabloaugusto.atlassian.net/browse/DOT-12) -
    desbloquear o `1Password SSH Agent` para GitHub e assinatura local
  - [`DOT-28`](https://pabloaugusto.atlassian.net/browse/DOT-28) -
    destravar checkpoint commit com signer tecnico
## Leitura operacional atual

- `Jira`: pronto para backlog core, issues, comentarios, transicoes e
  configuracoes de projeto cobertas por `Jira Platform`
- `Confluence`: pronto para bootstrap de paginas e documentacao oficial
- `Jira + Confluence`: seed retroativo ja executado e validado no tenant atual
- o repair retroativo mais recente:
  - regravou descricoes e comentarios gerados para normalizar links, narrativa e
    referencias de artefatos do repo
  - promoveu referencias de arquivos versionados para links oficiais do
    `GitHub` em `Jira` e `Confluence`
  - removeu residuos de `paths` locais e de artefatos nao versionados, como o
    `storageState` local do `Playwright`, do material publicado no tenant
  - passou a linkar apenas arquivos rastreados no `Git`, evitando URLs falsas
    para caches, sessao de browser e outros artefatos efemeros
  - passou a valer tambem como contrato perene para novas issues, comentarios e
    paginas sincronizadas
  - depende de `commit checkpoint + push` para que arquivos novos desta
    worktree tenham URL oficial realmente valida no `GitHub`
- `Jira Software board`: layout visual ja alinhado; permanece bloqueado apenas
  o caminho de automacao pela API por gap de scope efetivo e/ou acesso ao
  produto
- `Jira admin modelagem estrutural`: parcialmente desbloqueado no plano
  `Jira Platform`; o unico bloqueio confirmado nesta trilha continua sendo a
  API de `board`

## Implicacao no plano

- a semeadura de `Jira` e `Confluence` pode comecar imediatamente
- por regra-base, a semeadura de `Jira` e `Confluence` nao deve rodar antes de
  o board refletir o workflow oficial
- excecao aprovada pelo usuario em `2026-03-08`:
  - a rodada atual pode semear mesmo com o gap visual do board
  - as proximas rodadas voltam ao bloqueio padrao ate confirmacao explicita do
    layout ou ajuste do flag no modelo
- resultado real dessa excecao:
  - seed executado com sucesso no tenant
  - o bloqueio futuro deixou de depender do layout visual e agora se resume ao
    uso da `Jira Software board API`
- o ajuste fino do board Kanban agora esta concluido na UI; a prioridade
  tecnica residual e fechar a `Jira Software board API`
- o control plane deve usar `Jira v3` e `Confluence v2` como padrao, evitando
  `Confluence v1` no fluxo-base
- a documentacao de rotacao precisa manter o gap de board explicito ate o
  primeiro probe verde em `/rest/agile/1.0/board`
- [`DOT-76`](https://pabloaugusto.atlassian.net/browse/DOT-76) foi concluida
  como analise arquitetural, com pagina oficial
  [`DOT - App Runtime Frontier Analysis`](https://pabloaugusto.atlassian.net/wiki/spaces/DOT/pages/254707273)
  e recomendacao final sincronizada entre repo, Jira e Confluence
