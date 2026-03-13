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

- Contexto: A auditoria estrutural encontrou fixtures de editor e scripts scratch na antiga area PowerShell hoje arquivada em [`archive/df/powershell/tests/`](archive/df/powershell/tests/), embora [`df/`](app/df/) deva conter apenas artefatos que vao para a maquina apos o bootstrap.
- Regra: Tudo que nao for runtime real da workstation deve ficar fora de [`df/`](app/df/). Fixtures vao para [`tests/fixtures/`](tests/fixtures/), material historico vai para [`archive/`](archive/) e apenas dotfiles ativos permanecem em [`df/`](app/df/).
- Solucao validada: Mover o fixture de TODO para [`tests/fixtures/editor/`](tests/fixtures/editor/), arquivar o scratch PowerShell em [`archive/`](archive/) e deixar [`df/`](app/df/) livre de testes e experimentos.
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
- Regra: [`README.md`](README.md) deve funcionar como catalogo funcional do projeto, e docs centrais como [`docs/README.md`](docs/README.md), [`docs/TASKS.md`](docs/TASKS.md), [`docs/WORKFLOWS.md`](docs/WORKFLOWS.md), [`tests/README.md`](tests/README.md) e [`bootstrap/README.md`](app/bootstrap/README.md) devem refletir o estado real atual, nao snapshots antigos ou incompletos.
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

## LA-019 - Signer tecnico deve ser worktree-scoped e orquestrado por CLIs criticos

- Contexto: Bloqueio recorrente de assinatura Git/1Password em rodadas locais de automacao exigia uma alternativa segura sem desligar o signer humano global.
- Regra: Automacao local nao pode burlar assinatura nem reaproveitar silenciosamente a identidade humana; deve usar signer tecnico dedicado por worktree, com chave publica resolvida por op, cadastro no GitHub via gh e chave privada mantida no 1Password SSH Agent.
- Solucao validada: Criar git-signing-mode.py e git_signing_lib.py, tasks git:signing:*, campo git.automation_signing_key_ref no bootstrap e checkEnv com modos human, auto e automation.
- Prevencao: Manter signer humano como padrao global, aplicar overrides somente via config.worktree e validar sempre com task git:signing:status e task env:check SIGN_MODE=automation antes de usar a worktree tecnica.
- Validacao: task git:signing:status:windows; task env:check:windows SIGN_MODE=human; task docs:check:windows; task docs:check:linux; task ai:validate:windows; task ai:validate:linux; task type:check:windows; task test:unit:python:windows; task test:unit:powershell; bash -n [`df/bash/.inc/check-env.sh`](app/df/bash/.inc/check-env.sh)
- Worklog relacionado: `WIP-20260307-GIT-AUTOMATION-SIGNING`
- Fontes relacionadas: dotfiles-test-harness

## LA-020 - Camadas documentais cross-surface exigem alinhamento do nucleo declarativo e das bordas Atlassian

- Contexto: A decomposicao da camada documental ficou correta no nucleo declarativo, mas o drift persistiu em jira-model, confluence-model e adaptadores Atlassian que ainda reintroduziam ownership legado e source of truth divergente.
- Regra: Sempre que uma mudanca alterar a governanca documental cross-surface, revisar em conjunto contracts, jira-model, confluence-model, routing e adaptadores Atlassian antes do fechamento.
- Solucao validada: A rodada DOT-181 so ficou coerente apos alinhar source of truth entre os modelos, trocar ai-documentation-agent por ai-documentation-sync nas bordas Atlassian e adicionar regressao dedicada para os pontos de drift.
- Prevencao: Tratar a camada documental como sistema cross-surface completo e incluir checks explicitos para source of truth, papeis de publication e roteamento em docs, validators e testes.
- Validacao: task ai:validate; task docs:check; task ai:eval:smoke; uv run --locked python -m unittest tests.python.ai_atlassian_seed_test tests.python.ai_atlassian_backfill_test tests.python.ai_assets_validator_test tests.python.ai_atlassian_agent_comment_audit_test tests.python.ai_sync_foundation_test
- Worklog relacionado: `WIP-20260312-033649`

