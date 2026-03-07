# Licoes Aprendidas

Historico incremental das regras operacionais que nao devem depender de memoria de chat.

## Leitura obrigatoria

- A cada novo comando do usuario, a IA deve ler:
  - [`AGENTS.md`](AGENTS.md)
  - [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md)
- Em caso de conflito entre regra normativa e licao operacional, prevalece o [`AGENTS.md`](AGENTS.md).

## Criterio de registro de novas licoes

- Registrar somente quando houver ganho real de eficiencia, qualidade, resiliencia ou precisao.
- Priorizar recorrencias, incidentes relevantes, workarounds comprovados e decisoes que reduzam drift.
- Cada licao deve ser curta, verificavel e acionavel.

## Formato recomendado de entrada

- `ID`: identificador curto, por exemplo `LA-004`
- `Contexto`: onde o problema apareceu
- `Regra`: comportamento que passa a ser obrigatorio
- `Solucao validada`: o que efetivamente resolveu
- `Prevencao`: como evitar a regressao
- `Validacao`: comandos, testes ou gates usados

## Curadoria e manutencao

- Evitar duplicacoes; consolidar licoes equivalentes.
- Promover para [`AGENTS.md`](AGENTS.md) apenas regras estaveis e amplas.
- Manter aqui os detalhes operacionais e a memoria incremental das rodadas.

## Catalogo de licoes

<!-- ai-lessons:catalog:start -->
## LA-001 - Auditoria exaustiva antes de importacao cross-repo

- Contexto: importar governanca, agentes, skills, workflows ou contratos de outros repos por amostragem gerou lacunas e drift.
- Regra: qualquer reuso cross-repo deve comecar por auditoria estrutural exaustiva dos dominios relevantes.
- Solucao validada: cobrir contratos globais, docs, tasks, scripts, workflows, hooks, validadores, testes, agentes, skills, orquestracao, regras, evals e relacoes entre esses elementos antes de editar.
- Prevencao: registrar o inventario e o gap analysis em [`docs/AI-SOURCE-AUDIT.md`](docs/AI-SOURCE-AUDIT.md) antes da importacao.
- Validacao: `task ai:validate`, revisao do inventario versionado e rastreabilidade dos ativos importados.

## LA-002 - [`.agents`](.agents) e a fonte canonica; [`.codex`](.codex) e apenas ponte legada

- Contexto: fontes diferentes usam camadas distintas como origem declarativa; sem fronteira explicita, a estrutura fica ambigua.
- Regra: neste repo, [`.agents/`](.agents/) concentra cartoes, skills, registry, orchestration, rules, evals e config; [`.codex/`](.codex/) deve conter somente um [`README.md`](README.md) de compatibilidade.
- Solucao validada: estruturar [`.agents/`](.agents/) com subpastas e migrar toda a camada declarativa para la, deixando [`.codex/README.md`](.codex/README.md) apontar para a fonte canonica.
- Prevencao: nao permitir contratos declarativos manuais em [`.codex/`](.codex/) nem duplicar a mesma regra em duas arvores.
- Validacao: `task ai:validate` deve falhar em caso de drift estrutural ou ausencia de artefatos obrigatorios.

## LA-003 - `Doing` deve permanecer vivo ate o fechamento real da rodada

- Contexto: fechar o worklog cedo demais faz o tracker parecer "limpo" enquanto a execucao ainda esta acontecendo.
- Regra: o item ativo deve permanecer em `Doing` durante toda a execucao relevante.
- Solucao validada: mover para `Done` apenas imediatamente antes da resposta final, quando nao houver mais trabalho tecnico pendente naquela rodada.
- Prevencao: reforcar `task ai:worklog:close:gate` e manter o log incremental fiel ao estado real.
- Validacao: `task ai:worklog:close:gate`.

## LA-004 - Toda finalizacao de worklog exige revisao explicita de licoes

- Contexto: o repo passou a ter tracker e roadmap, mas ainda permitia fechar uma rodada sem avaliar se havia aprendizado novo.
- Regra: nenhum worklog pode ser encerrado sem registrar uma revisao explicita em [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md), com decisao `capturada` ou `sem_nova_licao`.
- Solucao validada: integrar [`scripts/ai-lessons.py`](scripts/ai-lessons.py) ao [`scripts/ai-worklog.py`](scripts/ai-worklog.py), registrar revisao no momento do `done` e bloquear o fechamento global se algum item concluido estiver sem revisao.
- Prevencao: exigir `task ai:lessons:check` em CI e no gate local de governanca.
- Validacao: `task ai:lessons:check`, `task ai:worklog:close:gate`.

