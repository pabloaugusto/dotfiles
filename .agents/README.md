# .agents

Fonte de verdade da camada declarativa e operacional de IA deste repo.

## Estrutura

- [`cards/`](cards/): cartoes operacionais dos agentes do projeto
- [`skills/`](skills/): skills versionadas do repo
- [`prompts/`](prompts/): prompt packs e material historico relacionado a IA
- [`registry/`](registry/): agentes declarativos tipados
- [`orchestration/`](orchestration/): matriz de capacidade, policy e schemas
- [`rules/`](rules/): regras declarativas de operacao e CI
- [`evals/`](evals/): cenarios e datasets minimos de regressao
- [`config.toml`](config.toml): contrato central da camada declarativa

## Regra

- Toda regra declarativa portavel deve nascer em [`.agents/`](.agents/).
- Prompt packs versionados tambem devem ficar sob [`.agents/`](.agents/), nunca soltos na raiz do repo.
- [`.codex/`](.codex/) existe apenas como ponte de compatibilidade e deve conter so [`README.md`](README.md).
