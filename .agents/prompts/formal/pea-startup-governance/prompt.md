# Prompt Para Codex - Formalizar Pre-Execution Alignment (PEA) no dotfiles

## Missao

Implementar no repo [`dotfiles`](../../../../README.md) a camada perene de
**Pre-Execution Alignment (PEA)** para reduzir drift entre o pedido humano e a
execucao da IA, integrando essa rotina a governanca real do projeto sem criar
fluxo paralelo nem duplicar enforcement ja existente.

## Regra zero

Antes de criar qualquer demanda nova:

1. verificar no `Jira` se ja existe **issue aberta** cobrindo este tema
2. verificar se ja existe **Epic aberto** aderente ao macro tema
3. reutilizar a issue existente se ela ja cobrir o escopo
4. reutilizar o Epic aberto correto se o tema ja estiver coberto
5. nao criar novo `Epic`
6. se o Epic aberto de governanca de IA ainda for [`DOT-71`](https://pabloaugusto.atlassian.net/browse/DOT-71) e continuar aderente, usar `DOT-71`
7. se houver issue aberta equivalente para startup, alinhamento, continuity ou guardrails, nao duplicar

## Distincao obrigatoria entre camadas

### Startup/restart

Responsavel por releitura integral do contexto canonico quando a sessao reinicia
ou nasce do zero.

### PEA

Responsavel por alinhar entendimento antes da execucao quando houver
ambiguidade, impacto persistente, risco estrutural ou pre-condicao faltante.

### Enforcement

Responsavel por bloquear ou validar a operacao real via hooks, tasks,
validators, reviews, Jira workflow, worklog, lessons e closeout.

Regra obrigatoria:

- o startup nao vira enforcement de Git
- o PEA nao vira substituto de `Jira`, worklog, reviews ou gates
- o enforcement real continua em [`task ai:worklog:check`](../../../../docs/TASKS.md#aiworklogcheck),
  [`task git:governance:check`](../../../../docs/TASKS.md#gitgovernancecheck),
  [`task ai:validate`](../../../../docs/TASKS.md#aivalidate),
  [`task docs:check`](../../../../docs/TASKS.md#docscheck),
  [`task ai:review:check`](../../../../docs/TASKS.md#aireviewcheck),
  [`task ai:lessons:check`](../../../../docs/TASKS.md#ailessonscheck) e
  [`task ai:worklog:close:gate`](../../../../docs/TASKS.md#aiworklogclosegate)

## Modos de execucao

- `fast_lane`: pedido claro, local, reversivel e sem ambiguidade relevante
- `alinhamento_resumido_e_execucao`: impacto moderado, entendimento razoavelmente claro, mas nao trivial
- `aguardando_confirmacao_humana`: mudanca estrutural, persistente ou cross-cutting
- `bloqueado_por_pre_condicao`: falta issue dona, dedupe, startup, branch coerente ou contexto minimo

## Formato padrao do PEA

Quando o PEA for necessario, a IA deve produzir:

1. `Entendimento`
2. `Work item e ownership`
3. `Preflight de dedupe`
4. `Escopo entendido`
5. `Fora de escopo`
6. `Assuncoes`
7. `Riscos ou ambiguidades`
8. `Validacoes previstas`
9. `Modo de execucao`

## Startup/restart: extensao obrigatoria

A camada de startup/restart deve:

- carregar o catalogo de prompt packs em
  [`.agents/prompts/CATALOG.md`](../../CATALOG.md)
- carregar os packs formais aplicaveis em [`.agents/prompts/formal/`](../../formal/)
- expor `pea_status` no relatorio de startup
- distinguir explicitamente `startup`, `PEA` e `enforcement`
- preparar o pacote minimo de delegacao com issue dona, branch atual, startup
  report e classificacao do PEA quando aplicavel

## Regras obrigatorias adicionais

- `Jira` continua sendo a fonte primaria do fluxo vivo
- [`docs/AI-WIP-TRACKER.md`](../../../../docs/AI-WIP-TRACKER.md) continua como fallback contingencial
- `concluir_primeiro` continua significando concluir o WIP atual ou puxar apenas o work item minimo que o destrava
- o bypass humano pode pular a conversa de confirmacao, mas nao pode pular startup obrigatorio, dedupe de issue ou `Epic`, Jira primario, reviews obrigatorios, lessons, worklog e gates
- assuncoes que alterem escopo, ownership, branch, backlog, arquitetura, governanca ou impacto operacional devem ser explicitas
- quando houver delegacao, a classificacao do `PEA`, as assuncoes relevantes e as ambiguidades abertas precisam viajar junto do pacote minimo de contexto do subagente

## Arquivos e areas provaveis de impacto

- [`AGENTS.md`](../../../../AGENTS.md)
- [`docs/AI-STARTUP-GOVERNANCE-MANIFEST.md`](../../../../docs/AI-STARTUP-GOVERNANCE-MANIFEST.md)
- [`docs/AI-STARTUP-AND-RESTART.md`](../../../../docs/AI-STARTUP-AND-RESTART.md)
- [`docs/AI-DELEGATION-FLOW.md`](../../../../docs/AI-DELEGATION-FLOW.md)
- [`docs/TASKS.md`](../../../../docs/TASKS.md)
- [`docs/ai-operating-model.md`](../../../../docs/ai-operating-model.md)
- [`config/ai/contracts.yaml`](../../../../config/ai/contracts.yaml)
- [`config/ai/agent-operations.yaml`](../../../../config/ai/agent-operations.yaml)
- [`scripts/ai_session_startup_lib.py`](../../../../scripts/ai_session_startup_lib.py)
- [`scripts/validate-ai-assets.py`](../../../../scripts/validate-ai-assets.py)
- testes Python correlatos

## Criterios de aceite

1. existir uma camada perene de PEA formalizada no repo
2. `startup`, `PEA` e `enforcement` ficarem claramente separados
3. pedidos triviais continuarem em fast lane
4. pedidos estruturais exigirem alinhamento e confirmacao
5. pedidos sem pre-condicao valida entrarem em bloqueio operacional
6. criacao de issue ou `Epic` respeitar dedupe e reuso do `Epic` aberto
7. o startup passar a contemplar os contratos novos e os antigos sempre que a sessao reiniciar ou nascer do zero
8. o startup expuser explicitamente um bloco `pea_status`
9. subagentes passarem a receber contexto minimo compativel com PEA quando aplicavel
10. docs, contracts, ops, startup e validadores ficarem em paridade
11. houver regressao automatizada cobrindo os cenarios principais

## Validacoes minimas esperadas

- `task ai:startup:session`
- `task ai:worklog:check`
- `task ai:validate`
- `task docs:check`
- `task ai:eval:smoke`
- `task type:check`
- `task ai:review:check`
- `task ai:lessons:check`
- `task ai:worklog:close:gate`

## Instrucao final

Implemente isso como evolucao da governanca viva do repo.

- nao crie framework generico paralelo
- nao crie `Epic` novo
- nao duplique issue existente
- nao misture startup com enforcement
- nao bypass regras reais de Jira, Git, worklog, review, lessons ou closeout
