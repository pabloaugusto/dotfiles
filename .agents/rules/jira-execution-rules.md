# Jira Execution Rules

## Objetivo

Centralizar ownership, comentarios estruturados, evidencias e transicoes no
`Jira`.

## Escopo

- comments estruturados
- ownership por papel
- evidencias e handoff
- status do fluxo vivo

## Fonte canonica e precedencia

- [`../../config/ai/contracts.yaml`](../../config/ai/contracts.yaml)
- [`../../config/ai/agent-operations.yaml`](../../config/ai/agent-operations.yaml)
- [`../../config/ai/jira-model.yaml`](../../config/ai/jira-model.yaml)
- [`../../docs/ai-operating-model.md`](../../docs/ai-operating-model.md)

## Regras obrigatorias

- todo toque relevante em issue rastreada precisa de comentario estruturado
- ownership atual e proximo papel devem ficar explicitos
- evidencias objetivas valem mais que resumo generico
- agente desabilitado por config nao pode ser exigido como etapa obrigatoria
  sem override humano rastreavel

## Startup: o que precisa ser carregado

- saude minima do Atlassian
- `cloud_id`, `project_key`, `space_key` e auth mode
- issue dona da rodada

## Delegacao: o que o subagente precisa receber

- issue dona
- comment type esperado
- evidencias minimas e proximo papel

## Fallback e Recuperacao

- `Jira` e a fonte primaria do fluxo vivo
- trackers locais so operam em modo `degraded` ou `recovery`

## Enforcement e validacoes

- [`../../scripts/ai_control_plane_lib.py`](../../scripts/ai_control_plane_lib.py)
- [`../../scripts/ai_jira_apply_lib.py`](../../scripts/ai_jira_apply_lib.py)
- [`../../tests/python/ai_jira_model_test.py`](../../tests/python/ai_jira_model_test.py)

## Artefatos relacionados

- [`../../docs/AI-FALLBACK-LEDGER.md`](../../docs/AI-FALLBACK-LEDGER.md)
- [`../../docs/AI-DELEGATION-FLOW.md`](../../docs/AI-DELEGATION-FLOW.md)
- [`../../docs/AI-SCRUM-MASTER-LEDGER.md`](../../docs/AI-SCRUM-MASTER-LEDGER.md)

## Temas vizinhos

- [`intake-and-backlog-rules.md`](intake-and-backlog-rules.md)
- [`delegation-rules.md`](delegation-rules.md)
- [`review-and-quality-rules.md`](review-and-quality-rules.md)
