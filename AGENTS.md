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
4. `docs/bootstrap-flow.md` quando a tarefa tocar bootstrap
5. `Taskfile.yml`

## Skills locais

- `ai/skills/dotfiles-bootstrap`
- `ai/skills/dotfiles-test-harness`
- `ai/skills/dotfiles-repo-governance`

Leia a skill mais proxima do escopo antes de editar arquivos relevantes.

## Guardrails

- Preferir `task` e scripts existentes antes de criar fluxos paralelos.
- Manter tasks e scripts worktree-friendly usando `{{.TASKFILE_DIR}}` quando aplicavel.
- Preservar paridade entre Windows e WSL sempre que a mudanca tocar bootstrap, links, auth ou Git.
- Tratar caminhos canonicos absolutos como fonte de verdade.
- Validar estado final e idempotencia, nao apenas `exit code`.
- Nao versionar runtime local de IA: `.codex/`, `.gemini/`, `.agents/`, sessoes, auth, caches, browser profiles ou historico.
- Se um artefato de IA for declarativo, portavel e sem segredo, mover a fonte canonica para o repo e materializar no `HOME` via bootstrap, link ou copia controlada.

## Fluxo operacional minimo

1. Ler o contexto minimo.
2. Escolher a skill local adequada.
3. Fazer a menor mudanca coerente com a arquitetura do repo.
4. Validar localmente com tasks, lints e testes cabiveis.
5. Manter commit e PR no padrao `emoji + conventional commits`.