## LA-005 - Importacao cross-repo precisa cobrir todas as camadas aplicaveis, nao so licoes

- Contexto: transportar apenas licoes aprendidas ou apenas snippets isolados produz governanca parcial e desconexa.
- Regra: a adaptacao deve considerar todas as camadas uteis ainda ausentes aqui, incluindo agentes, skills, catalogos, rules, orchestration, evals, validadores, workflows, docs e gates.
- Solucao validada: auditar `py-bootstrap`, `cr-automations` e `iageny` por dominio, comparar com o estado atual e importar os ativos compatveis com a arquitetura de dotfiles.
- Prevencao: documentar em [`docs/AI-SOURCE-AUDIT.md`](docs/AI-SOURCE-AUDIT.md) o que foi adotado agora, o que foi adaptado e o que ficou de fora com justificativa.
- Validacao: revisao do gap map e `task ai:validate`.

## LA-006 - Arquitetura e modernizacao precisam de um gate paralelo permanente

- Contexto: em repos operacionais como este, mudancas pequenas podem introduzir acoplamento, complexidade acidental, regressao de performance e sobrecarga de manutencao sem sinais imediatos.
- Regra: toda analise substantiva deve passar por um agente especializado em arquitetura, refactor, performance, simplificacao, resiliencia e testabilidade, atuando em paralelo ao fluxo principal.
- Solucao validada: manter um agente e skill dedicados para catalogar melhorias, apontar gaps, identificar drifts e retroalimentar backlog/roadmap.
- Prevencao: registrar os proximos passos e riscos estruturais no roadmap em vez de deixar insights presos no chat.
- Validacao: revisar [`docs/AI-DELEGATION-FLOW.md`](docs/AI-DELEGATION-FLOW.md), [`docs/AI-AGENTS-CATALOG.md`](docs/AI-AGENTS-CATALOG.md) e os gates da camada canonica [`.agents/`](.agents/).

## LA-007 - Integracoes criticas exigem guardiao proprio

- Contexto: `gh`, `op`, `sops`, `age`, `ssh-agent`, assinatura Git e demais ferramentas criticas podem parecer estaveis mesmo quando um ajuste colateral quebrou a experiencia real do ambiente.
- Regra: qualquer mudanca que toque bootstrap, auth, secrets, CI, CLI ou integracoes do workstation deve passar por um guardiao de integracoes criticas.
- Solucao validada: ter um agente/skill dedicado para revisar disponibilidade, login, secrets, fluxo seguro e regressao de ferramentas de missao critica antes do encerramento.
- Prevencao: usar caminhos canonicos, `checkEnv`, tasks existentes e gates de ambiente como fonte de verdade, nunca suposicoes locais.
- Validacao: `task env:check`, `task ci:validate`, `task ai:validate`.

## LA-008 - Backends Python da camada de IA precisam ser portaveis entre Windows e WSL

- Contexto: O backend novo de intake/route/delegate e smoke eval falhou no Linux porque o runtime real nao tinha tomllib, apesar de passar no Windows.
- Regra: Toda nova automacao Python deste repo deve ser compativel com o runtime disponivel em Windows e WSL, sem assumir Python 3.11+ sem fallback.
- Solucao validada: Adicionar fallback deterministico para parse TOML no backend de roteamento e validar a suite em ambos os ambientes antes de fechar a rodada.
- Prevencao: Executar sempre task ai:validate, ai:eval:smoke, ci:workflow:sync:check e test:unit:python em Windows e Linux para qualquer novo CLI Python de governanca.
- Validacao: task ai:validate:windows; task ai:eval:smoke:windows; task test:unit:python:windows; task ai:validate:linux; task ai:eval:smoke:linux; task test:unit:python:linux
- Worklog relacionado: `WIP-20260307-GAP-IMPORTS`
- Fontes relacionadas: py-bootstrap, cr-automations, iageny

## LA-009 - Wrappers PowerShell devem blindar CLIs Python contra colisao de parametros comuns

