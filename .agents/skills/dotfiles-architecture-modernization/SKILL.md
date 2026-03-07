---
name: dotfiles-architecture-modernization
description: Revisar arquitetura, refactor, performance, simplificacao, resiliencia, testabilidade e modernizacao deste repo de dotfiles. Use em qualquer analise substantiva ou mudanca relevante em codigo, docs, tasks, workflows, bootstrap ou estrutura para identificar melhorias, drifts, gargalos e proximos passos tecnicos.
---

# dotfiles-architecture-modernization

## Objetivo

Atuar como gate paralelo obrigatorio de arquitetura e modernizacao.

## Fluxo

1. Ler [`AGENTS.md`](AGENTS.md), [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md), [`docs/AI-DELEGATION-FLOW.md`](docs/AI-DELEGATION-FLOW.md), [`../../../docs/AI-WIP-TRACKER.md`](../../../docs/AI-WIP-TRACKER.md), [`../../../ROADMAP.md`](../../../ROADMAP.md) e [`../../../docs/ROADMAP-DECISIONS.md`](../../../docs/ROADMAP-DECISIONS.md).
2. Se a mudanca vier de importacao cross-repo, confirmar auditoria em [`docs/AI-SOURCE-AUDIT.md`](docs/AI-SOURCE-AUDIT.md).
3. Mapear contratos, acoplamentos, backlog existente e custo estrutural dos arquivos tocados.
4. Avaliar se existe alternativa mais simples, modular, testavel, performatica ou resiliente.
5. Registrar gaps e proximos passos no roadmap, backlog ou registrador vivo correspondente quando a melhoria nao entrar agora.
6. Exigir evidencias tecnicas, nao apenas preferencia estetica.

## Regras

- Sempre considerar backlog, WIP e roadmap como entrada obrigatoria do raciocinio.
- Nao recomendar stack, ferramenta ou refactor sem ganho objetivo de simplicidade, performance, custo ou resiliencia.
- Converter melhoria nao executada em item rastreavel de backlog, nunca em observacao perdida no chat.

## Entregas esperadas

- riscos estruturais
- simplificacoes possiveis
- melhorias de performance e resiliencia
- backlog tecnico rastreavel

## Validacao

- `task ai:validate`
- `task ai:eval:smoke`
- `task ci:workflow:sync:check`
- `task test:unit:python:windows`
- `task ci:lint:windows`

## Referencias

- [`references/checklist.md`](references/checklist.md)
