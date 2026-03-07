# AI WIP Tracker

Atualizado em: 2026-03-07 09:17 UTC

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
| WIP-20260307-090534 | Auditar o repo inteiro em busca de simplificacoes, codigo e arquivos desnecessarios, pontos de falha e melhorias de performance, resiliencia e manutencao | feat/test-harness-hybrid | ai-agent | 2026-03-07 09:05 UTC | 2026-03-07 09:17 UTC | Separar os pendentes em blocos coerentes de commit: governanca/IA, harnesses/bootstrap e simplificacao/higiene. | - |
<!-- ai-worklog:doing:end -->

## Done

<!-- ai-worklog:done:start -->
| ID | Tarefa | Branch | Responsavel | Inicio UTC | Concluido UTC | Resultado |
| --- | --- | --- | --- | --- | --- | --- |
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
| 2026-03-07 09:17 UTC | WIP-20260307-090534 | doing | Auditar o repo inteiro em busca de simplificacoes, codigo e arquivos desnecessarios, pontos de falha e melhorias de performance, resiliencia e manutencao | Inventariar hotspots por dominio e classificar em remocao segura, simplificacao segura e backlog arquitetural. | - | bootstrap,df,scripts,tests,.github,docs,.agents,Taskfile.yml,README.md | inicio da tarefa |
| 2026-03-07 09:17 UTC | WIP-20260307-090534 | doing | Contexto operacional fixado: esta rodada deve usar sempre a worktree C:\Users\pablo\dotfiles-test-harness como fonte de verdade. Iniciando pacote de simplificacao segura: placeholder stubs, JSON valido para mcp.json e... | Aplicar ajustes de baixo risco e registrar backlog arquitetural para monolitos e legado historico. | - | bootstrap,df,docs,Taskfile.yml,ROADMAP | checkpoint incremental |
| 2026-03-07 09:17 UTC | WIP-20260307-090534 | doing | Ajustes seguros aplicados: symlinks.ps1 virou wrapper para o fluxo canonico de relink, placeholders vazios passaram a ser stubs explicitos e mcp.json ficou um JSON valido. Sugestoes estruturais maiores foram registrad... | Rodar validacoes, revisar o roadmap atualizado e fechar a rodada com consolidado objetivo de oportunidades e riscos residuais. | - | bootstrap,df,docs,ROADMAP,LICOES-APRENDIDAS.md | checkpoint incremental |
| 2026-03-07 09:17 UTC | WIP-20260307-090534 | doing | Enforcement de commit checkpoint entre rodadas implementado no ai:worklog:check, nos contratos de governanca e na skill de continuidade. Adicionadas regressões automatizadas para worktree dirty com e sem Doing ativo. | Validar ai:worklog:check, ai:validate e a suite Python; depois registrar a licao perene da nova regra. | - | scripts/ai-worklog.py,tests/python/ai_worklog_test.py,AGENTS.md,.agents/docs,Taskfile.yml | checkpoint incremental |
| 2026-03-07 09:17 UTC | WIP-20260307-090534 | doing | A governanca de commit checkpoint entre rodadas foi endurecida no backend, nos contratos e na licao LA-010. O proximo passo e reorganizar o indice Git e fechar commits por contexto para reduzir o acúmulo atual de pend... | Separar os pendentes em blocos coerentes de commit: governanca/IA, harnesses/bootstrap e simplificacao/higiene. | - | scripts/ai-worklog.py,tests/python/ai_worklog_test.py,AGENTS.md,.agents,LICOES-APRENDIDAS.md,Taskfile.yml | checkpoint incremental |
<!-- ai-worklog:log:end -->
