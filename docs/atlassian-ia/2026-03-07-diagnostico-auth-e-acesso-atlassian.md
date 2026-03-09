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
    `66` issues (`DOT-1` a `DOT-66`)
  - `Confluence`: `24` paginas oficiais sincronizadas e verificadas por API
    apos o docs sync dedicado
  - total bruto atual visivel no `space`: `25` paginas, incluindo a pagina
    nativa `dotfiles Home` fora da arvore oficial do control plane
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
- o board visivel na UI do projeto `DOT` continua em drift estrutural:
  - colunas default ainda usam `Selected for development` e `In progress`
  - statuses do workflow oficial (`Refinement`, `Ready`, `Doing`, `Testing`,
    `Review`, `Changes Requested`) aparecem como `Unmapped statuses`
  - a UI mostra o erro `This status isn't available in any workflows used by this board`
- o backlog oficial agora possui um item dedicado para esse gap:
  - [`DOT-65`](https://pabloaugusto.atlassian.net/browse/DOT-65) -
    normalizacao do layout do board ao workflow oficial
- a ativacao do browser validator ficou rastreada separadamente em:
  - [`DOT-66`](https://pabloaugusto.atlassian.net/browse/DOT-66) -
    validacao visual via `Playwright` apos estabilizacao da fase base
- a primeira tentativa real de `Playwright` nesta trilha ficou bloqueada por
  fronteira de autenticacao browser:
  - a sessao isolada do navegador foi redirecionada para
    [`id.atlassian.com/login`](https://id.atlassian.com/login)
  - a evidencia visual foi anexada em
    [`DOT-66`](https://pabloaugusto.atlassian.net/browse/DOT-66)
  - o proximo passo para essa capacidade e prover bootstrap de sessao
    autenticada antes de reexecutar a validacao visual
- o tenant reaproveitou o status global `DOING` para os itens em execucao:
  - isso nao impede a semeadura
  - mas confirma que a normalizacao visual do board continua pendente
## Leitura operacional atual

- `Jira`: pronto para backlog core, issues, comentarios, transicoes e
  configuracoes de projeto cobertas por `Jira Platform`
- `Confluence`: pronto para bootstrap de paginas e documentacao oficial
- `Jira + Confluence`: seed retroativo ja executado e validado no tenant atual
- `Jira Software board`: ainda bloqueado por gap de scope efetivo e/ou acesso
  ao produto, com drift adicional no layout do board atual
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
  - o bloqueio futuro continua ativo por padrao na CLI de seed e no modelo
- o ajuste fino do board Kanban continua como proxima prioridade tecnica e
  depende de fechar a `Jira Software board API` e remover o layout legado com
  statuses default presos nas colunas
- o control plane deve usar `Jira v3` e `Confluence v2` como padrao, evitando
  `Confluence v1` no fluxo-base
- a documentacao de rotacao precisa manter o gap de board explicito ate o
  primeiro probe verde em `/rest/agile/1.0/board`
