# AGENTS.md

## Missao

Manter este repo de dotfiles confiavel, testavel e reproduzivel em Windows host e Ubuntu WSL.

## Escopo e precedencia

- Este arquivo define as regras permanentes de trabalho da IA neste repo.
- [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md) complementa o contrato com memoria normativa incremental.
- Em caso de conflito:
  1. politicas da plataforma e do sistema
  2. instrucoes explicitas do usuario na sessao atual
  3. este [`AGENTS.md`](AGENTS.md)
  4. [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md)

## Idioma

- Escrever documentacao, comentarios e respostas em portugues.
- Preferir ASCII nos arquivos do repo, exceto quando um arquivo existente exigir Unicode.

## Leitura minima antes de editar

1. [`CONTEXT.md`](CONTEXT.md)
2. [`docs/test-strategy.md`](docs/test-strategy.md)
3. [`docs/ai-operating-model.md`](docs/ai-operating-model.md)
4. [`docs/AI-WIP-TRACKER.md`](docs/AI-WIP-TRACKER.md)
5. [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md)
6. [`docs/bootstrap-flow.md`](docs/bootstrap-flow.md) quando a tarefa tocar bootstrap
7. [`Taskfile.yml`](Taskfile.yml)

## Leitura integral obrigatoria ao retomar do zero

- Sempre que a sessao de IA voltar do zero ou perder continuidade confiavel,
  reler integralmente todos os arquivos resolvidos por
  [`docs/AI-STARTUP-GOVERNANCE-MANIFEST.md`](docs/AI-STARTUP-GOVERNANCE-MANIFEST.md)
  antes de qualquer operacao relevante.
- Essa releitura integral e obrigatoria em queda de energia, travamento,
  limpeza de cache, limpeza de sessoes, troca de worktree, troca de app, troca
  de modelo ou qualquer retomada sem contexto comprovadamente fiel.
- Nessas retomadas, e proibido operar por amostragem, memoria parcial,
  presuncao, estimativa ou "parece que eu ja li isso".
- Nessas retomadas, a IA deve consultar tambem
  [`docs/AI-CHAT-CONTRACTS-REGISTER.md`](docs/AI-CHAT-CONTRACTS-REGISTER.md)
  para avisar o usuario sobre contratos nascidos no chat e ainda nao
  promovidos para a governanca oficial.

## Skills locais

- [`.agents/skills/dotfiles-bootstrap`](.agents/skills/dotfiles-bootstrap)
- [`.agents/skills/dotfiles-architecture-modernization`](.agents/skills/dotfiles-architecture-modernization)
- [`.agents/skills/dotfiles-critical-integrations`](.agents/skills/dotfiles-critical-integrations)
- [`.agents/skills/dotfiles-lessons-governance`](.agents/skills/dotfiles-lessons-governance)
- [`.agents/skills/dotfiles-python-review`](.agents/skills/dotfiles-python-review)
- [`.agents/skills/dotfiles-powershell-review`](.agents/skills/dotfiles-powershell-review)
- [`.agents/skills/dotfiles-automation-review`](.agents/skills/dotfiles-automation-review)
- [`.agents/skills/dotfiles-orthography-review/SKILL.md`](.agents/skills/dotfiles-orthography-review/SKILL.md)
- [`.agents/skills/dotfiles-secrets-rotation`](.agents/skills/dotfiles-secrets-rotation)
- [`.agents/skills/task-routing-and-decomposition`](.agents/skills/task-routing-and-decomposition)
- [`.agents/skills/dotfiles-test-harness`](.agents/skills/dotfiles-test-harness)
- [`.agents/skills/dotfiles-repo-governance`](.agents/skills/dotfiles-repo-governance)
- [`.agents/skills/wip-continuity-governance`](.agents/skills/wip-continuity-governance)

Leia a skill mais proxima do escopo antes de editar arquivos relevantes.

## Guardrails

