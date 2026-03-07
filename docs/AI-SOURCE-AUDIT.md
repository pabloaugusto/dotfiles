# AI Source Audit

Inventario versionado da auditoria estrutural usada para importar ou adaptar governanca, agentes, skills, workflows e contratos de IA neste repo.

## Escopo da auditoria

Esta auditoria cobre, para cada repo-fonte:

- contratos globais
- docs e catalogos
- tasks, taskfiles e aliases
- scripts e CLIs
- workflows, hooks e gates
- validadores e testes
- agentes, skills e metadata
- orquestracao, rules e evals
- relacoes entre worklog, roadmap, CI e governanca

## Repositorios auditados

### py-bootstrap

- caminho auditado: `\\wsl.localhost\Ubuntu\home\pablo\py-bootstrap`
- contrato global: [`AGENTS.md`](AGENTS.md), [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md)
- camada declarativa IA: [`.agents/registry`](.agents/registry), [`.agents/skills`](.agents/skills), [`.agents/orchestration`](.agents/orchestration), [`.agents/rules`](.agents/rules), [`.agents/evals`](.agents/evals), [`.agents/config.toml`](.agents/config.toml)
- docs centrais: [`docs/AI-WIP-TRACKER.md`](docs/AI-WIP-TRACKER.md), [`docs/ROADMAP.md`](docs/ROADMAP.md), [`docs/ROADMAP-DECISIONS.md`](docs/ROADMAP-DECISIONS.md), [`docs/AI-AGENTS-CATALOG.md`](docs/AI-AGENTS-CATALOG.md), [`docs/AI-DELEGATION-FLOW.md`](docs/AI-DELEGATION-FLOW.md), [`docs/AI-GOVERNANCE-AND-REGRESSION.md`](docs/AI-GOVERNANCE-AND-REGRESSION.md), `docs/AI-IMPLEMENTATION-PLAN.md`, [`docs/ai-operating-model.md`](docs/ai-operating-model.md), [`docs/AI-SKILLS-CATALOG.md`](docs/AI-SKILLS-CATALOG.md), [`docs/TASKS.md`](docs/TASKS.md), [`docs/WORKFLOWS.md`](docs/WORKFLOWS.md)
- automacao: `.taskfiles/ai.yaml`, `.taskfiles/roadmap.yaml`, `.taskfiles/scripts/*`
- testes/gates: `tests/governance/test_ai_worklog_governance.py`

### cr-automations

- caminho auditado: `\\wsl.localhost\Ubuntu\home\pablo\cr-automations`
- contrato global: [`AGENTS.md`](AGENTS.md), [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md)
- camada declarativa IA: [`.agents/registry`](.agents/registry), [`.agents/skills`](.agents/skills), [`.agents/orchestration`](.agents/orchestration), [`.agents/rules`](.agents/rules), [`.agents/evals`](.agents/evals), [`.agents/config.toml`](.agents/config.toml)
- docs centrais: [`docs/AI-WIP-TRACKER.md`](docs/AI-WIP-TRACKER.md), [`docs/ROADMAP.md`](docs/ROADMAP.md), [`docs/ROADMAP-DECISIONS.md`](docs/ROADMAP-DECISIONS.md), [`docs/TASKS.md`](docs/TASKS.md), [`docs/WORKFLOWS.md`](docs/WORKFLOWS.md)
- automacao: `.taskfiles/ai.yaml`, `.taskfiles/scripts/ai-wip-tracker.py`, `.taskfiles/scripts/ai-roadmap-refresh.sh`, `.taskfiles/scripts/ai-roadmap-register.sh`, `.taskfiles/scripts/ai-wip-roadmap-pending.sh`
- testes/gates: `tests/governance/test_ai_wip_governance.py`

### iageny

- caminho auditado: `D:\projects\iageny`
- contrato principal: docs estruturais + camada [`.agents/`](.agents/)
- camada declarativa IA: `.agents/implementation-agents`, `.agents/implementation-subagents`, [`.agents/skills`](.agents/skills), `.agents/workflows`
- docs centrais: [`docs/AI-WIP-TRACKER.md`](docs/AI-WIP-TRACKER.md), [`docs/ROADMAP.md`](docs/ROADMAP.md), [`docs/ROADMAP-DECISIONS.md`](docs/ROADMAP-DECISIONS.md), `docs/agent-catalog.md`, `docs/implementation-agents.md`, `docs/phase-guide.md`, `docs/reference-catalog.md`, `docs/decisions.md`, `docs/lessons-learned.md`, `docs/time-and-locale.md`
- automacao: [`Taskfile.yml`](Taskfile.yml), `scripts/ai_worklog.py`, `scripts/roadmap_register.py`, `scripts/validate_repo.py`, [`scripts/validate_docs.py`](scripts/validate_docs.py), `scripts/validate_implementation_agents.py`, [`scripts/validate_workflow_task_sync.py`](scripts/validate_workflow_task_sync.py), `scripts/validate_workflows.py`
- testes/gates: `tests/test_ai_worklog.py`, `tests/test_roadmap_register.py`, `tests/test_validate_repo.py`, `tests/test_validate_docs.py`, `tests/test_validate_workflow_task_sync.py`, `tests/test_validate_workflows.py`

