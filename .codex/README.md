# .codex

Esta pasta nao e fonte de verdade neste repo.

## Fonte canonica

Use `.agents/` e suas subpastas:

- `.agents/cards/`
- `.agents/skills/`
- `.agents/registry/`
- `.agents/orchestration/`
- `.agents/rules/`
- `.agents/evals/`
- `.agents/config.toml`

## Regra de compatibilidade

- `.codex/` deve permanecer apenas com este `README.md`.
- Qualquer contrato, skill, schema, rule, eval ou metadata declarativa deve ser mantido em `.agents/`.
- Se algum assistente precisar de materializacao propria, ela deve ser gerada a partir de `.agents/`, nunca editada manualmente aqui.
