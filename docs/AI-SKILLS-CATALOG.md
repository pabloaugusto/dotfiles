# AI Skills Catalog

Catalogo das skills versionadas do repo e seu papel operacional.

| Skill | Objetivo | Quando usar |
| --- | --- | --- |
| `$dotfiles-bootstrap` | Bootstrap, relink, config de usuario e paridade Windows/WSL | `bootstrap/`, links, paths canonicos |
| `$dotfiles-test-harness` | Tests, CI, harnesses e ambientes efemeros | `tests/`, `.github/workflows/`, `docker/` |
| `$dotfiles-repo-governance` | Contratos do repo, naming, docs, skills e organizacao | `AGENTS.md`, `.agents/`, `.codex/README.md`, governanca |
| `$wip-continuity-governance` | Continuidade, Doing/Done, roadmap e fechamento | `docs/AI-WIP-TRACKER.md`, `docs/ROADMAP*.md` |
| `$dotfiles-architecture-modernization` | Gate paralelo de arquitetura, simplificacao, performance e backlog tecnico | qualquer mudanca substantiva |
| `$dotfiles-critical-integrations` | Protecao de auth, secrets, CLI critica, bootstrap, sync e environment | bootstrap, auth, `gh`, `op`, `sops`, `age`, `ssh-agent`, CI |
| `$dotfiles-lessons-governance` | Curadoria de licoes, revisoes por rodada e retroativos | `LICOES-APRENDIDAS.md`, `scripts/ai-lessons.py`, fechamento |
| `$task-routing-and-decomposition` | Intake, roteamento declarativo, decomposicao e delegacao | triagem, backlog, planos de execucao e gates obrigatorios |
