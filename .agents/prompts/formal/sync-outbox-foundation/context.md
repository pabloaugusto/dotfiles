# Contexto Do Pack

<!-- cspell:words reutilizavel agnostica sincronizacao solucao repositorio validacao implementacao portaveis duravel separacao canonico LICOES worktree -->

Este prompt pack existe para materializar uma trilha formal e reutilizavel para
arquitetura agnostica de sincronizacao de artefatos vivos de IA, sem acoplar a
solucao ao nome atual do repositorio.

## Contexto especifico do projeto atual

- o projeto atual ja possui uma arvore canonica de prompt packs em
  [`.agents/prompts/`](../../README.md)
- o projeto atual ja distingue contrato declarativo versionado de runtime local
  fora do Git em [`AGENTS.md`](../../../../AGENTS.md) e
  [`docs/ai-operating-model.md`](../../../../docs/ai-operating-model.md)
- o projeto atual ja possui trilhas versionadas de governanca, startup,
  validacao, review, lessons e closeout que precisam ser reutilizadas
- a implementacao derivada deste pack deve respeitar a governanca local do repo
  atual, mas nascer com nomenclatura e arquitetura portaveis para outros repos

## Fronteiras

- este pack nao autoriza persistir runtime duravel dentro do repo
- este pack nao autoriza tratar `.cache` como fonte de verdade para dados que
  nao podem ser perdidos
- este pack exige a separacao entre artefato canonico versionado, outbox local
  duravel e fonte remota perene
- este pack nao autoriza migracao cega de todos os `.md` vivos para destino
  remoto sem classificacao previa

## Dependencias e ordem segura

- prerequisite packs: nenhum
- preflight packs:
  - `startup-alignment`
- ordem segura:
  1. checar `startup-alignment` quando a continuidade da sessao nao estiver
     comprovadamente integra
  2. executar `sync-outbox-foundation`
  3. so depois rodar packs de dominio que consumam a fundacao de sync

## Arquivos vivos relacionados

- [`AGENTS.md`](../../../../AGENTS.md)
- [`LICOES-APRENDIDAS.md`](../../../../LICOES-APRENDIDAS.md)
- [`docs/ai-operating-model.md`](../../../../docs/ai-operating-model.md)
- [`docs/AI-STARTUP-AND-RESTART.md`](../../../../docs/AI-STARTUP-AND-RESTART.md)
- [`docs/AI-DELEGATION-FLOW.md`](../../../../docs/AI-DELEGATION-FLOW.md)
- [`docs/TASKS.md`](../../../../docs/TASKS.md)
- [`config/ai/`](../../../../config/ai/)
- [`Taskfile.yml`](../../../../Taskfile.yml)

## Resultado esperado

- a arvore [`.agents/prompts/`](../../README.md) passa a ter um pack formal e
  catalogado para arquitetura agnostica de sync
- a implementacao derivada deste pack deve resolver `workspace_id` e
  `runtime_environment_id` como identidades diferentes e complementares
- a implementacao derivada deste pack deve preparar o caminho para `Confluence`
  como fonte perene de historico sem depender de worktree ou nome do repo
