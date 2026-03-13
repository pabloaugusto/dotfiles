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

- [.agents/config/agents.toml](../../../../../.agents/config/agents.toml) ->
  futuro `agents.toml` na pasta `config` sob [`.agents/`](../../../../)
- [.agents/config/agents.toml](../../../../../.agents/config/agents.toml)
  -> futuro `agents.toml` na pasta `config` sob [`.agents/`](../../../../)
- [.agents/config/agents.toml](../../../../../.agents/config/agents.toml) ->
  futuro `agents.toml` na pasta `config` sob [`.agents/`](../../../../)
- chat/startup/orchestration declarativos ->
  futuros `communication.toml`, `startup.toml` e `orchestration.toml` na pasta
  `config` sob [`.agents/`](../../../../)
- reviewer policies ->
  futuro `reviews.toml` na pasta `config` sob [`.agents/`](../../../../)
- [config/platforms.yaml](../../../../../config/platforms.yaml),
  [config/jira-model.yaml](../../../../../config/jira-model.yaml),
  [config/confluence-model.yaml](../../../../../config/confluence-model.yaml)
  e [config/sync-targets.yaml](../../../../../config/sync-targets.yaml)
  permanecem em [config/](../../../../../config/)
- [`.agents/config.toml`](../../../../config.toml) ->
  manifesto operacional complementar da camada IA
