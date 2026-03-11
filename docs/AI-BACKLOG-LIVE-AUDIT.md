# AI Backlog Live Audit

## Objetivo

Registrar a auditoria factual de [DOT-133: Cruzar backlog vivo e pendencias documentais com o Jira](https://pabloaugusto.atlassian.net/browse/DOT-133), cruzando o backlog vivo versionado com o estado real do `Jira`.

## Escopo auditado

- [`ROADMAP.md`](../ROADMAP.md)
- [`docs/ROADMAP-DECISIONS.md`](ROADMAP-DECISIONS.md)
- [`docs/AI-CHAT-CONTRACTS-REGISTER.md`](AI-CHAT-CONTRACTS-REGISTER.md)
- `Jira` do projeto `DOT`

## Resumo factual

- `44` sugestoes em status `aceita` foram lidas em [`docs/ROADMAP-DECISIONS.md`](ROADMAP-DECISIONS.md).
- `41` dessas sugestoes continuam ativas no backlog vivo em [`ROADMAP.md`](../ROADMAP.md), nos horizontes `now`, `next` ou `later`.
- `3` sugestoes ativas ja tinham **work item** oficial comprovado no `Jira`: [DOT-14](https://pabloaugusto.atlassian.net/browse/DOT-14), [DOT-23](https://pabloaugusto.atlassian.net/browse/DOT-23) e [DOT-32](https://pabloaugusto.atlassian.net/browse/DOT-32).
- `38` sugestoes ativas ainda nao tinham owner oficial comprovado e receberam **work item** proprio na auditoria [DOT-133](https://pabloaugusto.atlassian.net/browse/DOT-133): [DOT-137](https://pabloaugusto.atlassian.net/browse/DOT-137) ate [DOT-174](https://pabloaugusto.atlassian.net/browse/DOT-174).
- `3` sugestoes aceitas nao aparecem mais em `now/next/later`; foram classificadas como historico aceito nao ativo e nao geraram nova issue nesta rodada.

## Ativos com issue oficial preexistente

| Suggestion ID | Horizonte | Work item oficial | Resumo |
| --- | --- | --- | --- |
| `SG-20260307-REVIEWER-STACK-PARITY` | `next` | [DOT-14](https://pabloaugusto.atlassian.net/browse/DOT-14) | Tornar obrigatorio que todo revisor especializado use toda a stack de qualidade |
| `SG-20260307-ATLASSIAN-PRODUCT-DISCOVERY` | `next` | [DOT-23](https://pabloaugusto.atlassian.net/browse/DOT-23) | Integrar Atlassian Product Discovery como camada opcional de intake e discovery upstream do Jira |
| `SG-20260307-095241` | `next` | [DOT-32](https://pabloaugusto.atlassian.net/browse/DOT-32) | Criar tasks/CLIs ai:status, ai:diff, ai:sync e ai:backup |

## Ativos regularizados na auditoria DOT-133

### Backlog funcional

| Suggestion ID | Horizonte | Work item criado | Resumo |
| --- | --- | --- | --- |
| `SG-20260308-024832` | `next` | [DOT-137](https://pabloaugusto.atlassian.net/browse/DOT-137) | Cache de secrets na borda da sessao para reduzir leituras repetidas do runtime. |
| `SG-20260308-020528` | `later` | [DOT-138](https://pabloaugusto.atlassian.net/browse/DOT-138) | Telemetria de esforco por agente e por etapa da demanda. |
| `SG-20260308-014206` | `later` | [DOT-139](https://pabloaugusto.atlassian.net/browse/DOT-139) | Evolucao para monolito modular em Python com fronteiras de dominio. |
| `SG-20260308-013625` | `next` | [DOT-140](https://pabloaugusto.atlassian.net/browse/DOT-140) | Governanca perene de comentarios explicativos em contratos e configuracoes. |
| `SG-20260307-PLAN-HISTORY` | `next` | [DOT-141](https://pabloaugusto.atlassian.net/browse/DOT-141) | Historico versionado de planos sugeridos, aprovados e implementados. |
| `SG-20260307-SSH-CONFIG-ACL` | `now` | [DOT-142](https://pabloaugusto.atlassian.net/browse/DOT-142) | Correcao de ACL e ownership da configuracao SSH do usuario. |
| `SG-20260307-EPHEMERAL-CLEANUP` | `next` | [DOT-143](https://pabloaugusto.atlassian.net/browse/DOT-143) | Governanca e automacao para limpeza de artefatos efemeros do repo. |
| `SG-20260307-DOCS-RESTRUCTURE` | `next` | [DOT-144](https://pabloaugusto.atlassian.net/browse/DOT-144) | Reestruturacao semantica da arvore documental do repositorio. |
| `SG-20260307-LESSONS-DOCS` | `next` | [DOT-145](https://pabloaugusto.atlassian.net/browse/DOT-145) | Migracao de LICOES-APRENDIDAS para a camada documental canonica. |
| `SG-20260307-REVIEWER-COVERAGE` | `next` | [DOT-146](https://pabloaugusto.atlassian.net/browse/DOT-146) | Expansao da malha de revisores especialistas por familia de arquivo. |
| `SG-20260307-SECRETS-ROTATION` | `now` | [DOT-147](https://pabloaugusto.atlassian.net/browse/DOT-147) | Modulo de rotacionamento automatizado de secrets e chaves. |
| `SG-20260307-DEVCONTAINER` | `next` | [DOT-148](https://pabloaugusto.atlassian.net/browse/DOT-148) | Formalizacao do ambiente de desenvolvimento com devcontainer e Docker. |
| `SG-20260307-LOCALE-DATES` | `next` | [DOT-149](https://pabloaugusto.atlassian.net/browse/DOT-149) | Padronizacao de datas, horas, locale e idioma em docs, scripts e logs. |
| `SG-WIP-20260307-VSCODE-WORKSPACE` | `next` | [DOT-150](https://pabloaugusto.atlassian.net/browse/DOT-150) | Auditoria e endurecimento da camada [`.vscode/`](../.vscode/). |
| `SG-20260307-ASSETS-IMG` | `next` | [DOT-151](https://pabloaugusto.atlassian.net/browse/DOT-151) | Definicao da fronteira entre assets de runtime, design e arquivo. |
| `SG-20260307-SCRIPTS-SPLIT` | `next` | [DOT-152](https://pabloaugusto.atlassian.net/browse/DOT-152) | Reavaliacao da fronteira entre entrypoints e biblioteca em [`scripts/`](../scripts/). |
| `SG-20260307-OPSIGN` | `now` | [DOT-153](https://pabloaugusto.atlassian.net/browse/DOT-153) | Desbloqueio operacional da assinatura Git com signer tecnico. |
| `SG-20260307-095316` | `later` | [DOT-154](https://pabloaugusto.atlassian.net/browse/DOT-154) | Camada de conhecimento global portavel para IA fora do contexto do repo. |
| `SG-20260307-095305` | `next` | [DOT-155](https://pabloaugusto.atlassian.net/browse/DOT-155) | Hooks e policies de IA com presets de permissao e bloqueios. |
| `SG-20260307-095254` | `next` | [DOT-156](https://pabloaugusto.atlassian.net/browse/DOT-156) | Adaptadores de assistentes e arquivos MCP a partir de fonte canonica unica. |
| `SG-20260307-090831` | `next` | [DOT-157](https://pabloaugusto.atlassian.net/browse/DOT-157) | Consolidacao ou arquivamento do legado historico nao canonico. |
| `SG-20260307-041349-01` | `now` | [DOT-158](https://pabloaugusto.atlassian.net/browse/DOT-158) | Expansao de datasets e cenarios de eval para bootstrap e risco operacional. |

### Backlog ortografico consultivo

| Suggestion ID | Horizonte | Bug criado | Resumo |
| --- | --- | --- | --- |
| `SG-ORTHO-WIP-DOT-131` | `next` | [DOT-159](https://pabloaugusto.atlassian.net/browse/DOT-159) | Pendencias ortograficas remanescentes do fechamento de DOT-131. |
| `SG-ORTHO-WIP-DOT-130` | `next` | [DOT-160](https://pabloaugusto.atlassian.net/browse/DOT-160) | Pendencias ortograficas remanescentes do fechamento de DOT-130. |
| `SG-ORTHO-DOT-122` | `next` | [DOT-161](https://pabloaugusto.atlassian.net/browse/DOT-161) | Pendencias ortograficas remanescentes ligadas a DOT-122. |
| `SG-ORTHO-DOT-118` | `next` | [DOT-162](https://pabloaugusto.atlassian.net/browse/DOT-162) | Pendencias ortograficas remanescentes ligadas a DOT-118. |
| `SG-ORTHO-DOT-119` | `next` | [DOT-163](https://pabloaugusto.atlassian.net/browse/DOT-163) | Pendencias ortograficas remanescentes ligadas a DOT-119. |
| `SG-ORTHO-DOT-120` | `next` | [DOT-164](https://pabloaugusto.atlassian.net/browse/DOT-164) | Pendencias ortograficas remanescentes ligadas a DOT-120. |
| `SG-ORTHO-DOT-121` | `next` | [DOT-165](https://pabloaugusto.atlassian.net/browse/DOT-165) | Pendencias ortograficas remanescentes ligadas a DOT-121. |
| `SG-ORTHO-DOT-124` | `next` | [DOT-166](https://pabloaugusto.atlassian.net/browse/DOT-166) | Pendencias ortograficas remanescentes ligadas a DOT-124. |
| `SG-ORTHO-DOT-115` | `next` | [DOT-167](https://pabloaugusto.atlassian.net/browse/DOT-167) | Pendencias ortograficas remanescentes ligadas a DOT-115. |
| `SG-ORTHO-DOT-128` | `next` | [DOT-168](https://pabloaugusto.atlassian.net/browse/DOT-168) | Pendencias ortograficas remanescentes ligadas a DOT-128. |
| `SG-ORTHO-DOT-127` | `next` | [DOT-169](https://pabloaugusto.atlassian.net/browse/DOT-169) | Pendencias ortograficas remanescentes ligadas a DOT-127. |
| `SG-ORTHO-DOT-117` | `next` | [DOT-170](https://pabloaugusto.atlassian.net/browse/DOT-170) | Pendencias ortograficas remanescentes ligadas a DOT-117. |
| `SG-ORTHO-DOT-114` | `next` | [DOT-171](https://pabloaugusto.atlassian.net/browse/DOT-171) | Pendencias ortograficas remanescentes ligadas a DOT-114. |
| `SG-ORTHO-WIP-20260307-ATLASSIAN-ADAPTERS` | `next` | [DOT-172](https://pabloaugusto.atlassian.net/browse/DOT-172) | Pendencias ortograficas remanescentes do worklog historico Atlassian adapters. |
| `SG-ORTHO-WIP-20260307-ATLASSIAN-IA-CONTEXT` | `next` | [DOT-173](https://pabloaugusto.atlassian.net/browse/DOT-173) | Pendencias ortograficas remanescentes do worklog historico Atlassian IA context. |
| `SG-ORTHO-WIP-20260307-SECRETS-ROTATION` | `now` | [DOT-174](https://pabloaugusto.atlassian.net/browse/DOT-174) | Pendencias ortograficas remanescentes do worklog historico de rotacao de secrets. |

## Aceitos historicos nao ativos

| Suggestion ID | Situacao na auditoria | Acao nesta rodada |
| --- | --- | --- |
| `SG-20260307-REVIEWER-AGENTS` | Aceita em [`docs/ROADMAP-DECISIONS.md`](ROADMAP-DECISIONS.md), mas ausente de `now/next/later` em [`ROADMAP.md`](../ROADMAP.md). | Nao criou nova issue; tratar na auditoria integral de **Done** e backlog historico. |
| `SG-20260307-041349` | Aceita em [`docs/ROADMAP-DECISIONS.md`](ROADMAP-DECISIONS.md), mas ausente de `now/next/later` em [`ROADMAP.md`](../ROADMAP.md). | Nao criou nova issue; tratar na auditoria integral de **Done** e backlog historico. |
| `SG-20260307-041348` | Aceita em [`docs/ROADMAP-DECISIONS.md`](ROADMAP-DECISIONS.md), mas ausente de `now/next/later` em [`ROADMAP.md`](../ROADMAP.md). | Nao criou nova issue; tratar na auditoria integral de **Done** e backlog historico. |

## Contratos de chat cruzados na mesma rodada

| Contrato | Resultado factual |
| --- | --- |
| `CHAT-002` | A auditoria confirmou que o contrato ja estava forte em contratos, docs e governanca de review, mas ainda faltava espelho claro no card e no registry do **Tech Lead**. Essa lacuna foi corrigida nesta branch para permitir promocao definitiva do contrato. |
| `CHAT-003` | A auditoria confirmou a camada perene de identidade humana em cards, registry, docs e fallback do `Jira`, com `display_name` como fonte oficial e espelho obrigatorio nos cards. |
| `CHAT-005` | O contrato continuava sem owner oficial no `Jira`. A auditoria criou [DOT-136](https://pabloaugusto.atlassian.net/browse/DOT-136) para assumir a promocao definitiva do dicionario vivo de terminologia agil. |
