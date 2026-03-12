## Evidencias e Racionais

### Evidencias versionadas

- [`config/ai/agent-operations.yaml`](../../../../../config/ai/agent-operations.yaml)
  ja exige contrato de chat antes da primeira mensagem operacional ao usuario
- [`config/ai/contracts.yaml`](../../../../../config/ai/contracts.yaml) ja
  marca trabalho sem startup integral como rejeitavel
- [`scripts/ai_session_startup_lib.py`](../../../../../scripts/ai_session_startup_lib.py)
  ja carrega `display_name`, pack formal de startup e relatorio operacional
- [`config/ai/agents.yaml`](../../../../../config/ai/agents.yaml) ainda nao
  declara `startup gatekeeper` dedicado
- [`docs/AI-AGENTS-CATALOG.md`](../../../../../docs/AI-AGENTS-CATALOG.md)
  ainda nao mapeia ownership explicito para a primeira resposta operacional da
  sessao

### Racionais obrigatorios

- regras normativas ja existem e nao precisam ser reinventadas
- o gap principal esta no bloqueio tecnico da primeira resposta operacional
- um agente dedicado sem `clearance` real e insuficiente
- `clearance` sem papel dedicado enfraquece ownership e auditoria
- a combinacao correta e `agente especializado + gate tecnico + auditoria do Scrum Master`