## LA-021 - Alias-first exige migracao viva e auditoria de drift

- Contexto: A troca de schema para apelidos no Jira entrou, mas board e comentarios continuaram mostrando technical_id porque os dados vivos antigos nao foram migrados e o auditor ainda nao denunciava esse drift.
- Regra: Sempre que um papel ganhar apelido visivel ou mudar a representacao canonica, a rodada deve incluir escrita futura alias-first, backfill dos dados vivos e detector explicito de drift para comentarios, campos e artefatos gerados.
- Solucao validada: Endurecer o runtime de comentarios e logs para usar alias-first, aplicar backfill dos campos e comentarios vivos no Jira e ampliar a auditoria para marcar valores tecnicos remanescentes.
- Prevencao: Nao aceitar mudanca de schema isolada como suficiente; emparelhar qualquer migracao de naming com seed/backfill, repair ou auditor equivalente e com validacao final de drift zero.
- Validacao: python -m unittest tests.python.ai_control_plane_test tests.python.ai_agent_execution_test tests.python.ai_atlassian_backfill_test tests.python.ai_fallback_governance_test tests.python.ai_atlassian_agent_comment_audit_test; task test:unit:python; task ai:validate; task ai:eval:smoke; varredura Jira com field_drift_count=0 e comment_drift_count=0
- Worklog relacionado: `WIP-DOT-211`
- Fontes relacionadas: dotfiles

## LA-022 - Artefatos locais visiveis precisam separar alias e id tecnico

- Contexto: Mesmo apos corrigir board e comentarios, o `active-execution` e o startup ainda projetavam `ai-*` como valor principal, o que mantinha drift em logs locais e confundia ownership visivel da sessao.
- Regra: Todo artefato local visivel ao operador deve expor alias-first como superficie principal e guardar o identificador tecnico apenas em campos `*_id` ou equivalente explicitamente interno.
- Solucao validada: Reestruturar `.cache/ai/active-execution.json` para gravar `agent`, `current_agent_role` e `next_required_role` com apelidos, preservando `agent_id`, `current_agent_role_id` e `next_required_role_id`; alinhar o startup para consumir os ids dedicados e continuar mostrando o alias.
- Prevencao: Sempre que um runtime local ou report novo carregar ownership de agente, revisar se a superficie principal esta humana e se o id tecnico ficou restrito a campo canonico separado.
- Validacao: python -m unittest tests.python.ai_agent_execution_test tests.python.ai_session_startup_test; task test:unit:python; task ai:validate; task ai:eval:smoke; `python scripts/ai-agent-execution.py status --repo-root C:\\Users\\pablo\\dotfiles`
- Worklog relacionado: `WIP-DOT-211-RUNTIME-FINAL`
- Fontes relacionadas: dotfiles

## LA-023 - Separar runtime da app do desenvolvimento antes de centralizar configuracao

- Contexto: A raiz misturava bootstrap e df como runtime materializado com control plane, tooling e governanca de desenvolvimento; isso confundia IA, docs e consumidores antes mesmo da etapa de centralizacao ampla de configuracao.
- Regra: Quando o repo tiver camada runtime e camada de desenvolvimento distintas, a fronteira precisa aparecer explicitamente no layout top-level antes de qualquer consolidacao ampla de configuracao.
- Solucao validada: Mover bootstrap e df para [`app/`](app/), atualizar bootstrap, runtime, docs, Taskfile, scripts, tests e validadores na mesma onda, e manter [`pyproject.toml`](pyproject.toml) e [`config/`](config/) como donos do dev-time e do control plane.
- Prevencao: Antes de centralizar configuracao, auditar ownership runtime vs dev-time, preservar [`pyproject.toml`](pyproject.toml) como toolchain de desenvolvimento e impedir que [`config/`](config/) vire deposito de runtime da app.
- Validacao: task ai:validate; task docs:check; task ai:eval:smoke; task test:unit:powershell; task test:integration:windows; task test:integration:linux; task test:unit:python
- Worklog relacionado: `WIP-20260312-DOT-212`
- Fontes relacionadas: dotfiles

<!-- ai-lessons:catalog:end -->

