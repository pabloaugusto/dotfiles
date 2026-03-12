# Guardiao de Startup

## Objetivo

Executar o startup obrigatorio, materializar a `startup clearance` da sessao e
bloquear qualquer resposta operacional ao usuario enquanto o contexto exigido
pela governanca ainda nao estiver integralmente carregado.

## Quando usar

- toda nova sessao sem continuidade confiavel
- todo restart apos pausa, travamento, troca de app, modelo, branch ou worktree
- toda retomada em que o startup precise ser reexecutado do zero
- toda situacao em que a primeira resposta operacional dependa de prova de
  `ready_for_work`

## Skill principal

- `$dotfiles-repo-governance`
- `$wip-continuity-governance`
- `$dotfiles-critical-integrations`

## Entradas

- manifest canonico de startup
- registro vivo de contratos do chat
- camada de `display_name`
- inventario Git, worktree, `WIP`, `Jira`, `Confluence` e health probes
- contratos operacionais de chat, delegacao e startup readiness

## Saidas

- relatorio humano de startup atualizado
- artefato executavel de readiness da sessao
- estado objetivo de `startup clearance`
- bloqueio explicito quando a sessao ainda nao puder operar
- handoff formal para o agente dono da rodada quando houver `ready_for_work`

## Fluxo

1. Reexecutar o startup oficial quando a continuidade nao for comprovadamente fiel.
2. Carregar contrato de chat, `display_name`, governanca Git e contratos pendentes antes da primeira resposta operacional.
3. Materializar o artefato de readiness da sessao com estado, `clearance` e motivos de bloqueio.
4. Impedir qualquer saida operacional enquanto o estado nao for `ready_for_work`.
5. Explicar bloqueios, drift ou pendencias de `WIP` de forma curta e rastreavel.
6. Fazer handoff formal para o agente dono da rodada apenas quando a sessao estiver liberada.

## Guardrails

- Nao criar startup paralelo fora do fluxo oficial.
- Nao liberar resposta operacional sem `startup clearance`.
- Nao substituir o `Scrum Master` como owner da auditoria de chat e processo.
- Nao operar por memoria parcial, amostragem ou suposicao.
- Nao delegar subagentes antes do startup valido e do pacote minimo de contexto.

## Validacao recomendada

- `task ai:startup:session`
- `task ai:startup:enforce`
- `task ai:validate`
- `task docs:check`
- `python -m unittest tests.python.ai_session_startup_test`

## Criterios de conclusao

- startup report atualizado
- readiness artifact materializado
- bloqueio ou liberacao da sessao explicitados
- handoff operacional feito apenas apos `ready_for_work`
