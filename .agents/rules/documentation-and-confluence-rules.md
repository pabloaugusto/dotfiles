# Documentation And Confluence Rules

## Objetivo

Definir source of truth, placement, lifecycle e publication documental.

## Escopo

- docs do repo
- Confluence
- linkagem e source of truth

## Fonte canonica e precedencia

- [`../../config/ai/contracts.yaml`](../../config/ai/contracts.yaml)
- [`../../docs/ai-operating-model.md`](../../docs/ai-operating-model.md)
- [`../../docs/AI-DELEGATION-FLOW.md`](../../docs/AI-DELEGATION-FLOW.md)

## Regras obrigatorias

- repo-first para contratos e documentacao tecnica versionada
- Confluence para publication e navegacao institucional quando elegivel
- `pascoalete` atua em modo consultivo quando estiver `enabled`
- `documentation-link` e responsabilidade do `ai-documentation-sync`

## Startup: o que precisa ser carregado

- source of truth do artefato
- papeis documentais habilitados
- regras de linkagem e sync

## Delegacao: o que o subagente precisa receber

- surface dona
- source of truth
- se `ai-linguistic-reviewer` esta `enabled` ou `disabled`

## Fallback e Recuperacao

- sem Confluence, manter repo como fonte versionada
- sync remoto so volta apos classificacao e reconciliacao

## Enforcement e validacoes

- `task docs:check`
- `task ai:review:check`

## Artefatos relacionados

- [`../../docs/AI-AGENTS-CATALOG.md`](../../docs/AI-AGENTS-CATALOG.md)
- [`../../docs/AI-REVIEW-LEDGER.md`](../../docs/AI-REVIEW-LEDGER.md)

## Temas vizinhos

- [`review-and-quality-rules.md`](review-and-quality-rules.md)
- [`sync-foundation-rules.md`](sync-foundation-rules.md)