- Contexto: A task ai:worklog:update:windows quebrava ao repassar --progress para ai-worklog.py via pwsh -File, porque o parser do PowerShell tentava tratar o argumento como common parameter.
- Regra: No Windows, tasks que chamam CLIs Python via PowerShell nao devem repassar flags sensiveis --* diretamente por pwsh -File quando houver risco de colisao com common parameters; usar wrapper .ps1 com nomes seguros ou forwarding explicito por array.
- Solucao validada: Criar [`scripts/run-ai-worklog-update.ps1`](scripts/run-ai-worklog-update.ps1) com parametros PowerShell seguros e repasse deterministico do array de argumentos para [`scripts/invoke-python.ps1`](scripts/invoke-python.ps1).
- Prevencao: Padronizar wrappers PowerShell finos para comandos de governanca que usem flags como --progress, --verbose, --debug ou outras suscetiveis a colisao no parser do shell.
- Validacao: task ai:worklog:update:windows; task ai:validate:windows; task test:unit:powershell
- Worklog relacionado: `WIP-20260307-084440`
- Fontes relacionadas: dotfiles-test-harness

## LA-010 - Rodadas concluídas exigem commit checkpoint antes do próximo escopo

- Contexto: O repo acumulou várias rodadas já concluídas sem commit intermediário, aumentando risco de drift, conflitos e dificuldade de revisão. O problema ficou claro quando a worktree estava limpa no tracker, mas ainda carregava muitas mudanças locais de contextos já encerrados.
- Regra: Se uma rodada terminou e a worktree continua dirty sem item ativo em Doing, a próxima rodada deve ser bloqueada até existir commit checkpoint do contexto anterior.
- Solucao validada: Endurecer o ai:worklog:check para inspecionar a worktree e falhar quando não houver Doing ativo e ainda existirem mudanças locais, além de refletir a regra em AGENTS, cartões e skill de continuidade.
- Prevencao: Usar task ai:worklog:check como preflight obrigatório de toda nova rodada e criar commit checkpoint imediatamente após o fechamento técnico de cada contexto coerente.
- Validacao: task ai:worklog:check:windows PENDING_ACTION=concluir_primeiro; python -m unittest tests.python.ai_worklog_test; task ai:validate:windows
- Worklog relacionado: `WIP-20260307-090534`
- Fontes relacionadas: dotfiles-test-harness

## LA-011 - Manter df estritamente como runtime materializado

- Contexto: A auditoria estrutural encontrou fixtures de editor e scripts scratch na antiga area PowerShell hoje arquivada em [`archive/df/powershell/tests/`](archive/df/powershell/tests/), embora [`df/`](df/) deva conter apenas artefatos que vao para a maquina apos o bootstrap.
- Regra: Tudo que nao for runtime real da workstation deve ficar fora de [`df/`](df/). Fixtures vao para [`tests/fixtures/`](tests/fixtures/), material historico vai para [`archive/`](archive/) e apenas dotfiles ativos permanecem em [`df/`](df/).
- Solucao validada: Mover o fixture de TODO para [`tests/fixtures/editor/`](tests/fixtures/editor/), arquivar o scratch PowerShell em [`archive/`](archive/) e deixar [`df/`](df/) livre de testes e experimentos.
- Prevencao: Em toda revisao estrutural, varrer df em busca de tests, scratch, backups, fixtures e nomes maquina-especificos antes de aceitar novos arquivos no runtime.
- Validacao: git ls-files df; task ai:validate:windows; task test:unit:powershell; git diff --check
- Worklog relacionado: `WIP-20260307-ESTRUTURA`

## LA-012 - Cada workflow deve chamar tasks canonicas, nao listas duplicadas de gates

- Contexto: A paridade entre CI/CD, Taskfile e documentacao ficou fragil quando workflows passaram a repetir listas de gates manualmente, em vez de apontar para uma task canonica por job.
- Regra: Todo workflow ou job recorrente deve ter uma task canonica correspondente no Taskfile; o workflow deve chamar essa task, e os catalogos devem documentar a mesma entrada canonica.
- Solucao validada: Criar `ci:ai:check:{windows,linux}`, `ci:quality:{windows,linux}` e `ci:bootstrap:integration:{windows,linux}`, depois atualizar workflows e docs para consumir essas entradas unicas.
- Prevencao: Sempre modelar primeiro a task canonica e so depois apontar workflow, docs e validadores para ela.
- Validacao: task ci:ai:check:windows; task ci:quality:windows; task ci:bootstrap:integration:windows; wsl task ci:ai:check:linux; wsl task ci:quality:linux; wsl task ci:bootstrap:integration:linux; task ci:workflow:sync:check:windows; task ci:workflow:sync:check:linux
- Worklog relacionado: `WIP-20260307-CI-TASK-PARITY`

