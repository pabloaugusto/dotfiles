# Auth, Scopes e Permissoes Atlassian

- Status: `canonico-para-rotacao`
- Data-base: `2026-03-07`
- Relacionados:
  - [`2026-03-07-diagnostico-auth-e-acesso-atlassian.md`](2026-03-07-diagnostico-auth-e-acesso-atlassian.md)
  - [`2026-03-07-parecer-e-plano-inicial.md`](2026-03-07-parecer-e-plano-inicial.md)
  - [`../../config/ai/platforms.yaml`](../../config/ai/platforms.yaml)
  - [`../../docs/secrets-and-auth.md`](../../docs/secrets-and-auth.md)

## Regra canonica por produto

- `Jira`: usar [`REST API v3`](https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/)
- `Confluence`: usar [`REST API v2`](https://developer.atlassian.com/cloud/confluence/rest/v2/)
- `Jira Software board API`: usar a API oficial de board do `Jira Software`
  quando os scopes especificos estiverem liberados
- evitar `Confluence REST v1 /wiki/rest/api/space/...` para o fluxo-base; esse
  caminho exige escopo adicional e hoje nao e necessario para o control plane

## Token amplo atual

Snapshot documentado a partir do token informado pelo usuario e validado contra
o tenant em `2026-03-07`.

### Manage

- `manage:jira-configuration`
- `manage:jira-project`
- `manage:jira-webhook`
- `write:product:jira-service-management`

### Read

- `read:project:jira`
- `read:board-scope:jira-software`
- `read:board-scope.admin:jira-software`
- `read:comment:confluence`
- `read:jira-user`
- `read:jira-work`
- `read:page:confluence`
- `read:space:confluence`

### Search

- `search:confluence`

### Write

- `write:attachment:confluence`
- `write:board-scope:jira-software`
- `write:board-scope.admin:jira-software`
- `write:comment:confluence`
- `write:page:confluence`
- `write:attachment:jira`
- `write:build-info:jira`
- `write:build:jira-software`
- `write:cmdb-schema:jira`
- `write:comment:jira`
- `write:comment.property:jira`
- `write:custom-field-contextual-configuration:jira`
- `write:dashboard:jira`
- `write:dashboard.property:jira`
- `write:deployment-info:jira`
- `write:deployment:jira-software`
- `write:dev-info:jira`
- `write:document-info:jira`
- `write:epic:jira-software`
- `write:field-configuration-scheme:jira`
- `write:field-configuration:jira`
- `write:field:jira`
- `write:field.default-value:jira`
- `write:field.option:jira`
- `write:issue-adjustments:jira`
- `write:issue-link:jira`
- `write:issue-type-screen-scheme:jira`
- `write:issue-type:jira`
- `write:issue-type.property:jira`
- `write:issue:jira`
- `write:issue:jira-software`
- `write:issue.property:jira`
- `write:issue.watcher:jira`
- `write:permission:jira`
- `write:product:jira-service-management`
- `write:project-role:jira`
- `write:project:jira`
- `write:remote-link:jira-software`
- `write:jira-work`

Observacao:

- a categoria exibida pela UI da Atlassian para alguns itens usa `Manage` e
  `Write` de forma misturada; o agrupamento acima replica o snapshot informado
  pelo usuario para facilitar futuras rotacoes

## Scopes minimos do token

### Jira core

Necessarios para ler projeto, criar issue, comentar, transicionar e operar o
backlog base:

- `read:jira-user`
- `read:jira-work`
- `write:jira-work`

### Jira administracao e customizacao

Necessarios para modelar projeto, componentes, campos e configuracoes
administrativas do escopo:

- `manage:jira-project`
- `manage:jira-configuration`

### Jira Software board

Necessarios para ler, criar e administrar board Kanban/Scrum:

- `read:project:jira`
- `read:board-scope:jira-software`
- `write:board-scope:jira-software`
- `read:board-scope.admin:jira-software`
- `write:board-scope.admin:jira-software`

Observacao operacional:

- a documentacao oficial do `Jira Software board API` exige `read:project:jira`
  em conjunto com os scopes de `board`; o token amplo anterior nao listava esse
  scope, o que explica o `401 Unauthorized; scope does not match`
- em `2026-03-07`, o tenant respondeu `401 Unauthorized; scope does not match`
  em [`/rest/agile/1.0/board`](https://developer.atlassian.com/cloud/jira/software/rest/api-group-board/)
  mesmo com `Jira core`, `workflow search`, `issue type scheme` e `field search`
  verdes; isso indica gap real no token efetivo para `board`, no acesso ao
  produto `Jira Software` ou em ambos

### Confluence core

Necessarios para lookup de spaces, leitura de paginas, criacao/edicao de
paginas e busca:

- `read:space:confluence`
- `read:page:confluence`
- `write:page:confluence`
- `search:confluence`

### Confluence opcional

Necessarios apenas se o fluxo passar a escrever comentarios ou anexos:

- `read:comment:confluence`
- `write:comment:confluence`
- `write:attachment:confluence`

## Escopo legado que so entra por excecao

Se algum fluxo realmente precisar continuar usando
[`Confluence REST API v1 - Space`](https://developer.atlassian.com/cloud/confluence/rest/v1/api-group-space/),
o escopo granular oficial inclui `read:space-details:confluence`.

No control plane atual, isso deve ser evitado. O fluxo-base foi ajustado para
`Confluence v2`, onde o lookup de space usa `GET /wiki/api/v2/spaces`.

## Permissoes do principal

Scope de token nao substitui permissao do principal. A service account precisa:

- acesso ao produto `Jira`
- acesso ao produto `Jira Software` para operar board
- acesso ao produto `Confluence`
- permissao global `Administer Jira` se a rodada for customizar status,
  workflows, campos ou esquemas
- permissao de projeto suficiente para:
  - ver projeto
  - criar issues
  - editar issues
  - comentar
  - transicionar
  - criar subtasks
  - linkar issues
- permissao de `space` no `Confluence` para:
  - ver paginas
  - criar paginas
  - editar paginas

## Observacoes do tenant atual

- o secret configurado no overlay local derivado de
  [`../../config/ai/platforms.local.yaml.tpl`](../../config/ai/platforms.local.yaml.tpl)
  resolve `space_key = DOT`
- no tenant real, o `space` devolvido pela API v2 possui:
  - `key = DO`
  - `currentActiveAlias = DOT`
  - `_links.webui = /spaces/DOT`
- portanto, o valor `DOT` no secret esta correto para a sua operacao atual; o
  adapter precisa aceitar alias ativo, nao apenas `key` literal
- o token amplo atual foi validado com sucesso para:
  - `Jira core`
  - `Confluence v2`
  - `GET /rest/api/3/workflow/search`
  - `GET /rest/api/3/issuetypescheme/project`
  - `GET /rest/api/3/field/search`
- o unico gap confirmado no momento continua sendo
  [`/rest/agile/1.0/board`](https://developer.atlassian.com/cloud/jira/software/rest/api-group-board/)
  com `401 Unauthorized; scope does not match`

## Checklist objetivo para destravar DOT-65

Usar esta sequencia quando a meta for liberar o board do `Jira Software` no
tenant atual.

1. Confirmar na service account acesso real ao produto `Jira Software`, nao
   apenas a `Jira`.
2. Confirmar que o token ativo continua contendo, no snapshot efetivo:
   - `read:project:jira`
   - `read:board-scope:jira-software`
   - `write:board-scope:jira-software`
   - `read:board-scope.admin:jira-software`
   - `write:board-scope.admin:jira-software`
3. Se o token for rotacionado, repetir `task ai:atlassian:check`.
4. Rodar um probe dedicado em `GET /rest/agile/1.0/board`.
5. So depois de o probe ficar verde:
   - alinhar o layout visual do board
   - confirmar mapeamento das colunas
   - marcar `project.target_board.layout_confirmed=true` em
     [`../../config/ai/jira-model.yaml`](../../config/ai/jira-model.yaml)

Diagnostico tecnico que embasa esse checklist:

- `gateway + Bearer`: `401 Unauthorized; scope does not match`
- `gateway + Basic`: `401 Unauthorized`
- `site + Basic`: `401 Client must be authenticated to access this resource`
- `site + Bearer`: `403 Failed to parse Connect Session Auth Token`

Conclusao operacional:

- `gateway + Bearer` continua sendo o modo canonico para o control plane
- o gap residual de `DOT-65` parece estar em scope, entitlement ou acesso
  efetivo ao produto, nao apenas em base path

## Checklist de rotacao futura

1. Rotacionar o token no `1Password` mantendo o mesmo ref consumido pelo
   overlay local derivado de
   [`../../config/ai/platforms.local.yaml.tpl`](../../config/ai/platforms.local.yaml.tpl).
2. Garantir os scopes de `Jira core`, `Jira administracao`, `Jira Software
   board` e `Confluence core`.
3. Confirmar que a service account continua com acesso aos tres produtos:
   `Jira`, `Jira Software` e `Confluence`.
4. Rodar `task ai:atlassian:check`.
5. Validar separadamente o board com probe em `/rest/agile/1.0/board`.
6. Registrar qualquer gap residual neste diretorio antes de seguir para novas
   escritas automatizadas.

Observacao:

- a partir desta rodada, `task ai:atlassian:check` ja publica no payload a
  matriz de probes do board (`gateway_bearer`, `gateway_basic`, `site_basic`,
  `site_bearer`), para que o diagnostico de `DOT-65` nao dependa de tentativas
  manuais fora do fluxo canonico

## Operacao recomendada do 1Password para automacao

Para evitar `Too many requests` do `op`:

- resolver refs `op://...` em lote com `op run` no inicio da execucao
- evitar multiplos `op read` consecutivos para campos do mesmo item
- usar `op item get --format json` como fallback de item unico quando o batch
  nao estiver disponivel
- manter cache apenas em memoria durante o processo
- nao paralelizar probes remotos que dependam do mesmo item do `1Password`
  enquanto o cofre estiver quente

No control plane Atlassian, isso significa:

- uma unica resolucao em lote do item `atlassian` por processo
- distribuicao interna dos valores resolvidos para `Jira` e `Confluence`
- reexecucao remota em serie quando houver sinais de rate limit do CLI
