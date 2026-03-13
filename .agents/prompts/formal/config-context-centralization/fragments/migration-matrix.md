# Matriz De Migracao

## Shape obrigatorio

A matriz versionada deve conter, no minimo:

- `origem`
- `destino`
- `justificativa`
- `owner`
- `status`
- `tipo`
- `observacoes`

## Primeira drenagem obrigatoria

- [config/ai/agents.yaml](../../../../../config/ai/agents.yaml) ->
  futuro `agents.toml` na pasta `config` sob [`.agents/`](../../../../)
- [config/ai/agent-enablement.yaml](../../../../../config/ai/agent-enablement.yaml)
  -> futuro `agents.toml` na pasta `config` sob [`.agents/`](../../../../)
- [config/ai/agent-runtime.yaml](../../../../../config/ai/agent-runtime.yaml) ->
  futuro `agents.toml` na pasta `config` sob [`.agents/`](../../../../)
- chat/startup/orchestration declarativos ->
  futuros `communication.toml`, `startup.toml` e `orchestration.toml` na pasta
  `config` sob [`.agents/`](../../../../)
- reviewer policies ->
  futuro `reviews.toml` na pasta `config` sob [`.agents/`](../../../../)
- [config/ai/platforms.yaml](../../../../../config/ai/platforms.yaml),
  [config/ai/jira-model.yaml](../../../../../config/ai/jira-model.yaml),
  [config/ai/confluence-model.yaml](../../../../../config/ai/confluence-model.yaml)
  e [config/ai/sync-targets.yaml](../../../../../config/ai/sync-targets.yaml)
  permanecem em [config/](../../../../../config/)
- [`.agents/config.toml`](../../../../config.toml) ->
  ponte temporaria para o futuro `config.toml` na pasta `config` sob
  [`.agents/`](../../../../)