## LA-013 - README raiz e docs centrais devem ser catalogos vivos do estado real do repo

- Contexto: O repo evoluiu em bootstrap, testes, CI/CD e camada de IA, mas parte da documentacao central ainda descrevia estados iniciais ou cobertura parcial, exigindo uma auditoria documental ampla.
- Regra: [`README.md`](README.md) deve funcionar como catalogo funcional do projeto, e docs centrais como [`docs/README.md`](docs/README.md), [`docs/TASKS.md`](docs/TASKS.md), [`docs/WORKFLOWS.md`](docs/WORKFLOWS.md), [`tests/README.md`](tests/README.md) e [`bootstrap/README.md`](bootstrap/README.md) devem refletir o estado real atual, nao snapshots antigos ou incompletos.
- Solucao validada: Auditar README, Taskfile, workflows, suites de teste, bootstrap e estrutura do repo em conjunto, depois reescrever os documentos centrais na mesma rodada para restaurar cobertura e coerencia.
- Prevencao: Sempre que a mudanca alterar capacidades do repo, automacao, testes, bootstrap ou governanca, atualizar na mesma rodada o README raiz e os catalogos centrais afetados antes de encerrar o trabalho.
- Validacao: task ai:validate:windows; task ci:workflow:sync:check:windows; task test:unit:python:windows; git diff --check
- Worklog relacionado: `WIP-20260307-DOCS-ATUALIZACAO`
- Fontes relacionadas: dotfiles-test-harness

## LA-014 - Worktree compartilhada entre Windows e WSL exige `.venv` por plataforma

- Contexto: Ao importar `uv` e a stack Python de qualidade, uma `.venv` unica na worktree passou a conflitar entre Windows host e WSL, contaminando binarios, shebangs e resolucao de executaveis.
- Regra: Neste repo, toda virtualenv compartilhada pela mesma worktree deve ser segregada por plataforma quando Windows e WSL operarem sobre a mesma arvore.
- Solucao validada: Padronizar `.venv/windows` e `.venv/linux`, expor isso no [`Taskfile.yml`](Taskfile.yml) via `UV_PROJECT_ENVIRONMENT` e ajustar os wrappers `invoke-python.ps1` e `python-runtime.sh`.
- Prevencao: Toda nova automacao Python ou task de ambiente deve assumir caminhos de venv por plataforma e nunca depender implicitamente de uma `.venv` unica na raiz.
- Validacao: task install:dev:windows; task install:dev:linux; task ci:quality:windows; wsl task ci:quality:linux
- Worklog relacionado: `WIP-20260307-QUALITY-IMPORTS`
- Fontes relacionadas: py-bootstrap, cr-automations, iageny

## LA-015 - Type checking em repo maduro deve entrar por fatias controladas

- Contexto: A importacao de `ty` sobre uma base de scripts historicos mostrou que tentar tipar tudo de uma vez gera muito ruido, retrabalho e risco de travar a rodada sem ganho proporcional.
- Regra: Em repos maduros e heterogeneos, type checking deve entrar por escopo pequeno, validado e com fronteira declarada, expandindo apenas depois que a base anterior estabilizar.
- Solucao validada: Aplicar `ty` primeiro na camada nova de qualidade importada (`release_tool`, `validate_docs`, wrappers e testes associados), mantendo o restante fora do gate ate haver refactor suficiente.
- Prevencao: Toda nova ampliacao do escopo de type checking deve ser explicitada em [`pyproject.toml`](pyproject.toml), [`Taskfile.yml`](Taskfile.yml) e nos catalogos de docs, em vez de crescer de forma acidental.
- Validacao: task type:check:windows; wsl task type:check:linux; task ci:quality:windows
- Worklog relacionado: `WIP-20260307-QUALITY-IMPORTS`
- Fontes relacionadas: py-bootstrap, cr-automations, iageny

## LA-016 - Citacoes internas viaveis em Markdown devem ser links, nao texto solto

