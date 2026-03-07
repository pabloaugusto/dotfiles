# AI Delegation Flow

## Pipeline canonico

1. Ler `AGENTS.md`, `LICOES-APRENDIDAS.md` e contexto minimo do repo.
2. Rodar preflight de pendencias em `docs/AI-WIP-TRACKER.md`.
3. Se houver importacao cross-repo, concluir auditoria estrutural e registrar o delta em `docs/AI-SOURCE-AUDIT.md`.
4. Acionar `repo-governance-authority`.
5. Acionar `execution-worklog-governance-owner`.
6. Acionar `architecture-modernization-authority` em paralelo, sempre lendo e monitorando `docs/AI-WIP-TRACKER.md`, `docs/ROADMAP.md`, `docs/ROADMAP-DECISIONS.md` e demais registradores vivos de backlog/pendencias.
7. Se a tarefa pedir triagem, decomposicao ou plano de delegacao, acionar `orchestrator` com `$task-routing-and-decomposition`.
8. Se o escopo tocar bootstrap, auth, secrets, CI, sync, CLI ou ambiente, acionar `critical-integrations-guardian`.
9. Se o escopo tocar `LICOES-APRENDIDAS`, fechamento de rodada ou retroativo, acionar `lessons-governance-curator`.
10. Implementar e validar.
11. Revisar licoes, fechar worklog e validar gates finais.

## Roteamento por escopo

- `bootstrap/**`, `df/**` -> `bootstrap-operator`
- `AGENTS.md`, `.agents/**`, `.codex/README.md`, `docs/**` -> `repo-governance-authority`
- `docs/AI-WIP-TRACKER.md`, `docs/ROADMAP*.md`, `scripts/ai-worklog.py` -> `execution-worklog-governance-owner`
- triagem, intake, decomposicao, delegacao -> `orchestrator`
- qualquer analise substantiva -> `architecture-modernization-authority`
- auth, secrets, `gh`, `op`, `sops`, `age`, `ssh-agent`, CI, sync, signing -> `critical-integrations-guardian`
- `LICOES-APRENDIDAS.md`, `scripts/ai-lessons.py`, retroativos -> `lessons-governance-curator`

## Gatilhos obrigatorios

- `architecture-modernization-authority` e sempre obrigatorio como gate paralelo.
- `architecture-modernization-authority` deve observar continuamente WIP, backlog, roadmap, decisions e outros artefatos vivos para nao sugerir trabalho fora de contexto.
- `critical-integrations-guardian` e obrigatorio em mudancas de plataforma e integracoes criticas.
- `orchestrator` governa `ai:chat:intake`, `ai:route` e `ai:delegate` quando a demanda exigir triagem ou decomposicao.
- nenhum worklog pode fechar sem revisao de `lessons-governance-curator`.

## Artefatos declarativos

- `.agents/config.toml`
- `.agents/registry/*.toml`
- `.agents/orchestration/*`
- `.agents/rules/*`
- `.agents/evals/*`
- `docs/AI-AGENTS-CATALOG.md`
- `docs/AI-SKILLS-CATALOG.md`
- `docs/AI-GOVERNANCE-AND-REGRESSION.md`
