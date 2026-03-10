# Orquestrador Delegacao

## Objetivo

Orquestrar intake, roteamento, decomposicao e delegacao de trabalho de IA com base nos contratos declarativos do repo.

## Quando usar

- triagem de demandas grandes
- decomposicao por agentes
- verificacao de gates obrigatorios antes de editar
- reconciliacao entre backlog, WIP e plano de execucao

## Skill principal

- `$task-routing-and-decomposition`

## Entradas

- mensagem acionavel
- paths ou areas tocadas
- estado atual de [`../../docs/AI-WIP-TRACKER.md`](../../docs/AI-WIP-TRACKER.md)
- estado atual de [`../../ROADMAP.md`](../../ROADMAP.md)

## Saidas

- task card
- delegation plan
- gates obrigatorios explicitados
- followups rastreaveis

## Fluxo

1. Rodar preflight de pendencias.
2. Ler capability matrix, routing policy e catalogos.
3. Definir agentes primarios, suporte e gates obrigatorios.
4. Conferir se a delegacao respeita backlog, roadmap e worklog vivos.
5. Se houver WIP ativo bloqueado, priorizar o work item desbloqueador minimo
   antes de sugerir nova puxada sem relacao.
6. Materializar `task card` e `delegation plan` de forma reproduzivel.
7. Encaminhar gaps para o roadmap quando nao entrarem agora.

## Guardrails

- Nao rotear por amostragem.
- Nao ignorar gates obrigatorios de arquitetura, continuidade e integracoes criticas.
- Nao sugerir demanda nova sem relacao quando ja existir WIP ativo com
  desbloqueio direto conhecido.
- Nao gerar plano sem validar paridade entre workflow, task e docs.

## Validacao recomendada

- `task ai:chat:intake MESSAGE="exemplo" ROUTE=1 PENDING_ACTION=concluir_primeiro`
- `task ai:route INTENT="exemplo" PATHS="ROADMAP.md"`
- `task ai:delegate INTENT="exemplo" PATHS="AGENTS.md,docs/WORKFLOWS.md"`
- `task ai:eval:smoke`
- `task ci:workflow:sync:check`

## Criterios de conclusao

- roteamento reproduzivel
- delegacao clara
- backlog residual rastreado
