# Arquitetura Alvo

## Principio central

[`.agents/rules/`](../../../../rules/) vira a fonte canonica **normativa por
tema**.

## Separacao obrigatoria

- [`AGENTS.md`](../../../../../AGENTS.md): contrato global curto, precedencia,
  leitura obrigatoria e ponte para os temas
- [`.agents/rules/`](../../../../rules/): regra humana canonica por tema
- [`docs/`](../../../../../docs/): guias, runbooks, explicacoes e material
  derivado
- [`Taskfile.yml`](../../../../../Taskfile.yml), [`.githooks/`](../../../../../.githooks/),
  scripts e testes: enforcement executavel

## Estrutura alvo minima

- arquivo inicial da pasta de rules
- `CATALOG.md`
- `core-rules.md`
- `chat-and-identity-rules.md`
- `startup-and-resume-rules.md`
- `git-rules.md`
- `intake-and-backlog-rules.md`
- `jira-execution-rules.md`
- `documentation-and-confluence-rules.md`
- `delegation-rules.md`
- `review-and-quality-rules.md`
- `worklog-and-lessons-rules.md`
- `scrum-and-ceremonies-rules.md`
- `prompt-pack-rules.md`
- `auth-secrets-and-critical-integrations-rules.md`
- `sync-foundation-rules.md`
- `source-audit-and-cross-repo-rules.md`

## Template obrigatorio por tema

Cada arquivo tematico deve conter:

1. `Objetivo`
2. `Escopo`
3. `Fonte canonica e precedencia`
4. `Regras obrigatorias`
5. `Startup: o que precisa ser carregado`
6. `Delegacao: o que o subagente precisa receber`
7. `Fallback e Recuperacao`
8. `Enforcement e validacoes`
9. `Artefatos relacionados`
10. `Temas vizinhos`

## Regra de fallback

`fallback` deve aparecer como secao obrigatoria dentro dos temas relevantes, e
nao como arquivo principal separado neste primeiro corte.