## Inventario consolidado por dominio

### Contratos globais

Padrao comum validado nas fontes:

- [`AGENTS.md`](AGENTS.md) como contrato operacional global em `py-bootstrap` e `cr-automations`
- [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md) como camada incremental de memoria normativa
- docs especificos para operating model, catalogos, delegation flow e governanca/regression

Contribuicao util de `iageny`:

- ausencia de [`AGENTS.md`](AGENTS.md), mas forte centralizacao declarativa em [`.agents/`](.agents/) e em docs estruturais versionados
- contrato mais explicito de timezone/locale, retroatividade de worklog e correlacao entre WIP e roadmap

### Camada declarativa de IA

Padrao comum em `py-bootstrap` e `cr-automations`:

- [`.agents/config.toml`](.agents/config.toml)
- `.agents/registry/*.toml`
- [`.agents/orchestration/capability-matrix.yaml`](.agents/orchestration/capability-matrix.yaml)
- [`.agents/orchestration/routing-policy.yaml`](.agents/orchestration/routing-policy.yaml)
- `.agents/orchestration/*.schema.json`
- `.agents/rules/*.rules`
- `.agents/evals/*`
- `.agents/skills/*`

Contribuicao util de `iageny`:

- [`.agents/`](.agents/) como camada declarativa primaria para implementation agents, subagents, skills e workflows
- validadores dedicados para provar estrutura e sincronismo entre docs, schemas e workflows

### Worklog e roadmap

Padrao comum:

- tracker com `Doing`, `Done` e log incremental
- gate obrigatorio de fechamento
- decisao humana obrigatoria entre `concluir_primeiro` e `roadmap_pendente`
- rastreabilidade de sugestoes em `ROADMAP-DECISIONS`

Contribuicao util de `py-bootstrap` e `cr-automations`:

- aliases e taskfiles maduros para `ai:worklog:*`
- sincronismo com roadmap em runtime e CI

Contribuicao util de `iageny`:

- [`ROADMAP.md`](ROADMAP.md) como contraparte explicita do tracker
- registro de decisoes com `related WIP`
- contrato de timezone/locale e retroatividade de registros

### Validacao e testes

Padrao comum:

- validadores dedicados para camada de IA/governanca
- testes de regressao para worklog e roadmap
- workflows de CI que rodam esses gates

Contribuicao util de `iageny`:

- `scripts/validate_repo.py` com inventario declarativo do repo
- testes para os validadores em si, nao apenas para as features de runtime

### Toolchain Python, lint e validacao transversal

Padrao comum em `py-bootstrap` e `cr-automations`:

- [`pyproject.toml`](pyproject.toml), [`uv.lock`](uv.lock) e [`.python-version`](.python-version)
- `ruff`
- `pytest`, `pytest-cov` e suporte a execucao paralela
- `ty`
- `pymarkdownlnt`
- tasks de `cspell`

Contribuicao util de `iageny`:

- [`.yamllint.yml`](.yamllint.yml)
- `.pre-commit-config.yaml`
- `mypy`
- wrappers e pinagem declarativa para `actionlint` e `gitleaks`
- [`scripts/validate_docs.py`](scripts/validate_docs.py)
- gates de qualidade maduros no [`Taskfile.yml`](Taskfile.yml)

## Gaps no repo atual

No inicio desta rodada, os gaps materiais eram:

- faltava [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md)
- faltava auditoria versionada das fontes em [`docs/AI-SOURCE-AUDIT.md`](docs/AI-SOURCE-AUDIT.md)
- a regra de auditoria exaustiva ainda nao estava endurecida em contratos e validadores
- havia `AI-WIP-TRACKER` e `ROADMAP-DECISIONS`, mas a camada de [`ROADMAP.md`](ROADMAP.md) ainda estava incompleta
- [`.agents/`](.agents/) e a antiga camada [`.codex/`](.codex/) ainda nao tinham fronteira contratual suficientemente explicita nem gate para drift conceitual
- o repo ainda nao tinha paridade com as fontes em [`.agents/config.toml`](.agents/config.toml), [`.agents/registry`](.agents/registry), [`.agents/orchestration`](.agents/orchestration), [`.agents/rules`](.agents/rules) e [`.agents/evals`](.agents/evals)
- a validacao local de IA ainda era superficial comparada a `iageny`

