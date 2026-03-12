# AI Skills Catalog

Catalogo das skills versionadas do repo e seu papel operacional.

| Skill | Objetivo | Quando usar |
| --- | --- | --- |
| `$dotfiles-bootstrap` | Bootstrap, relink, config de usuario e paridade Windows/WSL | [`../app/bootstrap/`](../app/bootstrap/), links, paths canonicos |
| `$dotfiles-test-harness` | Tests, CI, harnesses e ambientes efemeros | [`../tests/`](../tests/), [`../.github/workflows/`](../.github/workflows/), [`../docker/`](../docker/) |
| `$dotfiles-repo-governance` | Contratos do repo, naming, docs, skills e organizacao | [`../AGENTS.md`](../AGENTS.md), [`../.agents/`](../.agents/), [`../.codex/README.md`](../.codex/README.md), governanca |
| `$wip-continuity-governance` | Continuidade, Doing/Done, roadmap e fechamento | [`AI-WIP-TRACKER.md`](AI-WIP-TRACKER.md), [`../ROADMAP.md`](../ROADMAP.md), [`ROADMAP-DECISIONS.md`](ROADMAP-DECISIONS.md) |
| `$dotfiles-architecture-modernization` | Gate paralelo de arquitetura, simplificacao, performance e backlog tecnico | qualquer mudanca substantiva |
| `$dotfiles-critical-integrations` | Protecao de auth, secrets, CLI critica, bootstrap, sync e environment | bootstrap, auth, `gh`, `op`, `sops`, `age`, `ssh-agent`, CI |
| `$dotfiles-secrets-rotation` | Rotacao segura de tokens, chaves SSH, refs de segredo e artefatos `sops+age` | rotacao, revogacao, expiracao e continuidade de acesso |
| `$dotfiles-orthography-review` | Review consultivo de ortografia tecnica e curadoria do `cspell`, com backlog automatico quando a falha textual permanecer aberta | [`../.cspell.json`](../.cspell.json), [`../.cspell/project-words.txt`](../.cspell/project-words.txt), [`AI-ORTHOGRAPHY-LEDGER.md`](AI-ORTHOGRAPHY-LEDGER.md), docs, comentarios e configs textuais |
| `$dotfiles-python-review` | Review tecnico para codigo Python | [`../scripts/`](../scripts/), [`../tests/python/`](../tests/python/), [`../pyproject.toml`](../pyproject.toml) |
| `$dotfiles-powershell-review` | Review tecnico para codigo PowerShell | [`../app/bootstrap/`](../app/bootstrap/), [`../app/df/powershell/`](../app/df/powershell/), [`../tests/powershell/`](../tests/powershell/) |
| `$dotfiles-automation-review` | Review tecnico para shell, workflows, Taskfile e Docker | [`../.github/workflows/`](../.github/workflows/), [`../Taskfile.yml`](../Taskfile.yml), [`../docker/`](../docker/) |
| `$dotfiles-lessons-governance` | Curadoria de licoes, revisoes por rodada e retroativos | [`../LICOES-APRENDIDAS.md`](../LICOES-APRENDIDAS.md), [`../scripts/ai-lessons.py`](../scripts/ai-lessons.py), fechamento |
| `$task-routing-and-decomposition` | Intake, roteamento declarativo, decomposicao e delegacao | triagem, backlog, planos de execucao e gates obrigatorios |
