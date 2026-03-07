# AGENTS.md

## Missao

Manter este repo de dotfiles confiavel, testavel e reproduzivel em Windows host e Ubuntu WSL.

## Idioma

- Escrever documentacao, comentarios e respostas em portugues.
- Preferir ASCII nos arquivos do repo, exceto quando um arquivo existente exigir Unicode.

## Leitura minima antes de editar

1. `CONTEXT.md`
2. `docs/test-strategy.md`
3. `docs/ai-operating-model.md`
4. `docs/AI-WIP-TRACKER.md`
5. `docs/bootstrap-flow.md` quando a tarefa tocar bootstrap
6. `Taskfile.yml`

## Skills locais

- `.codex/skills/dotfiles-bootstrap`
- `.codex/skills/dotfiles-test-harness`
- `.codex/skills/dotfiles-repo-governance`
- `.codex/skills/wip-continuity-governance`

Leia a skill mais proxima do escopo antes de editar arquivos relevantes.

## Guardrails

- Preferir `task` e scripts existentes antes de criar fluxos paralelos.
- Manter tasks e scripts worktree-friendly usando `{{.TASKFILE_DIR}}` quando aplicavel.
- Preservar paridade entre Windows e WSL sempre que a mudanca tocar bootstrap, links, auth ou Git.
- Tratar caminhos canonicos absolutos como fonte de verdade.
- Validar estado final e idempotencia, nao apenas `exit code`.
- Branches devem seguir `<type>/<slug>` e nao usar emoji.
- Commit e PR title devem seguir `emoji + conventional commit` com maximo recomendado de 72 caracteres.
- Cada branch deve carregar um unico contexto coerente; separar assuntos independentes em branches diferentes.
- `docs/AI-WIP-TRACKER.md` e a fonte de verdade do trabalho incremental de IA.
- Nao versionar runtime local de IA: `.gemini/`, sessoes, auth, caches, browser profiles, historico e arquivos locais gerados dentro de `.codex/` fora das pastas declarativas versionadas.
- Se um artefato de IA for declarativo, portavel e sem segredo, mover a fonte canonica para o repo e materializar no `HOME` via bootstrap, link ou copia controlada.

## Fluxo operacional minimo

1. Ler o contexto minimo.
2. Rodar `task ai:worklog:check` antes de execucao relevante.
3. Escolher a skill local adequada.
4. Fazer a menor mudanca coerente com a arquitetura do repo.
5. Validar localmente com tasks, lints e testes cabiveis.
6. Fechar o tracker com `task ai:worklog:close:gate`.
7. Manter commit e PR no padrao `emoji + conventional commits`.