## Revisoes de rodadas

Toda finalizacao de worklog deve registrar se houve nova licao.

<!-- ai-lessons:reviews:start -->
| Data/Hora UTC | Worklog ID | Decisao | Resumo | Licoes | Evidencia |
| --- | --- | --- | --- | --- | --- |
| 2026-03-13 04:44 UTC | WIP-DOT-216 | sem_nova_licao | A rodada confirmou e aplicou o contrato ja previsto: service accounts por agente com fallback global, retry de leitura e saneamento de state/drift; nao surgiu regra operacional nova alem do que ja foi materializado em... | - | DOT-216; PR #62; backfill Jira do PO zerado; startup actor state alinhado |
| 2026-03-13 01:49 UTC | WIP-DOT-214 | sem_nova_licao | A rodada apenas restaurou o contrato canonico de symlinks do bootstrap Windows e drenou dos artefatos vivos a regra incorreta de materializacao, sem introduzir nova licao perene alem dos guardrails ja vigentes. | - | sudo task bootstrap:windows:relink; task test:unit:powershell; task test:integration:windows; task docs:check; task ai:validate; task ai:lessons:check; task ai:eval:smoke; task env:check:windows; SYMLINK_AUDIT_OK count=25 |
| 2026-03-12 21:39 UTC | WIP-20260312-DOT-212 | capturada | A fronteira runtime vs desenvolvimento precisa ser resolvida antes de centralizar configuracao. | LA-023 | task ai:validate; task docs:check; task ai:eval:smoke; task test:unit:powershell; task test:integration:windows; task test:integration:linux; task test:unit:python |
| 2026-03-12 20:13 UTC | WIP-DOT-211-LEDGER-ALIAS | sem_nova_licao | LA-022 ja cobre a necessidade de alias-first nos artefatos locais visiveis; esta fatia apenas expandiu a aplicacao e drenou o historico local mais exposto. | - | worklog/review ledger alias-first; scrum master ledger e paused audit drenados nos campos visiveis |
| 2026-03-12 19:57 UTC | WIP-DOT-211-RUNTIME-FINAL | capturada | Alias-first precisa cobrir tambem artefatos locais visiveis, mantendo ids tecnicos apenas em campos canonicos separados. | LA-022 | active-execution alias-first regravado; startup passou a consumir agent_id/current_agent_role_id/next_required_role_id |
| 2026-03-12 19:37 UTC | WIP-DOT-211 | capturada | Schema alias-first so e valido com escrita futura, backfill vivo e auditoria de drift juntos. | LA-021 | Jira live backfill e auditoria final zerada |
| 2026-03-12 18:43 UTC | WIP-DOT-208 | sem_nova_licao | A rodada endureceu o runtime multiagente, a visibilidade alias-first e a conciliacao role x registry diretamente na governanca canonica, sem exigir nova licao perene alem da propria regra entregue. | - | python -m unittest tests.python.ai_control_plane_test tests.python.ai_session_startup_test tests.python.ai_assets_validator_test tests.python.ai_agent_execution_test tests.python.ai_atlassian_browser_auth_test tests.p... |
| 2026-03-12 17:41 UTC | WIP-DOT-207 | sem_nova_licao | A primeira onda hibrida .md + .rules foi absorvida diretamente na governanca canonica, no startup e no validator, sem exigir nova licao incremental alem da propria regra entregue. | - | PR #52=merged; [`docs/AI-STARTUP-AND-RESTART.md`](docs/AI-STARTUP-AND-RESTART.md); [`.agents/rules/projections.yaml`](.agents/rules/projections.yaml); [`scripts/ai_rules_lib.py`](scripts/ai_rules_lib.py); [`scripts/validate-ai-assets.py`](scripts/validate-ai-assets.py) |
| 2026-03-12 16:40 UTC | WIP-20260312-DOT-205-RERUN | sem_nova_licao | As regras e falhas desta trilha foram absorvidas diretamente na camada canonica [`.agents/rules/`](.agents/rules/README.md), no startup e no validator, sem gerar licao incremental adicional. | - | task ai:validate=ok; task docs:check=ok; task ai:eval:smoke=ok; task ci:workflow:sync:check=ok; task ai:startup:enforce PENDING_ACTION=concluir_primeiro=ok |
| 2026-03-12 15:09 UTC | WIP-20260312-120449 | sem_nova_licao | A rodada apenas concluiu a publicacao remota e o closeout operacional de DOT-206, sem nova licao perene alem do proprio fechamento canonico. | - | PR #49 mergeado; merge commit 8c75121 |
| 2026-03-12 14:55 UTC | WIP-20260312-142856 | sem_nova_licao | A rodada endureceu estruturalmente o startup com Guardiao de Startup, readiness artifact e enforcement do first-response gate, sem revelar licao perene adicional alem do proprio incremento entregue. | - | - |
| 2026-03-12 14:16 UTC | WIP-20260312-141233 | sem_nova_licao | A rodada formalizou um novo pack de execucao para endurecer o startup, sem revelar licao perene nova alem do proprio artefato entregue. | - | - |
| 2026-03-12 13:47 UTC | WIP-20260312-DOT-205 | sem_nova_licao | Prompt pack formal salvo no padrao canonico, com task Jira dona e backlog consultivo de ortografia rastreado. | - | commit ffda714; task docs:check; task ai:validate; task ai:prompts:jira:check; task ai:eval:smoke; task spell:dictionary:audit; SG-ORTHO-WIP-20260312-DOT-205 |
| 2026-03-12 05:05 UTC | WIP-20260312-033649 | capturada | A rodada consolidou LA-020 sobre alinhamento cross-surface da camada documental entre modelos, adaptadores e publication. | LA-020 | LICOES-APRENDIDAS.md; task ai:lessons:check=ok |
| 2026-03-12 01:45 UTC | WIP-20260312-014434 | sem_nova_licao | A rodada apenas publicou o commit ja validado de DOT-180 em main, sem nova licao perene alem do proprio fechamento operacional. | - | commit=9b03ac6; origin/main atualizado |
| 2026-03-12 01:30 UTC | WIP-20260312-011221 | sem_nova_licao | A rodada apenas formalizou e catalogou o novo pack temporal, sem revelar licao perene adicional alem do proprio artefato entregue. | - | DOT-180; task ai:prompts:jira:check=ok; task docs:check=ok; task ai:validate=ok |
| 2026-03-11 23:45 UTC | WIP-20260311-204022 | sem_nova_licao | A rodada foi uma cirurgia controlada de publicacao e sincronismo Git para adequar commits e branches aos hooks existentes; nao surgiu licao perene nova alem das regras ja formalizadas de governanca Git e prompts. | - | PR #45 mergeado; branch DOT-179 reconstruida a partir de origin/main; cherry-pick do diff da fundacao de sync refeito com subject prompt; task ai:worklog:check; task ai:lessons:check; task ai:worklog:close:gate |
| 2026-03-11 23:08 UTC | WIP-20260311-220259 | sem_nova_licao | A rodada materializou a fundacao de sync como artefato principal e codificou suas fronteiras diretamente em contracts, docs, tasks e testes, sem exigir licao perene adicional. | - | python [`scripts/validate-ai-assets.py`](scripts/validate-ai-assets.py); python -m pytest --override-ini addopts='' [`tests/python/ai_sync_foundation_test.py`](tests/python/ai_sync_foundation_test.py) [`tests/python/ai_assets_validator_test.py`](tests/python/ai_assets_validator_test.py) [`tests/python/ai_control_plane_test.py`](tests/python/ai_control_plane_test.py); uv run --locked... |
| 2026-03-11 22:00 UTC | WIP-20260311-212032 | sem_nova_licao | A rodada consolidou e salvou os packs formais como artefato principal; nao surgiu licao perene nova alem da propria estrutura entregue. | - | - |
| 2026-03-11 19:45 UTC | WIP-20260311-183919 | sem_nova_licao | A rodada endureceu e automatizou contratos permanentes do namespace prompt, sem revelar licao perene nova alem do proprio artefato entregue. | - | commit=ab59d7f; commit=24c5f44; pr=[#44](https://github.com/pabloaugusto/dotfiles/pull/44); task ai:validate=ok; task ci:workflow:sync:check=ok; task ai:prompts:jira:check=ok; targeted unittest=ok |
| 2026-03-11 15:56 UTC | WIP-DOT-178 | sem_nova_licao | A rodada promoveu os contratos diretamente para docs, startup e validadores; nao houve licao adicional alem do proprio artefato entregue. | - | PR #41 mergeado em main; task ai:startup:session com pea_status=ok |
| 2026-03-11 14:40 UTC | WIP-DOT-177 | sem_nova_licao | Sem nova licao perene nesta fatia; a distincao startup-versus-enforcement ficou absorvida nos contratos entregues pela propria DOT-177. | - | - |
| 2026-03-11 13:18 UTC | WIP-DOT-175-CLOSEOUT | sem_nova_licao | Sem nova licao nesta fatia; o gap de memoria operacional do fallback GitHub sera tratado em work item proprio sob DOT-71. | - | PR=[#38](https://github.com/pabloaugusto/dotfiles/pull/38); commit=3bef3e0; python -m unittest tests.python.ai_assets_validator_test=ok; task ai:validate=ok; task docs:check=ok; task ai:eval:smoke=ok; task type:check=ok; tas... |
| 2026-03-11 12:38 UTC | WIP-DOT-175 | sem_nova_licao | Sem nova licao; a rodada formalizou um contrato novo e deixou a pendencia ortografica consultiva rastreada. | - | task ai:validate=ok; task docs:check=ok; task ai:eval:smoke=ok; task type:check=ok; python -m unittest tests.python.ai_assets_validator_test=ok; task spell:review=reprovado_consultivo_com_backlog_SG-ORTHO-WIP-DOT-175 |
| 2026-03-11 12:06 UTC | WIP-DOT-37 | sem_nova_licao | A rodada apenas materializou o fechamento formal de DOT-37 usando contratos, gates e auditorias ja existentes, sem revelar nova licao perene. | - | [`docs/AI-PAUSED-ISSUES-AUDIT.md`](docs/AI-PAUSED-ISSUES-AUDIT.md); Jira comments 10939-10942; task docs:check=ok; task ai:validate=ok; task ai:eval:smoke=ok; task spell:review=ok |
| 2026-03-11 09:17 UTC | WIP-DOT-106 | sem_nova_licao | DOT-106 consolidou um protocolo perene de fallback contingencial e apenas endureceu contratos, docs, Taskfile e gates que ja estavam alinhados com as licoes vigentes sobre paridade doc-task-validacao e higiene worktre... | - | [`docs/AI-FALLBACK-OPERATIONS.md`](docs/AI-FALLBACK-OPERATIONS.md); [`docs/AI-FALLBACK-LEDGER.md`](docs/AI-FALLBACK-LEDGER.md); task ai:validate=ok; task ai:eval:smoke=ok; task docs:check=ok; task type:check=ok |
| 2026-03-11 07:54 UTC | WIP-DOT-109-RETRO | sem_nova_licao | A retrospectiva apenas fechou a cadeia cerimonial ja contratada para DOT-109 e deixou o residual ortografico consultivo rastreado em backlog proprio. | - | Confluence: [Retrospectiva - 2026-03-11 04:45](https://pabloaugusto.atlassian.net/wiki/spaces/DOT/pages/256737308); PR alvo: [#34](https://github.com/pabloaugusto/dotfiles/pull/34); orthography backlog: SG-ORTHO-WIP-DOT-109-RETRO |
| 2026-03-11 07:30 UTC | WIP-DOT-109 | sem_nova_licao | A rodada exigiu revisao explicita de licoes, mas as correcoes ficaram contidas no proprio backend/versionamento desta trilha sem demandar novo contrato operacional perene alem dos ja existentes. | - | DOT-109 em Done no Jira; comments 10896,10897,10898,10899,10900; jira apply CLI=ok; jira live-delta CLI=sem gaps ativos; task ai:validate=ok; task ai:eval:smoke=ok; task docs:check=ok; task ai:review:check:windows WOR... |
| 2026-03-11 06:08 UTC | WIP-DOT-134 | sem_nova_licao | DOT-134 consolidou a baseline auditavel das issues Done e saneou apenas drift terminal de comentarios, sem criar novo contrato perene alem dos ja vigentes. | - | [`docs/AI-DONE-ISSUES-AUDIT.md`](docs/AI-DONE-ISSUES-AUDIT.md); [`docs/README.md`](docs/README.md); task docs:check=ok; task ai:validate=ok; task ai:eval:smoke=ok; task spell:review=consultivo_reprovado(SG-ORTHO-WIP-DOT-134) |
| 2026-03-11 05:35 UTC | WIP-DOT-135 | sem_nova_licao | DOT-135 ampliou a cobertura historica de retrospectivas usando contratos e gates ja vigentes, sem criar regra perene nova alem das ja formalizadas em DOT-121, DOT-124 e DOT-131. | - | [`docs/AI-RETROSPECTIVE-BACKFILL-AUDIT.md`](docs/AI-RETROSPECTIVE-BACKFILL-AUDIT.md); [`docs/AI-SCRUM-MASTER-LEDGER.md`](docs/AI-SCRUM-MASTER-LEDGER.md); task docs:check=ok; task ai:validate=ok |
| 2026-03-11 04:27 UTC | WIP-DOT-132 | sem_nova_licao | DOT-132 consolidou uma auditoria factual de pausadas e correcao de fluxo no board, sem criar novo contrato perene alem dos ja vigentes. | - | [`docs/AI-PAUSED-ISSUES-AUDIT.md`](docs/AI-PAUSED-ISSUES-AUDIT.md); [`docs/README.md`](docs/README.md); task docs:check; Jira: DOT-1=Done, DOT-37=PAUSED, DOT-126=PAUSED |
| 2026-03-11 01:46 UTC | WIP-DOT-133 | sem_nova_licao | sem_nova_licao | - | PR #29; commit 88c0f71; merge 9150608; [`docs/AI-BACKLOG-LIVE-AUDIT.md`](docs/AI-BACKLOG-LIVE-AUDIT.md); task docs:check; task ai:validate; task ai:review:check; git diff --check |
| 2026-03-11 00:57 UTC | WIP-DOT-131 | sem_nova_licao | A rodada nao gerou nova licao perene alem das lacunas ja rastreadas em backlog e no ledger do Scrum Master. | - | PR #28; pagina de Confluence da Retrospectiva; DOT-135 criado; task docs:check=ok; task ai:validate=ok; task ai:eval:smoke=ok; task ai:review:check=ok |
| 2026-03-10 23:58 UTC | WIP-20260307-SECRETS-ROTATION | sem_nova_licao | Backfill de governanca do fallback local apos migracao do fluxo vivo para o Jira; sem nova licao especifica alem do proprio alinhamento ja registrado. | - | Alinhamento fallback-jira registrado em [`docs/AI-WIP-TRACKER.md`](docs/AI-WIP-TRACKER.md) em 2026-03-10 |
| 2026-03-10 23:58 UTC | WIP-20260307-ATLASSIAN-ADAPTERS | sem_nova_licao | Backfill de governanca do fallback local apos migracao do fluxo vivo para o Jira; sem nova licao especifica alem do proprio alinhamento ja registrado. | - | Alinhamento fallback-jira registrado em [`docs/AI-WIP-TRACKER.md`](docs/AI-WIP-TRACKER.md) em 2026-03-10 |
| 2026-03-10 23:57 UTC | WIP-DOT-130 | sem_nova_licao | DOT-130 endureceu contratos e validadores ja previstos sem revelar licao nova alem do proprio incremento entregue. | - | task ai:startup:session=ok; task ai:worklog:check PENDING_ACTION=concluir_primeiro=ok; task ai:validate=ok; task ai:eval:smoke=ok; task docs:check=ok; python -m unittest tests.python.conventional_emoji_test tests.pyth... |
| 2026-03-07 18:20 UTC | WIP-20260307-ATLASSIAN-IA-CONTEXT | sem_nova_licao | A rodada consolidou rastreabilidade documental do estudo Atlassian + IA e adicionou o insight de Figma/UX/SEO ao plano, mas nao criou novo contrato perene alem das regras ja vigentes do repo. | - | task docs:check; task ai:validate; task ai:eval:smoke; task spell:dictionary:audit; task spell:review (consultivo, backlog SG-ORTHO-WIP-20260307-ATLASSIAN-IA-CONTEXT); [`docs/atlassian-ia/README.md`](docs/atlassian-ia/README.md) |
| 2026-03-07 18:03 UTC | WIP-20260307-JIRA-CONFLUENCE-IA | sem_nova_licao | A rodada produziu parecer e plano arquitetural, mas nao introduziu regra operacional perene nova alem dos contratos ja vigentes do repo. | - | Leitura integral de [`.agents/`](.agents/), [`docs/`](docs/), workflows e scripts `ai-*`; confronto com blueprint do usuario e com documentacao oficial Atlassian sobre Jira REST, Confluence REST, Jira Automation, Rovo MCP e Forge MCP. |
| 2026-03-07 14:18 UTC | WIP-20260307-GIT-AUTOMATION-SIGNING | capturada | A rodada consolidou que worktrees de automacao devem usar signer tecnico dedicado e worktree-scoped, orquestrado por op + gh + 1Password SSH Agent, sem bypass da identidade humana global. | LA-019 | [`scripts/git-signing-mode.py`](scripts/git-signing-mode.py); [`scripts/git_signing_lib.py`](scripts/git_signing_lib.py); [`df/powershell/_functions.ps1`](app/df/powershell/_functions.ps1); [`df/bash/.inc/check-env.sh`](app/df/bash/.inc/check-env.sh); [`Taskfile.yml`](Taskfile.yml); [`docs/checkenv.md`](docs/checkenv.md); [`docs/secrets-and-auth.md`](docs/secrets-and-auth.md) |
| 2026-03-07 14:17 UTC | WIP-20260307-VSCODE-WORKSPACE | sem_nova_licao | A rodada nao concluiu implementacao tecnica; apenas converteu o escopo para pendencia formal de roadmap, sem novo contrato perene. | - | [`ROADMAP.md`](ROADMAP.md); [`docs/ROADMAP-DECISIONS.md`](docs/ROADMAP-DECISIONS.md); [`docs/AI-WIP-TRACKER.md`](docs/AI-WIP-TRACKER.md) |
| 2026-03-07 13:46 UTC | WIP-20260307-ROADMAP-EXTRA-APPROVALS | sem_nova_licao | A rodada apenas consolidou aprovacoes adicionais em itens que ja estavam mapeados como gaps reais; nao surgiu contrato novo nem correcao estrutural que justificasse nova licao perene. | - | task ai:roadmap:register:windows (3x); task docs:check:windows; task ai:validate:windows; uv run --locked python -m pytest [`tests/python/ai_roadmap_test.py`](tests/python/ai_roadmap_test.py) -q; git diff --check |
| 2026-03-07 13:41 UTC | WIP-20260307-DOC-LINKS-HARDENING | capturada | A licao LA-018 formalizou que a governanca de links precisa cobrir texto corrido, tabelas e refs locais nao versionadas, com destino documentado quando o alvo real nao e versionado. | LA-018 | [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md), [`scripts/validate_docs.py`](scripts/validate_docs.py) e [`tests/python/validate_docs_test.py`](tests/python/validate_docs_test.py) |
| 2026-03-07 13:27 UTC | WIP-20260307-ROADMAP-APPROVALS | capturada | O incidente mostrou que governanca baseada em Markdown precisa comparar contratos e itens por semantica, nao por texto literal, para resistir a links, wrapping e truncamento. | LA-017 | [`scripts/ai_roadmap_lib.py`](scripts/ai_roadmap_lib.py), [`scripts/validate-ai-assets.py`](scripts/validate-ai-assets.py), [`tests/python/ai_roadmap_test.py`](tests/python/ai_roadmap_test.py) e [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md) |
| 2026-03-07 12:44 UTC | WIP-20260307-DOC-LINKING | capturada | A rodada consolidou que referencias internas viaveis em Markdown nao devem ficar soltas em inline code; elas precisam ser links explicitos e validados automaticamente. | LA-016 | [`AGENTS.md`](AGENTS.md), [`docs/ai-operating-model.md`](docs/ai-operating-model.md), [`.agents/cards/curador-repo.md`](.agents/cards/curador-repo.md), [`scripts/validate_docs.py`](scripts/validate_docs.py) e o sweep dos Markdown governados foram atualizados e validados em Windows e Linux. |
| 2026-03-07 11:46 UTC | WIP-20260307-QUALITY-IMPORTS | capturada | A rodada consolidou a necessidade de .venv por plataforma em worktree compartilhada Windows/WSL e de adotar type checking por fatias controladas em repo maduro. | LA-014, LA-015 | [`Taskfile.yml`](Taskfile.yml), [`scripts/invoke-python.ps1`](scripts/invoke-python.ps1), [`scripts/python-runtime.sh`](scripts/python-runtime.sh), [`pyproject.toml`](pyproject.toml) e gates ci:quality validos em Windows e Linux. |
| 2026-03-07 10:47 UTC | WIP-20260307-DOCS-ATUALIZACAO | capturada | A rodada consolidou a regra de que README raiz e docs centrais devem funcionar como catalogos vivos do estado real do repo, e nao como snapshots antigos ou parciais. | LA-013 | LICOES-APRENDIDAS.md atualizado com LA-013; docs centrais reescritos e validadores do repo passando |
| 2026-03-07 10:36 UTC | WIP-20260307-ALIASES-CANONICOS | sem_nova_licao | A rodada consolidou uma regra ja vigente do repo: loaders devem apenas carregar fontes canonicas. Nenhuma licao perene nova precisou ser adicionada. | - | bash -n em [`df/.aliases`](app/df/.aliases) e [`df/bash/.bashrc`](app/df/bash/.bashrc), carga real do [`df/powershell/aliases.ps1`](app/df/powershell/aliases.ps1) em pwsh e powershell, zsh -n no [`df/zsh/.zshrc`](app/df/zsh/.zshrc), source de [`df/.aliases`](app/df/.aliases) no WSL, parser de alias do Git em [`df/git/.gitconfig-base`](app/df/git/.gitconfig-base), ausencia de [alias] em... |
| 2026-03-07 10:18 UTC | WIP-20260307-CI-TASK-PARITY | capturada | A rodada consolidou a regra de que cada workflow/job recorrente deve chamar uma task canonica unica, em vez de duplicar listas de gates dentro do YAML. | LA-012 | LICOES-APRENDIDAS.md atualizado com LA-012; ci:workflow:sync:check passou em Windows e Linux |
| 2026-03-07 09:54 UTC | WIP-20260307-IA-REFERENCIAS | sem_nova_licao | A rodada gerou sugestoes de roadmap e referencia externa, mas nao introduziu regra operacional perene nova alem das governancas ja catalogadas. | - | task ai:validate:windows; git diff --check |
| 2026-03-07 09:43 UTC | WIP-20260307-ESTRUTURA | capturada | A rodada consolidou a regra de que [`df/`](app/df/) deve permanecer estritamente como runtime materializado; fixtures, scratch e historico devem sair para [`tests/fixtures/`](tests/fixtures/) ou [`archive/`](archive/). | LA-011 | [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md) atualizado com LA-011; fixture movido para [`tests/fixtures/editor/`](tests/fixtures/editor/); scratch PowerShell arquivado fora de [`df/`](app/df/). |
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
| 2026-03-13 02:06 UTC | WIP-DOT-215 | sem_nova_licao | A rodada corrigiu um residual da DOT-212 restaurando apenas o ponteiro canonico do runtime PowerShell via [`app/df/`](app/df/), sem introduzir regra nova alem do contrato ja vigente de symlinks. | - | task test:unit:powershell; task test:integration:windows; task env:check:windows (success=31 fail=1; residual fora do escopo em op://Personal/github/token-full-access); SYMLINK_AUDIT_OK count=25 expected=25 |
<!-- ai-lessons:reviews:end -->
