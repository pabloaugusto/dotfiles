# Sync Foundation Rules

## Objetivo

Definir a fundacao de sync duravel entre repo, outbox local e fonte remota.

## Escopo

- outbox local
- ack, retry e dead-letter
- publication remota elegivel

## Fonte canonica e precedencia

- [`../../docs/ai-sync-foundation.md`](../../docs/ai-sync-foundation.md)
- [`../../config/ai/sync-targets.yaml`](../../config/ai/sync-targets.yaml)
- [`../../config/ai/contracts.yaml`](../../config/ai/contracts.yaml)

## Regras obrigatorias

- cache nao vira fonte de verdade duravel
- nenhum dominio cria outbox paralelo
- publication remota exige `ack` antes de compaction local
- dominios especializados consomem a fundacao oficial

## Startup: o que precisa ser carregado

- manifest de sync
- workspace id e runtime ids relevantes
- estado de fallback quando houver publication remota

## Delegacao: o que o subagente precisa receber

- classe do artefato
- manifest de sync aplicavel
- regras de `ack` e retention

## Fallback e Recuperacao

- retry, dead-letter e recovery seguem o contrato da fundacao
- reconciliation precisa drenar o que ficou pendente no remoto

## Enforcement e validacoes

- `task ai:validate`
- testes e validadores da fundacao

## Artefatos relacionados

- [`../../docs/AI-FALLBACK-LEDGER.md`](../../docs/AI-FALLBACK-LEDGER.md)
- [`../../docs/AI-FALLBACK-OPERATIONS.md`](../../docs/AI-FALLBACK-OPERATIONS.md)

## Temas vizinhos

- [`documentation-and-confluence-rules.md`](documentation-and-confluence-rules.md)
- [`auth-secrets-and-critical-integrations-rules.md`](auth-secrets-and-critical-integrations-rules.md)
