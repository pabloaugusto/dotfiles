# AI Chat Contracts Register

## Objetivo

Registrar contratos, acordos e definicoes nascidos no chat que ainda nao foram
promovidos por completo para a governanca oficial versionada do repo.

## Regra de uso

- toda regra relevante nascida no chat e ainda nao perenizada deve entrar aqui
- este registro e fonte obrigatoria de leitura em startup e restart da IA
- quando houver itens pendentes, a sessao de IA deve avisar o usuario e listar
  quais contratos ainda aguardam promocao definitiva
- cada item deve apontar para o **work item** do `Jira` dono da promocao quando
  ele ja existir
- quando o contrato virar governanca oficial, o item sai da fila pendente e vai
  para o historico de promocoes

## Pendentes

<!-- ai-chat-contracts:pending:start -->
| ID | Contrato resumido | Evidencia factual de ausencia na auditoria DOT-116 | Work item dono | Destino perene esperado | Status |
| --- | --- | --- | --- | --- | --- |
| CHAT-005 | Criar dicionario vivo de terminologia agil para os agentes, com preferencia por termos como **fatia de incremento testavel** e eliminacao de termos improprios como `corte` e `checkpoint` quando houver equivalente agil melhor. | A auditoria [DOT-133: Cruzar backlog vivo e pendencias documentais com o Jira](https://pabloaugusto.atlassian.net/browse/DOT-133) confirmou que o contrato ainda nao virou artefato perene proprio, apesar de a terminologia ja aparecer em varios docs. | [DOT-136: Formalizar dicionario vivo de terminologia agil dos agentes](https://pabloaugusto.atlassian.net/browse/DOT-136) | cards, docs de governanca e guia idiomatico compartilhado | pendente |
<!-- ai-chat-contracts:pending:end -->

## Promovidos

<!-- ai-chat-contracts:promoted:start -->
| ID | Contrato resumido | Promovido em | Evidencia |
| --- | --- | --- | --- |
| CHAT-000 | Retomadas sem continuidade confiavel exigem releitura integral do manifest de governanca antes de qualquer operacao relevante. | [DOT-116: Criar procedimento vivo de startup e restart de IA](https://pabloaugusto.atlassian.net/browse/DOT-116) | [`AGENTS.md`](../AGENTS.md), [`config/ai/contracts.yaml`](../config/ai/contracts.yaml), [`docs/ai-operating-model.md`](ai-operating-model.md) e [`docs/AI-STARTUP-GOVERNANCE-MANIFEST.md`](AI-STARTUP-GOVERNANCE-MANIFEST.md) |
| CHAT-001 | Formalizar o **Scrum Master** como agente de enforcement continuo de governanca, fiscalizacao do board, logs de inconformidade e cobranca de aderencia de todos os agentes. | [DOT-115: Formalizar agente Scrum Master de enforcement continuo de governanca](https://pabloaugusto.atlassian.net/browse/DOT-115), [DOT-124: Formalizar log perene de inconformidades e cerimonias do Scrum Master](https://pabloaugusto.atlassian.net/browse/DOT-124) e [DOT-131: Endurecer enforcement efetivo do Scrum Master e das cerimonias](https://pabloaugusto.atlassian.net/browse/DOT-131) | [`.agents/cards/ai-scrum-master.md`](../.agents/cards/ai-scrum-master.md), [`.agents/registry/ai-scrum-master.toml`](../.agents/registry/ai-scrum-master.toml), [`docs/AI-SCRUM-MASTER-LEDGER.md`](AI-SCRUM-MASTER-LEDGER.md) e [`docs/ai-operating-model.md`](ai-operating-model.md) |
| CHAT-002 | Tornar o **Tech Lead** o revisor oficial de todo **PR** ou origem equivalente, com aprovacao ou reprovacao baseada nos criterios do repo. | [DOT-117: Formalizar AI Tech Lead como reviewer obrigatorio de PR e revisao oficial equivalente](https://pabloaugusto.atlassian.net/browse/DOT-117) e [DOT-133: Cruzar backlog vivo e pendencias documentais com o Jira](https://pabloaugusto.atlassian.net/browse/DOT-133) | [`.agents/cards/ai-tech-lead.md`](../.agents/cards/ai-tech-lead.md), [`.agents/registry/ai-tech-lead.toml`](../.agents/registry/ai-tech-lead.toml), [`config/ai/agent-operations.yaml`](../config/ai/agent-operations.yaml), [`config/ai/agents.yaml`](../config/ai/agents.yaml), [`config/ai/reviewer-policies.yaml`](../config/ai/reviewer-policies.yaml) e [`docs/ai-operating-model.md`](ai-operating-model.md) |
| CHAT-003 | Humanizar a operacao com apelidos perenes dos agentes em cards, chat e `Jira` quando houver apelido oficial. | [DOT-118: Versionar e aplicar apelidos perenes dos agentes](https://pabloaugusto.atlassian.net/browse/DOT-118) e [DOT-133: Cruzar backlog vivo e pendencias documentais com o Jira](https://pabloaugusto.atlassian.net/browse/DOT-133) | [`config/ai/contracts.yaml`](../config/ai/contracts.yaml), [`config/ai/agents.yaml`](../config/ai/agents.yaml), [`docs/ai-operating-model.md`](ai-operating-model.md), [`.agents/registry/ai-product-owner.toml`](../.agents/registry/ai-product-owner.toml), [`.agents/registry/ai-tech-lead.toml`](../.agents/registry/ai-tech-lead.toml), [`.agents/cards/ai-product-owner.md`](../.agents/cards/ai-product-owner.md) e [`.agents/cards/ai-tech-lead.md`](../.agents/cards/ai-tech-lead.md) |
| CHAT-004 | Ler o **board** da direita para a esquerda, priorizar terminar antes de comecar e permitir nova puxada apenas quando ela destravar diretamente o WIP ativo. | [DOT-127: Ajustar regra de concluir primeiro para permitir puxar item desbloqueador ativo](https://pabloaugusto.atlassian.net/browse/DOT-127) | [`AGENTS.md`](../AGENTS.md), [`config/ai/contracts.yaml`](../config/ai/contracts.yaml), [`config/ai/jira-model.yaml`](../config/ai/jira-model.yaml), [`docs/ai-operating-model.md`](ai-operating-model.md), [`docs/AI-WIP-TRACKER.md`](AI-WIP-TRACKER.md) e [`docs/AI-STARTUP-AND-RESTART.md`](AI-STARTUP-AND-RESTART.md) |
| CHAT-006 | Formalizar **cerimonias** ageis versionadas, com schema, logs em Markdown e rastreabilidade em `Confluence`, com **retrospectiva** obrigatoria ao fim de cada branch fechada. | [DOT-121: Formalizar cerimonias ageis versionadas e retrospectiva por branch](https://pabloaugusto.atlassian.net/browse/DOT-121) e [DOT-131: Endurecer enforcement efetivo do Scrum Master e das cerimonias](https://pabloaugusto.atlassian.net/browse/DOT-131) | [`.agents/cerimonias/README.md`](../.agents/cerimonias/README.md), [`.agents/cerimonias/retrospectiva.yaml`](../.agents/cerimonias/retrospectiva.yaml), [`.agents/cerimonias/logs/retrospectiva-template.md`](../.agents/cerimonias/logs/retrospectiva-template.md), [`docs/AI-SCRUM-MASTER-LEDGER.md`](AI-SCRUM-MASTER-LEDGER.md) e [`docs/ai-operating-model.md`](ai-operating-model.md) |
| CHAT-007 | Antes de criar `issue`, verificar duplicidade; antes de criar demanda nao-`Epic`, reutilizar `Epic` aberto aderente; antes de criar novo `Epic`, assegurar que nao existe `Epic` aberto para tratar o tema; bypass so com ordem humana ou consulta previa, com fallback autonomo apos 3 minutos e justificativa no `Jira`. | [DOT-175: Formalizar preflight obrigatorio de reuse de Epic e dedupe de issue no intake](https://pabloaugusto.atlassian.net/browse/DOT-175) | [`AGENTS.md`](../AGENTS.md), [`config/ai/contracts.yaml`](../config/ai/contracts.yaml), [`config/ai/jira-model.yaml`](../config/ai/jira-model.yaml), [`config/ai/agent-operations.yaml`](../config/ai/agent-operations.yaml), [`.agents/cards/ai-product-owner.md`](../.agents/cards/ai-product-owner.md), [`.agents/cards/ai-scrum-master.md`](../.agents/cards/ai-scrum-master.md) e [`docs/ai-operating-model.md`](ai-operating-model.md) |
<!-- ai-chat-contracts:promoted:end -->