- Preferir `task` e scripts existentes antes de criar fluxos paralelos.
- Manter tasks e scripts worktree-friendly usando `{{.TASKFILE_DIR}}` quando aplicavel.
- Preservar paridade entre Windows e WSL sempre que a mudanca tocar bootstrap, links, auth ou Git.
- Tratar caminhos canonicos absolutos como fonte de verdade.
- Validar estado final e idempotencia, nao apenas `exit code`.
- Em retomadas do zero, usar como base obrigatoria a leitura integral definida em
  [`docs/AI-STARTUP-GOVERNANCE-MANIFEST.md`](docs/AI-STARTUP-GOVERNANCE-MANIFEST.md).
- Em retomadas do zero, gerar ou atualizar o relatorio operacional da sessao
  com `task ai:startup:session` antes de decidir trabalho por memoria residual.
- Nunca operar por amostragem quando a tarefa envolver importar, adaptar, comparar ou consolidar contratos de outro repo.
- Qualquer importacao ou adaptacao cross-repo exige auditoria estrutural exaustiva antes de editar:
  contratos globais, docs, tasks, scripts, workflows, hooks, validadores, testes,
  agentes, skills, orquestracao, regras, evals e relacoes entre esses elementos.
- Toda auditoria cross-repo deve deixar rastreabilidade versionada em [`docs/AI-SOURCE-AUDIT.md`](docs/AI-SOURCE-AUDIT.md)
  antes de importar regras, logicas ou ativos declarativos.
- Quando houver fonte externa, agir com barra de qualidade de engenheiro/arquiteto senior:
  sem trabalho parcial, sem "copiar so o que parece importante" e sem pular validacao disponivel.
- Em toda analise substantiva, acionar em paralelo o gate de arquitetura/modernizacao para revisar:
  simplificacao, modularidade, performance, resiliencia, testabilidade, I/O, memoria, CPU e possiveis tecnologias/abordagens mais adequadas.
- Em toda mudanca versionada que altere texto, comentario, docstring, doc,
  configuracao textual ou identificadores legiveis, acionar tambem `pascoalete`
  com [`$dotfiles-orthography-review`](.agents/skills/dotfiles-orthography-review/SKILL.md)
  em modo consultivo para revisar ortografia tecnica e higiene do dicionario `cspell`.
- Em qualquer mudanca que toque bootstrap, auth, secrets, CI, CLI, sync ou integracoes do workstation,
  acionar tambem o guardiao de integracoes criticas para proteger `gh`, `op`, `sops`, `age`, `ssh-agent`,
  assinatura Git, secrets e demais ferramentas de missao critica.
- Em qualquer mudanca que toque rotacao, revogacao, expiracao, backup ou inventario
  de credenciais, chaves SSH, PATs, service accounts, `sops+age` ou notificacao
  de segredos, acionar tambem `secrets-rotation-governor` com a skill
  [`$dotfiles-secrets-rotation`](.agents/skills/dotfiles-secrets-rotation).
- Em qualquer mudanca de codigo ou automacao, acionar a skill e o revisor
  especialista correspondente a familia de arquivo afetada: Python com
  [`$dotfiles-python-review`](.agents/skills/dotfiles-python-review),
  PowerShell com
  [`$dotfiles-powershell-review`](.agents/skills/dotfiles-powershell-review)
  ou shell/workflow/Taskfile/Docker com
  [`$dotfiles-automation-review`](.agents/skills/dotfiles-automation-review).
  Fechamento com parecer reprovado ou sem revisor especializado aplicavel e
  invalido.
- Worktrees e rodadas de automacao local devem preferir signer tecnico dedicado,
  aplicado via `task git:signing:mode:automation`; signer humano continua como
  padrao fora da worktree tecnica e nao deve ser "bypassado" por variavel que
  silencie a aprovacao da identidade humana.
- Ao ler o board e decidir a proxima puxada, priorizar da direita para a
  esquerda o que estiver mais perto de terminar; quando um item ativo estiver
  bloqueado por outra issue, `concluir_primeiro` passa a significar concluir ou
  puxar apenas o work item minimo que o destrava diretamente, nunca demanda
  nova sem relacao com esse WIP.
