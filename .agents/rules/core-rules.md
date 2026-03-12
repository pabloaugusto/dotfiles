# Core Rules

## Objetivo

Definir contratos transversais que valem para toda rodada, independente do
tema tecnico.

## Escopo

- precedencia
- fronteira entre regra humana, config declarativa e enforcement
- enablement declarativo de agentes

## Fonte canonica e precedencia

- [`AGENTS.md`](../../AGENTS.md)
- [`LICOES-APRENDIDAS.md`](../../LICOES-APRENDIDAS.md)
- [`config/ai/contracts.yaml`](../../config/ai/contracts.yaml)
- [`config/ai/agents.yaml`](../../config/ai/agents.yaml)
- [`config/ai/agent-enablement.yaml`](../../config/ai/agent-enablement.yaml)

## Regras obrigatorias

- [`.agents/rules/`](./) e a fonte canonica humana por tema
- [`AGENTS.md`](../../AGENTS.md) fica como contrato global curto e transversal
- enablement ou disablement de agentes nao depende apenas de memoria de chat
- toda camada derivada deve apontar para a regra tematica correta

## Startup: o que precisa ser carregado

- [`README.md`](README.md)
- [`CATALOG.md`](CATALOG.md)
- tema aplicavel ao trabalho atual
- [`config/ai/agent-enablement.yaml`](../../config/ai/agent-enablement.yaml)

## Delegacao: o que o subagente precisa receber

- issue dona, branch, worklog e proximo passo
- regras tematicas aplicaveis
- estado declarativo de enablement dos agentes

## Fallback e Recuperacao

- se faltar regra tematica, bloquear o trabalho como drift de governanca
- se houver conflito entre docs e config, prevalece a regra humana + contrato
  declarativo correspondente

## Enforcement e validacoes

- [`scripts/validate-ai-assets.py`](../../scripts/validate-ai-assets.py)
- [`task ai:validate`](../../docs/TASKS.md#aivalidate)
- [`task docs:check`](../../docs/TASKS.md#docscheck)

## Artefatos relacionados

- [`README.md`](README.md)
- [`CATALOG.md`](CATALOG.md)
- [`../../docs/ai-operating-model.md`](../../docs/ai-operating-model.md)

## Temas vizinhos

- [`startup-and-resume-rules.md`](startup-and-resume-rules.md)
- [`delegation-rules.md`](delegation-rules.md)
- [`review-and-quality-rules.md`](review-and-quality-rules.md)

