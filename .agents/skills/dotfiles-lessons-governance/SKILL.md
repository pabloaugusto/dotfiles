---
name: dotfiles-lessons-governance
description: Governar o fluxo formal de LICOES-APRENDIDAS, revisoes por worklog, retroativos, curadoria de licoes e fechamento sem pendencias silenciosas. Use quando a tarefa tocar `LICOES-APRENDIDAS.md`, `scripts/ai-lessons.py`, `scripts/ai-worklog.py`, governanca de fechamento ou backfill de trabalho executado.
---

# dotfiles-lessons-governance

## Objetivo

Transformar `LICOES-APRENDIDAS.md` em contrato revisado a cada rodada.

## Fluxo

1. Ler `LICOES-APRENDIDAS.md`, `docs/AI-WIP-TRACKER.md` e `docs/ROADMAP.md`.
2. Determinar se a rodada gerou uma nova licao ou somente uma revisao `sem_nova_licao`.
3. Registrar novas licoes antes do `done`, nunca depois.
4. Garantir que cada worklog concluido tenha revisao associada.
5. Usar `task ai:lessons:check` como gate final de consistencia.

## Regras

- Toda revisao de rodada deve ser explicita.
- Nova licao so entra quando houver ganho real, validado e reutilizavel.
- Worklog, roadmap e lessons nao podem divergir.

## Entregas esperadas

- licoes novas quando houver ganho real
- revisao explicita de cada rodada
- worklog, roadmap e lessons sem drift

## Validacao

- `task ai:lessons:check`
- `task ai:worklog:close:gate`
- `task ai:validate`

## Referencias

- `references/checklist.md`
