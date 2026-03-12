# .agents

Fonte de verdade da camada declarativa e operacional de IA deste repo.

## Estrutura

- [`cards/`](cards/): cartoes operacionais dos agentes do projeto
- [`skills/`](skills/): skills versionadas do repo
- [`prompts/`](prompts/): prompt packs versionados, catalogados e material historico relacionado a IA
- [`registry/`](registry/): agentes declarativos tipados
- [`orchestration/`](orchestration/): matriz de capacidade, policy e schemas
- [`rules/`](rules/): fonte canonica humana das regras normativas por tema
- [`evals/`](evals/): cenarios e datasets minimos de regressao
- [`config.toml`](config.toml): contrato central da camada declarativa

## Dominios criticos permanentes

- bootstrap e links canonicos
- governanca e continuidade de IA
- integracoes criticas de auth e CLI
- rotacao segura de secrets, tokens, chaves SSH e `sops+age`
- revisao especializada obrigatoria por familia de arquivo
- revisao consultiva perene de ortografia tecnica e curadoria `cspell`

## Regra

- Toda regra declarativa portavel deve nascer em [`.agents/`](.agents/).
- A regra normativa humana por tema deve viver primeiro em
  [`.agents/rules/`](rules/); docs, startup e validadores consomem essa camada.
- Prompt packs versionados tambem devem ficar sob [`.agents/`](.agents/), nunca soltos na raiz do repo.
- A arvore de prompt packs deve seguir o catalogo canonico em
  [`.agents/prompts/README.md`](prompts/README.md) e
  [`.agents/prompts/CATALOG.md`](prompts/CATALOG.md), preservando `legacy/`
  para historico e `formal/` para pacotes executaveis vivos.
- [`.codex/`](.codex/) existe apenas como ponte de compatibilidade e deve conter so [`README.md`](README.md).

## Integracao com config

- [`../config/ai/agents.yaml`](../config/ai/agents.yaml) continua descrevendo os
  papeis declarativos do repo.
- [`../config/ai/agent-enablement.yaml`](../config/ai/agent-enablement.yaml)
  governa o enablement declarativo por agente, sem depender de memoria de chat.
