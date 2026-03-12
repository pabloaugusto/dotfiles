# Review And Quality Rules

## Objetivo

Consolidar revisores especializados, QA e gates de qualidade.

## Escopo

- review especializado
- QA
- revisao linguistica consultiva

## Fonte canonica e precedencia

- [`../../AGENTS.md`](../../AGENTS.md)
- [`../../docs/AI-REVIEW-LEDGER.md`](../../docs/AI-REVIEW-LEDGER.md)
- [`../../config/ai/agent-operations.yaml`](../../config/ai/agent-operations.yaml)

## Regras obrigatorias

- Python, PowerShell e automacao exigem revisor especializado
- `pascoalete` e consultivo por padrao, quando estiver `enabled`
- parecer especializado ausente invalida fechamento aplicavel
- QA precisa registrar evidencia

## Startup: o que precisa ser carregado

- revisores obrigatorios por familia
- estado de enablement dos papeis de review

## Delegacao: o que o subagente precisa receber

- arquivos da familia afetada
- criterio de risco
- confirmacao de enablement

## Fallback e Recuperacao

- `pascoalete` reprovado gera pendencia rastreavel quando nao corrigido
- sem revisor habilitado para familia obrigatoria, bloquear `done`

## Enforcement e validacoes

- `task ai:review:check`
- `task ai:validate`
- testes de validator e review

## Artefatos relacionados

- [`../../docs/AI-ORTHOGRAPHY-LEDGER.md`](../../docs/AI-ORTHOGRAPHY-LEDGER.md)
- [`../../config/ai/agent-enablement.yaml`](../../config/ai/agent-enablement.yaml)

## Temas vizinhos

- [`documentation-and-confluence-rules.md`](documentation-and-confluence-rules.md)
- [`worklog-and-lessons-rules.md`](worklog-and-lessons-rules.md)