- Manter o item ativo em `Doing` durante toda a execucao relevante e so move-lo para `Done`
  imediatamente antes da resposta final ao usuario.
- `Jira` e a fonte primaria do fluxo vivo; [`docs/AI-WIP-TRACKER.md`](docs/AI-WIP-TRACKER.md)
  funciona como fallback contingencial do repo.
- Quando a contingencia local realmente precisar assumir rastreabilidade
  temporaria, registrar o evento em
  [`docs/AI-FALLBACK-LEDGER.md`](docs/AI-FALLBACK-LEDGER.md) e voltar ao modo
  primario so depois de classificar cada registro como `drained`,
  `reconciled` ou `obsolete`.
- Ao concluir uma rodada e permanecerem mudancas locais coerentes, criar commit de fechamento
  antes de iniciar novo escopo; `task ai:worklog:check` deve bloquear worktree suja sem `Doing` ativo.
- Nenhum `done` e valido sem revisar [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md) e registrar explicitamente
  `capturada` ou `sem_nova_licao`.
- Reprovacao de `pascoalete` nao bloqueia `done`, PR ou commit, mas deve
  registrar log consultivo e abrir pendencia rastreavel se nao houver correcao
  na rodada atual.
- Commits devem ser atomicos, semanticamente coesos, ligados a uma unica issue Jira real
  e preferencialmente auto-testaveis.
- Branches novas devem seguir `<type>/<jira-key>-<slug>` e nao usar emoji;
  branches legadas pre-integracao com Jira so podem permanecer como excecao historica.
- Commit e PR title devem seguir `emoji + conventional commit`, carregar uma unica
  chave Jira real no subject e respeitar o maximo recomendado de 72 caracteres.
- Cada branch deve carregar um unico contexto coerente; separar assuntos independentes em branches diferentes.
- Ao retomar demanda antiga, abrir branch nova a partir de `main`, salvo evidencia objetiva de
  que a branch anterior ainda e a trilha certa.
- Apos merge ou absorcao em `main`, remover branches e worktrees desnecessarias assim que
  a trilha estiver segura.
- Em documentacao e comentarios que suportem links clicaveis, toda citacao
  viavel a arquivo, pasta, task, workflow, script do repo ou referencia
  externa deve usar link explicito para o alvo, nao apenas texto solto ou
  inline code. Paths locais fora do repo so podem ficar sem link quando nao
  houver destino clicavel razoavel no proprio repositorio.
- Mudancas em documentacao, catalogos e comentarios Markdown devem passar pelo
  `Curador Repo`, que e o responsavel por higiene documental e linkagem interna.
- Nao versionar runtime local de IA: `.gemini/`, sessoes, auth, caches, browser profiles e historico.
- No repo, [`.codex/`](.codex/) e apenas ponte de compatibilidade e deve conter so [`README.md`](README.md).
- Se um artefato de IA for declarativo, portavel e sem segredo, mover a fonte canonica para o repo e materializar no `HOME` via bootstrap, link ou copia controlada.

## Fluxo operacional minimo

1. Ler o contexto minimo.
2. Rodar `task ai:worklog:check` antes de execucao relevante e, se houver WIP
   ativo, tratar `concluir_primeiro` como concluir ou destravar primeiro.
3. Se houver reuso ou adaptacao de outro repo, concluir a auditoria exaustiva e registrar o gap analysis.
4. Escolher a skill local adequada.
5. Acionar os gates paralelos obrigatorios de arquitetura/modernizacao e, quando aplicavel, integracoes criticas.
6. Fazer a menor mudanca coerente com a arquitetura do repo.
7. Validar localmente com tasks, lints e testes cabiveis.
8. Manter o item em `Doing` enquanto a execucao estiver em curso.
9. So no ultimo passo tecnico, revisar licoes, mover o item para `Done` e validar `task ai:worklog:close:gate`.
10. Se a rodada terminou e a worktree ainda estiver dirty, criar commit de fechamento antes de aceitar novo escopo.
11. Manter commit e PR no padrao `emoji + conventional commits`.
