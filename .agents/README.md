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

## Dominios criticos permanentes

- bootstrap e links canonicos
- governanca e continuidade de IA
- integracoes criticas de auth e CLI
- rotacao segura de secrets, tokens, chaves SSH e `sops+age`
- revisao especializada obrigatoria por familia de arquivo
- revisao consultiva perene de ortografia tecnica e curadoria `cspell`

## Regra

- Toda regra declarativa portavel deve nascer em [`.agents/`](.agents/).
- Prompt packs versionados tambem devem ficar sob [`.agents/`](.agents/), nunca soltos na raiz do repo.
- [`.codex/`](.codex/) existe apenas como ponte de compatibilidade e deve conter so [`README.md`](README.md).