- Contexto: O repo passou a citar muitos arquivos, pastas, tasks e workflows apenas em inline code, o que piora navegacao, revisao e auditoria documental.
- Regra: Em documentacao e comentarios com suporte a links clicaveis, toda citacao viavel a um alvo interno do repo deve usar link explicito para esse alvo.
- Solucao validada: Tornar o `Curador Repo` responsavel por essa higiene, endurecer `validate_docs.py` para cobrar referencias internas sem link nos Markdown governados e executar sweep dos docs ativos.
- Prevencao: Toda nova rodada que tocar docs, catalogos, agentes ou comentarios Markdown deve fechar com `task docs:check` e com referencias internas navegaveis.
- Validacao: task docs:check:windows; task docs:check:linux; task ai:validate:windows
- Worklog relacionado: `WIP-20260307-DOC-LINKING`
- Fontes relacionadas: dotfiles-test-harness

## LA-017 - Validadores de governanca devem comparar Markdown por semantica

- Contexto: O round de aprovacao em massa do roadmap expôs dois bugs: o backend de roadmap nao removia sugestoes aceitas quando o item tinha links Markdown e truncamento levemente diferente, e o validador de contratos quebrava ao exigir snippets literais em AGENTS.md com links e quebra de linha.
- Regra: Backends e validadores de governanca que leem Markdown do repo devem normalizar links, crases, wrapping e variantes truncadas antes de comparar itens ou contratos; substring literal nao e criterio suficiente de conformidade.
- Solucao validada: Adicionar normalizacao semantica no ai_roadmap_lib.py para casar itens equivalentes com links/truncamento e no validate-ai-assets.py para validar snippets por significado, nao por formato bruto.
- Prevencao: Toda nova automacao de governanca baseada em Markdown deve ter regressao cobrindo links clicaveis, bullets multiline e retries idempotentes antes de entrar no gate oficial.
- Validacao: uv run --locked python -m pytest [`tests/python/ai_roadmap_test.py`](tests/python/ai_roadmap_test.py) -q; task test:unit:python:windows; task ai:validate:windows; git diff --check
- Worklog relacionado: `WIP-20260307-ROADMAP-APPROVALS`
- Fontes relacionadas: dotfiles-test-harness

## LA-018 - Governanca de links documentais deve cobrir texto corrido, tabelas e refs locais nao versionadas

- Contexto: A regra de linkagem ja existia, mas o enforcement inicial so cobria inline code e links locais quebrados. Isso permitiu que README, catalogos e docs operacionais mantivessem paths do repo em texto corrido, referencias em tabelas Markdown, URLs externas sem link e menções a arquivos locais ignorados que deveriam apontar para destinos documentados como [docs/config-reference.md](docs/config-reference.md) e [docs/secrets-and-auth.md](docs/secrets-and-auth.md).
- Regra: O validador documental do repo deve inspecionar Markdown governado em texto corrido, tabelas e inline code, aceitar autolinks validos e exigir que referencias internas, referencias externas viaveis e refs locais do repo sem alvo versionado sejam reescritas para um destino clicavel/documentado.
- Solucao validada: Expandir validate_docs.py para detectar paths soltos, tabelas Markdown, URLs externas sem link e referencias repo-ish locais; ajustar os contratos do Curador Repo e varrer os docs governados convertendo tudo para links ou descricoes com alvo documentado.
- Prevencao: Toda mudanca em docs, catalogos, skills, cartoes ou guias operacionais deve fechar com docs:check e com o Curador Repo revisando se nao ficou path cru, glob cru ou URL solta no conjunto governado.
- Validacao: uv run --locked python -m pytest [tests/python/validate_docs_test.py](tests/python/validate_docs_test.py) -q; task docs:check:windows; task docs:lint:windows; task ai:validate:windows; task test:unit:python:windows; git diff --check
- Worklog relacionado: `WIP-20260307-DOC-LINKS-HARDENING`
- Fontes relacionadas: dotfiles-test-harness
<!-- ai-lessons:catalog:end -->

## Revisoes de rodadas

Toda finalizacao de worklog deve registrar se houve nova licao.

