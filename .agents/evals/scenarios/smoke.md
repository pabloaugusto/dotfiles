# Smoke

## Objetivo

Validar se a camada declarativa de IA minima do repo esta completa e coerente.

## Criterios

- catalogos existem
- `.agents/config.toml` referencia arquivos reais
- agents, skills, orchestration, rules e evals estao em paridade com docs
- `task ai:validate` passa
- `task ai:eval:smoke` prova o roteamento minimo esperado
- `task ci:workflow:sync:check` prova paridade entre workflows, Taskfile e catalogos
