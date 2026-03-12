# Source Audit And Cross Repo Rules

## Objetivo

Definir a barra obrigatoria para importacao, adaptacao e consolidacao de regras
ou ativos de outro repo.

## Escopo

- auditoria estrutural
- gap analysis
- rastreabilidade da importacao

## Fonte canonica e precedencia

- [`../../docs/AI-SOURCE-AUDIT.md`](../../docs/AI-SOURCE-AUDIT.md)
- [`../../AGENTS.md`](../../AGENTS.md)
- [`../../LICOES-APRENDIDAS.md`](../../LICOES-APRENDIDAS.md)

## Regras obrigatorias

- nao operar por amostragem em importacao cross-repo
- auditar contratos, docs, tasks, scripts, hooks, validadores, testes e regras
- registrar a auditoria em [`../../docs/AI-SOURCE-AUDIT.md`](../../docs/AI-SOURCE-AUDIT.md) antes de importar
- agir com barra de senioridade e sem trabalho parcial

## Startup: o que precisa ser carregado

- manifest
- source audit existente
- temas que serao tocados pela importacao

## Delegacao: o que o subagente precisa receber

- repos fonte
- escopo auditado
- regras de rastreabilidade

## Fallback e Recuperacao

- sem auditoria versionada, bloquear importacao
- se a fonte ficar duvidosa, reabrir a auditoria antes de continuar

## Enforcement e validacoes

- `task ai:validate`
- atualizacao do source audit

## Artefatos relacionados

- [`../../docs/AI-GOVERNANCE-AND-REGRESSION.md`](../../docs/AI-GOVERNANCE-AND-REGRESSION.md)
- [`../../docs/AI-REVIEW-LEDGER.md`](../../docs/AI-REVIEW-LEDGER.md)

## Temas vizinhos

- [`core-rules.md`](core-rules.md)
- [`auth-secrets-and-critical-integrations-rules.md`](auth-secrets-and-critical-integrations-rules.md)