<!-- ai-lessons:reviews:start -->
| Data/Hora UTC | Worklog ID | Decisao | Resumo | Licoes | Evidencia |
| --- | --- | --- | --- | --- | --- |
| 2026-03-07 13:46 UTC | WIP-20260307-ROADMAP-EXTRA-APPROVALS | sem_nova_licao | A rodada apenas consolidou aprovacoes adicionais em itens que ja estavam mapeados como gaps reais; nao surgiu contrato novo nem correcao estrutural que justificasse nova licao perene. | - | task ai:roadmap:register:windows (3x); task docs:check:windows; task ai:validate:windows; uv run --locked python -m pytest tests/python/ai_roadmap_test.py -q; git diff --check |
| 2026-03-07 13:41 UTC | WIP-20260307-DOC-LINKS-HARDENING | capturada | A licao LA-018 formalizou que a governanca de links precisa cobrir texto corrido, tabelas e refs locais nao versionadas, com destino documentado quando o alvo real nao e versionado. | LA-018 | [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md), [`scripts/validate_docs.py`](scripts/validate_docs.py) e [`tests/python/validate_docs_test.py`](tests/python/validate_docs_test.py) |
| 2026-03-07 13:27 UTC | WIP-20260307-ROADMAP-APPROVALS | capturada | O incidente mostrou que governanca baseada em Markdown precisa comparar contratos e itens por semantica, nao por texto literal, para resistir a links, wrapping e truncamento. | LA-017 | [`scripts/ai_roadmap_lib.py`](scripts/ai_roadmap_lib.py), [`scripts/validate-ai-assets.py`](scripts/validate-ai-assets.py), [`tests/python/ai_roadmap_test.py`](tests/python/ai_roadmap_test.py) e [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md) |
| 2026-03-07 12:44 UTC | WIP-20260307-DOC-LINKING | capturada | A rodada consolidou que referencias internas viaveis em Markdown nao devem ficar soltas em inline code; elas precisam ser links explicitos e validados automaticamente. | LA-016 | [`AGENTS.md`](AGENTS.md), [`docs/ai-operating-model.md`](docs/ai-operating-model.md), [`.agents/cards/curador-repo.md`](.agents/cards/curador-repo.md), [`scripts/validate_docs.py`](scripts/validate_docs.py) e o sweep dos Markdown governados foram atualizados e validados em Windows e Linux. |
| 2026-03-07 11:46 UTC | WIP-20260307-QUALITY-IMPORTS | capturada | A rodada consolidou a necessidade de .venv por plataforma em worktree compartilhada Windows/WSL e de adotar type checking por fatias controladas em repo maduro. | LA-014, LA-015 | [`Taskfile.yml`](Taskfile.yml), [`scripts/invoke-python.ps1`](scripts/invoke-python.ps1), [`scripts/python-runtime.sh`](scripts/python-runtime.sh), [`pyproject.toml`](pyproject.toml) e gates ci:quality validos em Windows e Linux. |
| 2026-03-07 10:47 UTC | WIP-20260307-DOCS-ATUALIZACAO | capturada | A rodada consolidou a regra de que README raiz e docs centrais devem funcionar como catalogos vivos do estado real do repo, e nao como snapshots antigos ou parciais. | LA-013 | LICOES-APRENDIDAS.md atualizado com LA-013; docs centrais reescritos e validadores do repo passando |
| 2026-03-07 10:36 UTC | WIP-20260307-ALIASES-CANONICOS | sem_nova_licao | A rodada consolidou uma regra ja vigente do repo: loaders devem apenas carregar fontes canonicas. Nenhuma licao perene nova precisou ser adicionada. | - | bash -n em [`df/.aliases`](df/.aliases) e [`df/bash/.bashrc`](df/bash/.bashrc), carga real do [`df/powershell/aliases.ps1`](df/powershell/aliases.ps1) em pwsh e powershell, zsh -n no [`df/zsh/.zshrc`](df/zsh/.zshrc), source de [`df/.aliases`](df/.aliases) no WSL, parser de alias do Git em [`df/git/.gitconfig-base`](df/git/.gitconfig-base), ausencia de [alias] em... |
| 2026-03-07 10:18 UTC | WIP-20260307-CI-TASK-PARITY | capturada | A rodada consolidou a regra de que cada workflow/job recorrente deve chamar uma task canonica unica, em vez de duplicar listas de gates dentro do YAML. | LA-012 | LICOES-APRENDIDAS.md atualizado com LA-012; ci:workflow:sync:check passou em Windows e Linux |
| 2026-03-07 09:54 UTC | WIP-20260307-IA-REFERENCIAS | sem_nova_licao | A rodada gerou sugestoes de roadmap e referencia externa, mas nao introduziu regra operacional perene nova alem das governancas ja catalogadas. | - | task ai:validate:windows; git diff --check |
| 2026-03-07 09:43 UTC | WIP-20260307-ESTRUTURA | capturada | A rodada consolidou a regra de que [`df/`](df/) deve permanecer estritamente como runtime materializado; fixtures, scratch e historico devem sair para [`tests/fixtures/`](tests/fixtures/) ou [`archive/`](archive/). | LA-011 | [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md) atualizado com LA-011; fixture movido para [`tests/fixtures/editor/`](tests/fixtures/editor/); scratch PowerShell arquivado fora de [`df/`](df/). |
| 2026-03-07 09:28 UTC | WIP-20260307-090534 | sem_nova_licao | LA-010 ja cobre a regra normativa desta rodada; nao surgiu nova licao perene alem do enforcement e do checkpoint commit que ja foram registrados. | - | task test:unit:powershell; task test:integration:windows; wsl task test:integration:linux; task ai:validate:windows; git diff --check; commits a36c2ba,4610fdd,1c3902c,91bd551,49a5e64 |
| 2026-03-07 09:03 UTC | WIP-20260307-084440 | capturada | A rodada consolidou a necessidade de wrappers PowerShell dedicados para CLIs Python com flags sensiveis no Windows e reforcou a regra de manter .agents como fonte unica sem drift documental ou de workflow. | LA-009 | task ai:worklog:update:windows; task ai:validate:windows; task test:unit:powershell |
| 2026-03-07 08:43 UTC | WIP-20260307-083916 | sem_nova_licao | A rodada aplicou regras de governanca e higiene ja existentes; nao surgiu licao nova alem do endurecimento operacional corrente do repo. | - | git check-ignore -v -n [`.agents/skills/dotfiles-bootstrap/SKILL.md`](.agents/skills/dotfiles-bootstrap/SKILL.md) [`.agents/cards/bootstrap-operador.md`](.agents/cards/bootstrap-operador.md) [`.agents/config.toml`](.agents/config.toml) [`.codex/README.md`](.codex/README.md); git ls-files -ci --exclude-standard... |
| 2026-03-07 08:38 UTC | WIP-20260307-081800 | capturada | LA-002 foi endurecida para registrar que .agents e a fonte canonica da camada de IA e .codex no repo deve permanecer apenas como stub de compatibilidade. | LA-002 | LICOES-APRENDIDAS.md atualizado; AI assets OK; suite Python OK |
| 2026-03-07 08:15 UTC | WIP-20260307-GAP-IMPORTS | capturada | A rodada consolidou a licao de que toda nova automacao Python da camada de IA precisa ser portavel entre Windows e WSL, com fallback ou contrato explicito de runtime. | LA-008 | task ai:validate:windows; task ai:eval:smoke:linux |
| 2026-03-07 04:16 UTC | WIP-20260307-GOV-AGENTS | capturada | A rodada consolidou o fluxo formal de licoes por worklog, a importacao ampla da camada declarativa ausente e os gates permanentes de arquitetura/modernizacao e integracoes criticas. | LA-004, LA-005, LA-006, LA-007 | task ai:validate:windows; task ai:lessons:check:windows; task test:unit:python:windows; task ai:validate:linux; task test:unit:python:linux |
| 2026-03-07 04:05 UTC | WIP-20260306-ROADMAP-WIP | capturada | Backfill retroativo: esta rodada consolidou a licao de auditoria exaustiva antes de importacao cross-repo. | LA-001 | - |
| 2026-03-07 04:05 UTC | WIP-20260306-223413 | sem_nova_licao | Backfill retroativo: a fundacao inicial de IA ficou coberta pelas regras permanentes posteriores, sem nova licao isolada. | - | - |
| 2026-03-07 04:05 UTC | WIP-20260307-003625 | sem_nova_licao | Backfill retroativo: a rodada importou governanca de Git e WIP, mas as regras permanentes ja foram absorvidas no catalogo atual. | - | - |
| 2026-03-07 04:05 UTC | WIP-20260307-LIVE-DOING | capturada | Backfill retroativo: esta rodada consolidou a licao de manter Doing vivo ate o fechamento real. | LA-003 | - |
| 2026-03-07 04:05 UTC | WIP-20260307-ROADMAP-CYCLE-FIX | sem_nova_licao | Backfill retroativo: a correcao do ciclo duplicado virou regressao coberta por teste, sem demandar nova licao permanente. | - | - |
| 2026-03-07 04:05 UTC | WIP-20260307-BACKLOG-ADVANCE | sem_nova_licao | Backfill retroativo: a rodada consolidou backlog e harnesses sem introduzir licao nova alem das regras ja catalogadas. | - | - |
<!-- ai-lessons:reviews:end -->