Estado apos esta rodada de importacao:

- [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md) passou a ter catalogo e revisoes formais por worklog
- o repo agora versiona [`.agents/config.toml`](.agents/config.toml), [`.agents/registry`](.agents/registry), [`.agents/orchestration`](.agents/orchestration), [`.agents/rules`](.agents/rules) e [`.agents/evals`](.agents/evals)
- foram adicionados catalogos humanos de agentes, skills, delegacao e governanca/regression
- o fluxo de fechamento ganhou gate formal de lessons integrado ao worklog
- os papeis permanentes de arquitetura/modernizacao e integracoes criticas passaram a ser gates explicitamente versionados
- `chat-intake`, `route` e `delegate` agora tem backend Python real baseado em `.agents/orchestration/*`
- `orchestrator` e `$task-routing-and-decomposition` foram importados e adaptados para intake/delegacao
- [`docs/TASKS.md`](docs/TASKS.md) e [`docs/WORKFLOWS.md`](docs/WORKFLOWS.md) passaram a existir com gate executavel de sincronismo
- `ai:eval:smoke` passou a executar datasets reais de roteamento e governanca
- a camada Python do repo passou a ter [`pyproject.toml`](pyproject.toml), [`uv.lock`](uv.lock),
  [`.python-version`](.python-version) e `.venv` segregada por plataforma
- `quality-foundation` passou a cobrir `ruff`, `ty`, `pytest`,
  `pymarkdownlnt`, `yamllint`, `actionlint` e `gitleaks`
- `validate_docs.py`, `run_actionlint.py`, `run_gitleaks.py` e
  [`config/tooling.releases.yaml`](config/tooling.releases.yaml) foram importados e adaptados ao repo

## Decisoes de importacao

### Adotar agora

- contrato permanente de auditoria exaustiva cross-repo
- [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md) como memoria normativa incremental
- fluxo formal de revisao de licoes por worklog
- auditoria versionada em [`docs/AI-SOURCE-AUDIT.md`](docs/AI-SOURCE-AUDIT.md)
- consolidacao de [`.agents/`](.agents/) como fonte canonica e reducao de [`.codex/`](.codex/) a ponte legada
- [`.agents/config.toml`](.agents/config.toml)
- `.agents/registry/*.toml`
- `.agents/orchestration/*`
- `.agents/rules/*`
- `.agents/evals/*`
- catalogos e docs de delegacao/governanca aplicaveis
- gates permanentes de arquitetura/modernizacao e integracoes criticas
- endurecimento dos validadores para cobrar esses artefatos

### Adaptar agora

- fluxo de roadmap e worklog inspirado em `py-bootstrap`, `cr-automations` e `iageny`, mas preservando a estrutura task-first deste repo
- validacao estrutural do repo inspirada em `iageny`, mas focada na camada de IA/governanca deste repo
- catalogos, routing policy, rules e evals adaptados ao dominio de dotfiles, bootstrap, paridade Windows/WSL, auth e integracoes do workstation
- papeis de implementation agents de `iageny` traduzidos para papeis permanentes aderentes a este repo
- fluxo de [`docs/TASKS.md`](docs/TASKS.md), [`docs/WORKFLOWS.md`](docs/WORKFLOWS.md) e `validate_workflow_task_sync.py` inspirado em `py-bootstrap` e `iageny`, mas ajustado aos workflows reais desta worktree
- camada de intake/route/delegate portada dos taskfiles shell das fontes para backend Python worktree-friendly
- stack Python de qualidade portada para `uv` com `ruff`, `ty`, `pytest`,
  `pymarkdownlnt` e `yamllint`, mas ajustada para worktree compartilhada
  Windows/WSL com `.venv/windows` e `.venv/linux`
- wrappers de `actionlint` e `gitleaks` adaptados para pinagem declarativa em
  [`config/tooling.releases.yaml`](config/tooling.releases.yaml)
- `validate_docs.py` adaptado para o estilo documental real deste repo, com
  foco em links locais quebrados e sem impor reescrita massiva de Markdown

### Importar em etapas seguintes

- integracao opcional com execpolicy/rules engine quando a ferramenta existir localmente
- datasets e cenarios de eval ainda mais ricos, incluindo bootstrap full, auth real e risco operacional mais pesado
- validadores documentais adicionais inspirados em `iageny`, quando o custo de correcoes for aceitavel para este repo
- `pre-commit` como orquestrador unico de hooks, somente se o repo decidir
  substituir a atual estrategia com [`.githooks/`](.githooks/)
