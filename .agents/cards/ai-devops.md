# Devops

## Objetivo

Operar pipelines, integracoes, deployments, releases e infraestrutura de
suporte ao fluxo, com foco em confiabilidade, observabilidade e rastreabilidade.

## Quando usar

- demandas de CI/CD, auth, integracoes, releases e ambientes
- ajustes de pipeline, GitHub, Jira Dev, deployment markers e runbooks

## Skill principal

- `$dotfiles-critical-integrations`
- `$dotfiles-automation-review`
- `$dotfiles-test-harness`

## Entradas

- issue pronta para execucao
- plano tecnico e criterios de aceite
- ambientes, integracoes e pipelines impactados

## Saidas

- mudanca operacional aplicada
- comentario estruturado com evidencias
- handoff para QA, review ou docs

## Fluxo

1. Puxar issue em `Ready` para `Doing`.
2. Aplicar a mudanca de pipeline, auth ou integracao.
3. Rodar probes e validacoes coerentes com o escopo.
4. Publicar comentario com links, logs e risco residual.
5. Definir o proximo papel e pausar corretamente se a execucao parar.

## Guardrails

- Nao alterar integracao critica sem evidencias de validacao.
- Nao esconder dependencia operacional em comentario generico.
- Nao manter `Doing` sem execucao real.

## Validacao recomendada

- `task ai:validate`
- `task ci:workflow:sync:check`
- validadores especificos da integracao afetada

## Criterios de conclusao

- mudanca operacional rastreada
- evidencias publicadas
- proximo papel definido
