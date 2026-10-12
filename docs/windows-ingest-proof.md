# Ingestão do `dotfiles-windows` — prova por conteúdo

**Data:** 11/10/2026 · **Branch:** `fix/bootstrap-windows-ingest` (base `f9ee700` = `fix/bootstrap-fase-a`)
**Origem:** NUC `/srv/repos/dotfiles-windows.git` (bare, só leitura) via `git bundle`.
**Método:** `git cherry` (patch-id) + `git cat-file`/`rev-parse` (blob). Nada foi apagado na origem.

## 1. Commit de código — `7a034380` (`fix/boot-autosign`)

Cherry-pick sobre a linha viva `f9ee700`, resolvendo conflitos a favor do comportamento mais novo.

- O único hunk do `windows` sem equivalente funcional é a **remoção do `node`** da lista de binários
  esperados — e o `dotfiles` **já a fez antes** (`f9ee700` não tem a linha `'node'`).
- Resultado do cherry-pick: **no-op material** (a árvore resultante é idêntica a `f9ee700`). Registrado
  como commit `65ad599` (empty, com `(cherry picked from 7a034380…)`) para preservar a linhagem.

Prova de conteúdo — símbolos introduzidos por `7a034380` já presentes em `f9ee700`:

| Símbolo | Arquivo(s) em `f9ee700` |
|---|---|
| `automation.signing_key_ref` | `bootstrap-config.ps1`, `bootstrap-ubuntu-wsl.sh`, `_functions.ps1` |
| `daneel_ed25519` | `bootstrap-config.ps1`, `bootstrap-ubuntu-wsl.sh`, `signing-automation.sh` |
| `Get-ForbiddenEnvLeaks` | `_functions.ps1`, `CheckEnv.Tests.ps1` |
| `New-OpStub` | `BootstrapConfig.Tests.ps1` |
| `Test-EnvTemplateHasOpRefs` | `bootstrap-windows.ps1`, `_functions.ps1`, `DotEnvLocalSops.Tests.ps1` |

## 2. Tag `v1.0.0` (`a5a5d68`, 24/02/2026)

Trazida como tag **`windows-v1.0.0`** apontando para `a5a5d685ec95f552ec7db673571073443bbcbada`.
Linha própria: **não** é ancestral de `main`/`fix/bootstrap-fase-a`.

> ⚠️ **Bloqueio de push:** a linhagem de `a5a5d68` contém um **GitHub PAT** em `.gitconfig:10`
> (commits `0bd5a49`, `504b67c`, `8541ea0`…). O GitHub Push Protection **rejeita** o push da tag
> (`GH013`). A tag existe **localmente**; o push fica pendente de decisão do dono (não publicar segredo).

## 3. Stashes e worktree do `ryzen-win` → branches `wip/windows-<id>`

| Branch | SHA | Origem |
|---|---|---|
| `wip/windows-stash` | `d3c53c8` | `recuperado/ryzen-win/wip/stash` |
| `wip/windows-stash-1` | `73df54f` | `recuperado/ryzen-win/wip/stash-1` |
| `wip/windows-stash-2` | `847d849` | `recuperado/ryzen-win/wip/stash-2` |
| `wip/windows-stash-3` | `a3d63a0` | `recuperado/ryzen-win/wip/stash-3` |
| `wip/windows-stash-4` | `2c6c5dd` | `recuperado/ryzen-win/wip/stash-4` |
| `wip/windows-worktree-dotfiles_` | `0bc565c` | `recuperado/ryzen-win/wip/worktree-dotfiles_` |

Nada se perde; o dono decide depois o destino de cada WIP.

## 4. Veredito

Com os itens 1–3 o `dotfiles` passa a **cobrir por conteúdo** tudo que o `dotfiles-windows` tinha
fora do próprio `dotfiles`: o commit `7a034380` (no-op material — já contido em `f9ee700`), a tag
`v1.0.0` (preservada localmente, push bloqueado por segredo) e os 5 stashes + 1 worktree (preservados
como branches `wip/windows-*`). **Não excluir o `dotfiles-windows`** até o dono confirmar (o push da
tag segue pendente por causa do segredo na história antiga).
