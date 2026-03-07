# .agents

Fonte de verdade da camada declarativa e operacional de IA deste repo.

## Estrutura

- `cards/`: cartoes operacionais dos agentes do projeto
- `skills/`: skills versionadas do repo
- `registry/`: agentes declarativos tipados
- `orchestration/`: matriz de capacidade, policy e schemas
- `rules/`: regras declarativas de operacao e CI
- `evals/`: cenarios e datasets minimos de regressao
- `config.toml`: contrato central da camada declarativa

## Regra

- Toda regra declarativa portavel deve nascer em `.agents/`.
- `.codex/` existe apenas como ponte de compatibilidade e deve conter so `README.md`.