- promocao de `cspell` ao gate canonico, depois da curadoria do dicionario
- type checking mais amplo na camada Python, somente apos reduzir debt nos
  scripts historicos e fechar a configuracao alvo (`ty` amplo, `mypy` ou ambos)

Motivo do fatiamento: essas camadas precisam ser adaptadas ao problema especifico deste repo e a sua arquitetura de bootstrap Windows/WSL, nao apenas copiadas.

## Fronteira entre [`.agents`](.agents) canonico e [`.codex`](.codex) legado

Contrato decidido para este repo:

- [`.agents/`](.agents/) guarda a fonte de verdade completa da camada de IA do projeto
- [`.agents/cards/`](.agents/cards/) guarda cartoes operacionais e [`.agents/skills/`](.agents/skills/), [`.agents/registry/`](.agents/registry/), [`.agents/orchestration/`](.agents/orchestration/), [`.agents/rules/`](.agents/rules/) e [`.agents/evals/`](.agents/evals/) guardam a camada declarativa
- [`.codex/`](.codex/) no repo e apenas um ponto de compatibilidade documental e deve conter so [`README.md`](README.md)
- runtime local, sessoes, auth, caches e historico continuam fora do Git

## Regra operacional permanente

Nenhuma futura importacao ou adaptacao cross-repo deve comecar pela implementacao.

Sequencia obrigatoria:

1. auditar exaustivamente a fonte
2. registrar o inventario e o gap analysis
3. decidir o que sera adotado, adaptado ou adiado
4. so entao editar codigo, docs, tasks, workflows ou ativos declarativos

## Referencias externas complementares (2026-03-07)

Fontes adicionais pesquisadas para ideias de roadmap, sem importacao direta de
codigo nesta rodada:

### atxtechbro/dotfiles

- fonte: https://github.com/atxtechbro/dotfiles
- sinais relevantes:
  - fonte unica de configuracao para multiplos harnesses de IA
  - `knowledge/` global separado de docs especificos do repo
  - MCP global e simetria entre harnesses
  - procedimentos reproduziveis em comandos e worktrees paralelas
- aproveitamento potencial aqui:
  - geracao multiplataforma de adaptadores de IA a partir de uma fonte canonica
  - camada de conhecimento portavel separada do contexto especifico do repo

### jppferguson/dotfiles

- fonte: https://github.com/jppferguson/dotfiles
- sinais relevantes:
  - fluxo explicito para `install`, `status`, `diff`, `sync` e `backup` da configuracao de IA
  - estrategia de copia no lugar de symlink quando o harness tem bug conhecido
- aproveitamento potencial aqui:
  - commands/tasks de sincronismo e diff entre repo e `HOME` da ferramenta
  - fallback copy-vs-symlink por adaptador, em vez de assumir que todo harness aceita link

### joshukraine/dotfiles

- fonte: https://github.com/joshukraine/dotfiles
- sinais relevantes:
  - comandos slash estruturados para o ciclo completo de desenvolvimento
  - presets composaveis de permissao
  - hooks de seguranca e deny rules para operacoes perigosas
- aproveitamento potencial aqui:
  - presets de permissao por contexto (`dotfiles`, `review`, `sprint`, `ci`)
  - hooks/policies para bloquear leitura de segredos e comandos destrutivos

### basnijholt/dotfiles

- fonte: https://github.com/basnijholt/dotfiles
- sinais relevantes:
  - arvore explicita de configs por ferramenta (`claude`, `codex`, `gemini`, `opencode`)
  - bootstrap cross-platform forte
  - `Dockerfile` para experimentar o ambiente sem instalar tudo
  - branch publica sanitizada e install declarativo
- aproveitamento potencial aqui:
  - adaptadores dedicados por ferramenta de IA no `HOME`
  - export publico/sanitizado quando quisermos separar runtime privado de perfil compartilhavel

### Anthropic Claude Code Docs

- fontes:
  - settings: https://code.claude.com/docs/en/settings
  - memory: https://code.claude.com/docs/en/memory
  - hooks: https://code.claude.com/docs/en/hooks
  - MCP: https://code.claude.com/docs/en/mcp
- sinais relevantes:
  - hierarquia clara entre config de usuario, projeto e politica gerenciada
  - `CLAUDE.md` com imports
  - hooks, inclusive agent hooks e async hooks
  - expansao de variaveis em `.mcp.json`
- aproveitamento potencial aqui:
  - reforcar politicas de seguranca por harness
  - manter separacao entre escopo global e escopo do repo
  - gerar MCP/config com placeholders canonicos e expansao de env
