# Config Reference (arquivos estritos)

Guia de referência para arquivos de configuração que **não** suportam comentários
inline seguros (JSON/TOML/etc.) ou que devem permanecer enxutos.

## Objetivo

- documentar significado de chaves sem quebrar sintaxe de consumidores
- reduzir custo de manutenção para humanos e agentes de IA

## [`bootstrap/user-config.yaml`](../bootstrap/user-config.yaml.tpl)

Uso:

- fonte única local de configuração do bootstrap (wizard + sincronização de derivados),
  criada localmente a partir de [`bootstrap/user-config.yaml.tpl`](../bootstrap/user-config.yaml.tpl)

Pontos críticos (OneDrive Windows):

- `paths.windows.onedrive_enabled`: liga/desliga dependência de OneDrive
- `paths.windows.onedrive_root`: root desejada (auto-detect quando vazio)
- `paths.windows.onedrive_auto_migrate`: tentativa best-effort de migração automática
- `paths.windows.links_profile_*`: origens de symlinks no perfil
- `paths.windows.links_drive_enabled` + `links_drive_*`: atalhos opcionais em drive raiz
- `paths.windows.profile_links_migrate_content`: migra conteúdo antes de criar links das pastas padrão
- `paths.windows.profile_links_*`: ativa e define destino de pastas padrão (`Documents`, `Desktop`, `Downloads`, `Pictures`, `Videos`, `Music`, `Contacts`, `Favorites`, `Links`)

Observação:

- mudanças nesses campos impactam diretamente [`bootstrap/bootstrap-windows.ps1`](../bootstrap/bootstrap-windows.ps1),
  incluindo os gates de validação pós-bootstrap.

Pontos críticos (Git/signing):

- `git.signing_key`: signer humano padrão, mantido em paralelo ao 1Password SSH Agent
- `git.automation_signing_key_ref`: ref opcional do 1Password para a chave
  pública do signer técnico aplicado por worktree

## [`config/ai/platforms.yaml`](../config/ai/platforms.yaml)

Uso:

- fonte de verdade dev-time para plataformas externas da camada de IA
- separada de [`bootstrap/`](../bootstrap/) e [`df/`](../df/) por nao ser
  runtime materializado na maquina
- intencionalmente generica para que outros repos consumam o mesmo contrato
  sem herdar refs do `dotfiles`

Overlay local opcional:

- [`config/ai/platforms.local.yaml.tpl`](../config/ai/platforms.local.yaml.tpl):
  template versionado para materializacao local ignorada no Git
- o arquivo local derivado desse template funciona como override dev-time
  opcional, pensado para refs `op://...` ou ajustes por projeto sem acoplar o
  contrato base ao repo

Pontos criticos:

- `platforms.atlassian.auth.site_url`: aceita literal, `env://VAR` ou outro
  seletor de provider suportado; em `service-account-api-token` ela passa a ser
  referencia para links/UI e nao para o endpoint REST principal
- `platforms.atlassian.auth.email`, `token`, `service_account` e `cloud_id`:
  aceitam `env://VAR`, `op://...` ou literal, com precedencia do overlay local
- `platforms.atlassian.auth.mode = service-account-api-token`: usa
  `api.atlassian.com/ex/{product}/{cloud_id}` com `Bearer token`, conforme o
  contrato atual da Atlassian para tokens com escopo de service account
- refs `op://...` da trilha Atlassian devem ser resolvidos em lote na borda do
  processo; o control plane prefere `op run`, usa `op item get` como fallback
  por item e evita `op read` em cascata
- `platforms.atlassian.jira.project_key`: projeto padrao para backlog
- `platforms.atlassian.confluence.space_key`: key canonica do space para
  documentacao; neste projeto o valor oficial e `DOT`
- referencia de rotacao e escopos:
  [`docs/atlassian-ia/2026-03-07-atlassian-auth-scopes-and-permissions.md`](atlassian-ia/2026-03-07-atlassian-auth-scopes-and-permissions.md)

## [`config/ai/agents.yaml`](../config/ai/agents.yaml)

Uso:

- liga/desliga papeis operacionais e capacidades opcionais do modelo multiagente

Pontos criticos:

- `enabled`: ativa ou desativa o papel no fluxo-base
- `required`: indica se o papel faz parte do nucleo obrigatorio
- `ai-browser-validator`: capacidade opcional para evidencias via `Playwright`
- papeis como design, UX/CRO e SEO permanecem opcionais por dominio
- `ai-documentation-agent`: governa a linkagem bidirecional `Jira <-> Confluence`
  como contrato perene de rastreabilidade
  e a governanca `artifact-first -> sync`

## [`config/ai/agent-operations.yaml`](../config/ai/agent-operations.yaml)

Uso:

- define o passo a passo operacional de cada papel do time em `Jira` e
  `Confluence`
- separa identidade de papel em [`config/ai/agents.yaml`](../config/ai/agents.yaml)
  do contrato de atuacao efetiva nas ferramentas Atlassian

Pontos criticos:

- `global_contract.jira.required_comment_fields`: campos minimos do comentario
  estruturado por agente
- `global_contract.jira.accepted_evidence`: formatos de prova aceitos para que
  a atuacao seja considerada valida
- `roles.*.jira.transitions_owned`: transicoes que cada papel pode conduzir
- `roles.*.required_evidence`: evidencia minima que o papel deve anexar ou
  referenciar
- `roles.*.operating_steps`: passo a passo humano-legivel que sera a base dos
  futuros agentes operacionais

## [`config/ai/contracts.yaml`](../config/ai/contracts.yaml)

