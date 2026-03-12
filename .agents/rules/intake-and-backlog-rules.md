# Intake And Backlog Rules

## Objetivo

Governar intake, dedupe de demanda e reuse de `Epic`.

## Escopo

- criacao de issue
- reuse de `Epic`
- leitura do board e `concluir_primeiro`

## Fonte canonica e precedencia

- [`../../AGENTS.md`](../../AGENTS.md)
- [`../../config/ai/contracts.yaml`](../../config/ai/contracts.yaml)
- [`../../config/ai/agent-operations.yaml`](../../config/ai/agent-operations.yaml)
- [`../../config/ai/jira-model.yaml`](../../config/ai/jira-model.yaml)

## Regras obrigatorias

- antes de criar demanda, verificar issue aberta equivalente
- antes de criar demanda nao-`Epic`, verificar `Epic` aberto aderente
- `concluir_primeiro` significa concluir ou destravar primeiro
- o board e lido da direita para a esquerda

## Startup: o que precisa ser carregado

- regra de dedupe e reuse de `Epic`
- `Jira` como fonte primaria do backlog vivo
- WIP atual e work item desbloqueador minimo

## Delegacao: o que o subagente precisa receber

- issue dona
- posicao atual do item no fluxo
- restricao de nao puxar demanda nova sem relacao com o WIP ativo

## Fallback e Recuperacao

- tracker local so entra quando o modo cair para fallback explicito
- bypass de dedupe ou `Epic` exige comentario rastreavel no `Jira`

## Enforcement e validacoes

- [`../../scripts/ai-prompt-governance.py`](../../scripts/ai-prompt-governance.py)
- [`../../tests/python/ai_assets_validator_test.py`](../../tests/python/ai_assets_validator_test.py)

## Artefatos relacionados

- [`../../docs/AI-WIP-TRACKER.md`](../../docs/AI-WIP-TRACKER.md)
- [`../../ROADMAP.md`](../../ROADMAP.md)
- [`../../docs/ROADMAP-DECISIONS.md`](../../docs/ROADMAP-DECISIONS.md)

## Temas vizinhos

- [`jira-execution-rules.md`](jira-execution-rules.md)
- [`worklog-and-lessons-rules.md`](worklog-and-lessons-rules.md)
- [`scrum-and-ceremonies-rules.md`](scrum-and-ceremonies-rules.md)

