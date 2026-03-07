# AI WIP Tracker

Atualizado em: 2026-03-07 13:46 UTC

Fonte de verdade operacional para continuidade de tarefas dos agentes de IA.

## Regras operacionais

- Toda solicitacao acionavel deve passar por preflight de pendencias.
- Se houver itens em `Doing`, perguntar ao usuario:
  - concluir pendencias antes (`concluir_primeiro`), ou
  - manter pendencias e registrar no roadmap (`roadmap_pendente`).
- Durante execucao, registrar progresso incremental no ledger.
- O item ativo deve permanecer em `Doing` enquanto a execucao estiver em curso.
- Ultimo passo obrigatorio antes de encerrar demanda: mover item ativo de
  `Doing` para `Done` e remover do log incremental as demandas finalizadas.

## Doing

<!-- ai-worklog:doing:start -->
| ID | Tarefa | Branch | Responsavel | Inicio UTC | Ultima atualizacao UTC | Proximo passo | Bloqueios |
| --- | --- | --- | --- | --- | --- | --- | --- |
| (sem itens) | - | - | - | - | - | - | - |
<!-- ai-worklog:doing:end -->

## Done

<!-- ai-worklog:done:start -->
| ID | Tarefa | Branch | Responsavel | Inicio UTC | Concluido UTC | Resultado |
| --- | --- | --- | --- | --- | --- | --- |
| WIP-20260307-ROADMAP-EXTRA-APPROVALS | Registrar aprovacoes adicionais do usuario no roadmap para bloqueio de signing, fronteira de df/assets/img e revisao estrutural de scripts. | feat/test-harness-hybrid | ai-agent | 2026-03-07 13:44 UTC | 2026-03-07 13:46 UTC | As tres aprovacoes adicionais do usuario foram registradas no roadmap: signer de automacao para desbloquear checkpoint commit entrou em Now, e as decisoes sobre fronteira de scr... / evidencias: task ai:roadmap:regist... |
| WIP-20260307-DOC-LINKS-HARDENING | Endurecer a governanca de links documentais e eliminar referencias internas/externas sem link nos docs governados. | feat/test-harness-hybrid | ai-agent | 2026-03-07 13:29 UTC | 2026-03-07 13:41 UTC | Endurecimento definitivo da governanca de links documentais, com varredura dos docs governados, contratos atualizados e validador ampliado para texto corrido, tabelas, URLs exte... / evidencias: task docs:check:window... |
| WIP-20260307-ROADMAP-APPROVALS | Aplicar aprovacao em massa das sugestoes pendentes do roadmap desta worktree | feat/test-harness-hybrid | ai-agent | 2026-03-07 13:10 UTC | 2026-03-07 13:27 UTC | Todas as sugestoes pendentes do roadmap desta worktree foram aprovadas e rastreadas corretamente; o backend de roadmap passou a remover pendencias semanticas mesmo com links Mar... / evidencias: uv run --locked python... |
| WIP-20260307-DOC-LINKING | Endurecer a regra de linkagem interna em docs/comentarios e eliminar citacoes de arquivos do repo sem link quando viavel | feat/test-harness-hybrid | ai-agent | 2026-03-07 12:18 UTC | 2026-03-07 12:44 UTC | Regra documental endurecida para exigir links internos viaveis, Curador Repo assumido como autoridade de linkagem, validate_docs.py ampliado para cobrar referencias internas sem... / evidencias: task docs:check:window... |
| WIP-20260307-QUALITY-IMPORTS | Importar camada de qualidade | feat/test-harness-hybrid | ai-agent | 2026-03-07 10:49 UTC | 2026-03-07 11:46 UTC | Camada de qualidade cross-repo importada com pyproject/uv, .venv por plataforma, ruff, ty, pytest, pymarkdownlnt, yamllint, actionlint, gitleaks, validacao documental e docs cen... / evidencias: task ci:workflow:sync:... |
| WIP-20260307-DOCS-ATUALIZACAO | Auditar e atualizar a documentacao do repo para refletir as funcionalidades atuais, com README raiz servindo como catalogo confiavel do projeto. | feat/test-harness-hybrid | ai-agent | 2026-03-07 10:38 UTC | 2026-03-07 10:47 UTC | A documentacao central do repo foi auditada e atualizada para refletir o estado funcional atual: README raiz virou catalogo operacional do projeto, docs/README organizou a leitu... / evidencias: task ai:validate:windo... |
| WIP-20260307-ALIASES-CANONICOS | Centralizar aliases por ambiente nos arquivos principais e reorganizar a estrutura dos arquivos de aliases e Git configs para ficarem mais claros e canonicos | feat/test-harness-hybrid | ai-agent | 2026-03-07 10:25 UTC | 2026-03-07 10:36 UTC | Aliases por ambiente foram centralizados nos arquivos canonicos: df/.aliases concentra o shell Unix, df/powershell/aliases.ps1 concentra o PowerShell e df/git/.gitconfig-base vi... / evidencias: bash -n em df/.aliases... |
| WIP-20260307-CI-TASK-PARITY | Endurecer a paridade entre workflows de CI/CD, tasks canonicas e documentacao operacional do repo | feat/test-harness-hybrid | ai-agent | 2026-03-07 10:17 UTC | 2026-03-07 10:18 UTC | Paridade entre workflows, tasks e catalogos de CI/CD foi endurecida com entrypoints canonicos por workflow/job, docs atualizadas e gatilho do ai-governance ampliado para cobrir... / evidencias: task ci:workflow:sync:c... |
| WIP-20260307-IA-REFERENCIAS | Pesquisar referencias externas de dotfiles com forte uso de IA e registrar sugestoes aderentes ao roadmap do repo | feat/test-harness-hybrid | ai-agent | 2026-03-07 09:45 UTC | 2026-03-07 09:54 UTC | Referencias externas de dotfiles com forte uso de IA foram auditadas, documentadas em AI-SOURCE-AUDIT e convertidas em quatro sugestoes pendentes no roadmap para avaliacao humana. / evidencias: docs/AI-SOURCE-AUDIT.md... |
| WIP-20260307-ESTRUTURA | Auditar a estrutura completa do repositorio e simplificar layout de pastas/arquivos conforme boas praticas e contratos do projeto | feat/test-harness-hybrid | ai-agent | 2026-03-07 09:31 UTC | 2026-03-07 09:43 UTC | Estrutura do repo simplificada e reorganizada: legado isolado em archive/, prompt packs movidos para .agents/prompts/legacy, docs agrupados por funcao, nomes canonicos corrigido... / evidencias: task ai:validate:windo... |
| WIP-20260307-090534 | Auditar o repo inteiro em busca de simplificacoes, codigo e arquivos desnecessarios, pontos de falha e melhorias de performance, resiliencia e manutencao | feat/test-harness-hybrid | ai-agent | 2026-03-07 09:05 UTC | 2026-03-07 09:28 UTC | Auditoria de simplificacao concluida com commits checkpoint por contexto: harnesses reais de relink, reducao de drift estrutural, refresh de docs do repo e ajustes de workspace. / evidencias: task test:unit:powershell... |
| WIP-20260307-084440 | Auditar o repo inteiro e atualizar a documentacao para refletir as funcionalidades atuais, incluindo README raiz com catalogo de funcionalidades | feat/test-harness-hybrid | ai-agent | 2026-03-07 08:44 UTC | 2026-03-07 09:03 UTC | Duplicacao estrutural consolidada: .agents como fonte canonica, .codex reduzido a README e arvore vazia removida; quality-foundation passou a reutilizar tasks oficiais; docs e R... / evidencias: python scripts/validat... |
| WIP-20260307-083916 | Auditar .gitignore e corrigir exclusoes indevidas da camada .agents e demais ativos versionados | feat/test-harness-hybrid | ai-agent | 2026-03-07 08:39 UTC | 2026-03-07 08:43 UTC | Auditoria completa do .gitignore concluida; regra antiga que ocultava a arvore canonica .agents foi corrigida e entradas legadas de df/powershell/Modules, df/powershell/Scripts... / evidencias: git check-ignore -v -n... |
| WIP-20260307-081800 | Revisar agentes e skills para aderencia total aos contratos, schemas e regras atualizadas | feat/test-harness-hybrid | ai-agent | 2026-03-07 08:18 UTC | 2026-03-07 08:38 UTC | Fonte canonica da camada de IA migrada para .agents com subpastas; .codex reduzido a README de compatibilidade; scripts, validator, docs e workflow ajustados para o novo contrato. / evidencias: python scripts/validate... |
| WIP-20260307-GAP-IMPORTS | validacao cross-platform concluida | feat/test-harness-hybrid | ai-agent | 2026-03-07 07:47 UTC | 2026-03-07 08:15 UTC | Auditoria integral dos repos-fonte concluida e delta remanescente importado: backend Python de ai-chat-intake/route/delegate, orchestrator declarativo, smoke eval, catalogos TAS... / evidencias: task ai:validate:windo... |
| WIP-20260307-GOV-AGENTS | Criar agentes e skills perenes de arquitetura e integracoes criticas | feat/test-harness-hybrid | ai-agent | 2026-03-07 03:34 UTC | 2026-03-07 04:16 UTC | Fluxo formal de licoes aprendido implementado, camada declarativa de IA ampliada com agents/orchestration/rules/evals, novos gates permanentes de arquitetura e integracoes criti... / evidencias: task ai:validate:windo... |
| WIP-20260307-BACKLOG-ADVANCE | Avancar backlog pendente do roadmap de qualidade e harnesses | feat/test-harness-hybrid | ai-agent | 2026-03-07 03:12 UTC | 2026-03-07 03:32 UTC | Governanca base endurecida, roadmap atualizado e harnesses reais de relink entregues para Linux e Windows, com workflow dedicado de integracao e injecao minima de contexto nos b... / evidencias: task ai:validate:windo... |
| WIP-20260307-ROADMAP-CYCLE-FIX | Corrigir duplicacao de ciclos em ROADMAP-DECISIONS | feat/test-harness-hybrid | ai-agent | 2026-03-07 02:01 UTC | 2026-03-07 02:06 UTC | Duplicacao de ciclos no ROADMAP-DECISIONS corrigida com deduplicacao estrutural por ciclo no backend e regressao automatizada. / evidencias: py -3 -m unittest tests.python.ai_roadmap_test; task test:unit:python:window... |
| WIP-20260307-LIVE-DOING | Endurecer a regra de Doing em tempo real e alinhar contratos de continuidade | feat/test-harness-hybrid | ai-agent | 2026-03-07 01:52 UTC | 2026-03-07 01:58 UTC | Regra de Doing em tempo real endurecida, bug do resumo incremental corrigido e backfill do tracker refeito com todos os blocos relevantes desta worktree. / evidencias: task test:unit:python:windows; task ai:validate:w... |
| WIP-20260307-003625 | Importar governanca robusta de commits/PRs/branches e gates de continuidade de IA a partir de py-bootstrap e cr-automations | feat/test-harness-hybrid | ai-agent | 2026-03-07 00:36 UTC | 2026-03-07 00:36 UTC | Governanca de Git e WIP importada para a worktree com hooks, validadores, workflow de PR, tracker de continuidade e testes Python dedicados. / evidencias: commit 5e06ba6; task conventions:check:branch; task conventions:check:commits; task test:unit:python:windows |
| WIP-20260306-223413 | Criar a fundacao inicial de IA, qualidade e automacao da worktree de test harness | feat/test-harness-hybrid | ai-agent | 2026-03-06 22:34 UTC | 2026-03-06 22:34 UTC | Fundacao inicial criada com AGENTS, modelo operacional de IA, cartoes em `.agents`, skills em `.agents/skills`, tasks de governanca e workflows base de qualidade. / evidencias: commit dca8f8d; task ai:validate; task ci:validate:windows |
| WIP-20260306-ROADMAP-WIP | Importar camada de roadmap ligada ao AI-WIP e endurecer governança de rastreabilidade | feat/test-harness-hybrid | ai-agent | 2026-03-07 01:17 UTC | 2026-03-07 01:47 UTC | Contrato perene de auditoria exaustiva implementado, auditoria versionada das tres fontes registrada, roadmap ligado ao backend real, tasks/validadores/testes atualizados. / evidencias: task ai:roadmap:ensure:windows;... |
<!-- ai-worklog:done:end -->

## Log incremental - Tarefas nao finalizadas ainda

<!-- ai-worklog:log:start -->
| Data/Hora UTC | ID | Status | Resumo | Proximo passo | Bloqueios | Contexto | Notas |
| --- | --- | --- | --- | --- | --- | --- | --- |
| (sem itens) | - | - | - | - | - | - | - |
<!-- ai-worklog:log:end -->