Uso:

- concentra contratos operacionais da migracao Jira + Confluence

Pontos criticos:

- `backlog.issue_creation_policy`: somente o `AI Product Owner` cria issues
  principais
- `documentation.require_bidirectional_links`: obriga vinculo entre issue e
  pagina sempre que a demanda gerar trabalho nas duas plataformas
- `documentation.linking_contract`: define ownership e regras de enforcement da
  linkagem bidirecional governada pelo `AI Documentation Agent`
- `documentation.artifact_governance`: exige que schema, endpoint catalog e
  plano de sync existam no repo antes de apply e semeadura
- `documentation.artifact_governance.migration_bundle`: exige bundle auditavel
  em `.zip`, pronto para anexo na issue correspondente do `Jira`
- `agent_activity`: endurece o contrato de comentarios estruturados com
  evidencia obrigatoria antes de handoff, transicao e `Done`
- `workflow.always_enabled_columns`: fluxo-base obrigatorio
- `workflow.optional_columns`: colunas condicionais por capacidade
- `workflow.evidence_comment_types`: inclui `documentation-link` para registrar
  criacao/atualizacao de pagina vinculada
- `testing.optional_layers`: malhas adicionais de evidencia, como browser validation

## [`config/ai/jira-model.yaml`](../config/ai/jira-model.yaml)

Uso:

- define o estado alvo declarativo do projeto `Jira`, incluindo board, fluxo,
  fields, components, labels e dashboards

Pontos criticos:

- `metadata.model_id`: identificador neutro do pilot de control plane, sem
  acoplamento a runtime de `dotfiles`
- `project.target_board`: contrato alvo do board Kanban
- `workflow.statuses`: statuses que precisam existir antes da semeadura retroativa
- `fields.custom_fields`: campos minimos necessarios para a operacao multiagente
- `workflow.name` e `workflow.scheme_name`: identificadores declarativos do
  workflow e do workflow scheme que serao aplicados no tenant
- `fields.custom_fields[].enabled_when_role`: permite que campos opcionais de
  design, UX ou SEO so entrem quando a capability correspondente estiver ativa
- use [`docs/atlassian-ia/2026-03-07-jira-configuration-export.md`](atlassian-ia/2026-03-07-jira-configuration-export.md)
  para ver o delta ao vivo do tenant

## [`config/ai/confluence-model.yaml`](../config/ai/confluence-model.yaml)

Uso:

- define a arquitetura de informacao alvo do `Confluence` para a trilha
  `Jira + Confluence + repo`

Pontos criticos:

- `space.accepted_keys`: lista de keys canonicas aceitas pelo modelo; neste
  projeto a chave oficial e somente `DOT`
- `page_tree`: define hub, paginas de schema, operacao e migration plan
- `sync_contract.mode = repo-first-then-sync`: o repo nasce primeiro; o
  `Confluence` recebe a materializacao oficial depois

## [`vendor/atlassian/`](../vendor/atlassian/README.md)

Uso:

- congela os specs OpenAPI oficiais de `Jira Cloud` e `Confluence Cloud` para
  codegen, auditoria e comparacao de drift

Pontos criticos:

- os specs devem ser vendorizados antes de qualquer geracao de client
- `manifest.json` deve registrar a origem oficial e o momento da captura
- `Jira Product Discovery` segue tratado como extensao operacional do spec de
  `Jira Cloud` enquanto nao houver spec publico separado

## [`df/windows-terminal/settings.json`](../df/windows-terminal/settings.json)

Uso:

- configura perfis, aparência, fontes e atalhos do Windows Terminal
- é linkado durante bootstrap Windows

Pontos críticos:

- perfil PowerShell e perfil WSL
- fonte Nerd Font compatível com prompt
- actions/keybindings que impactam produtividade diária

## [`df/vscode/settings.json`](../df/vscode/settings.json)

Uso:

- define comportamento editor, terminal integrado, extensões e UX

Pontos críticos:

- integração com formatter/linter
- terminal default profile
- opções que afetam desempenho de workspace grande

## [`df/vscode/keybindings.json`](../df/vscode/keybindings.json)

Uso:

- customizações de atalhos

Pontos críticos:

- atalhos que colidem com defaults do VS Code
- atalhos críticos de navegação/build

## [`df/vscode/mcp.json`](../df/vscode/mcp.json)

Uso:

- configuração de integração MCP do ambiente local
- placeholder neutro e válido quando não houver servidores configurados (`{}`)

Pontos críticos:

- caminhos locais válidos
- políticas de segurança para ferramentas externas

## [`df/oh-my-posh/pablo.omp.json`](../df/oh-my-posh/pablo.omp.json)

Uso:

- layout visual do prompt

Pontos críticos:

- performance do prompt (segmentos caros)
- ícones/fonte compatível no terminal

## [`df/config/atuin/config.toml`](../df/config/atuin/config.toml)

Uso:

- histórico shell sincronizado/consultável

Pontos críticos:

- política de sync
- retenção e privacidade do histórico

## [`df/secrets/dotfiles.sops.yaml`](../df/secrets/dotfiles.sops.yaml)

Uso:

- regras de criptografia para `sops+age`

Pontos críticos:

- `creation_rules.path_regex` cobrindo arquivos corretos
- `age` recipient atualizado
- `encrypted_regex` coerente com seu schema de secrets

## Boas práticas gerais

- validar JSON/TOML/YAML após qualquer alteração
- manter documentação sincronizada com fluxo real de bootstrap
- não usar comentários inválidos em formatos estritos
