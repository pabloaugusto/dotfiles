# AI Operating Model

## Objetivo

Criar uma camada local de IA que seja:

- versionada
- reutilizavel
- testavel
- curta e especifica
- segura para operar em worktree, CI e uso manual

## Principios

### 1. Instrucoes claras e curtas

As instrucoes base devem ser pequenas, diretas e estaveis. O papel de `AGENTS.md` e alinhar linguagem, guardrails e fontes de verdade; os detalhes operacionais ficam nas skills e referencias.

### 2. Especializacao por escopo

Cada skill cobre um dominio estreito do repo. Isso reduz ambiguidade, evita prompts gigantes e melhora a reusabilidade em tarefas futuras.

### 3. Iteracao guiada por validacao

Prompts, skills e fluxos de agentes devem ser tratados como codigo: versao, review e validacao automatica. Mudanca sem avaliacao de saida aumenta regressao silenciosa.

### 4. Automacao reutilizavel

A automacao deve morar em scripts, tasks e workflows reutilizaveis. Isso reduz duplicacao e facilita evoluir CI/CD sem espalhar logica em varios pontos.

### 5. Auditoria exaustiva antes de reuso cross-repo

Quando a tarefa envolver importar, adaptar, comparar ou consolidar contratos de outro repo, a IA nao pode trabalhar por amostragem.

Cobertura minima obrigatoria da auditoria:

- contratos globais
- docs e catalogos
- tasks, taskfiles e aliases
- scripts e CLIs
- workflows, hooks e gates
- validadores e testes
- agentes, skills e metadata
- orquestracao, rules e evals
- relacoes entre esses elementos

Sem essa auditoria, o risco e alto de trazer governanca quebrada, testes incompletos, docs sem backend real ou duplicacao de contratos.

## Arquitetura local

### Camada 1. Contrato global

- `AGENTS.md`
- `LICOES-APRENDIDAS.md`
- `CONTEXT.md`
- `docs/test-strategy.md`
- `docs/ai-operating-model.md`
- `docs/AI-WIP-TRACKER.md`
- `docs/ROADMAP.md`
- `docs/ROADMAP-DECISIONS.md`

### Camada 2. Skills do repo

As skills ficam em `.agents/skills/` e seguem o contrato:

- `SKILL.md` curto e acionavel
- `agents/openai.yaml` com metadata reutilizavel
- `references/` para detalhes que nao precisam poluir o prompt principal

Prompt packs versionados tambem devem viver em `.agents/prompts/`, inclusive
material historico, pesquisas e pacotes de contexto usados em auditorias.

### Camada 2.1. Registry declarativo do repo

Os agentes tipados ficam em `.agents/registry/` e definem:

- `id` estavel do papel
- `purpose` e `triggers`
- skills padrao
- contrato de saida
- handoffs e gates obrigatorios

### Camada 2.2. Orquestracao, rules e evals

Para evitar roteamento implcito e drift entre docs e execucao, o repo tambem versiona:

- `.agents/orchestration/` para capability matrix, routing policy e schemas
- `.agents/rules/` para guardrails declarativos de operacao e CI
- `.agents/evals/` para cenarios e datasets minimos de regressao

### Camada 3. Cartoes de agentes

Os papeis operacionais ficam em `.agents/cards/`. Cada cartao define:

- objetivo
- quando usar
- entradas
- saidas
- fluxo
- guardrails
- criterio de conclusao

Esses cartoes funcionam como prompt-base para subagentes humanos ou de IA.

### Fronteira entre `.agents/` e adaptadores de assistente

Para evitar ambiguidades e drift:

- `.agents/` e a fonte canonica de contratos, skills, registry, orchestration, rules e evals
- `.codex/` no repo guarda apenas um `README.md` de compatibilidade apontando para `.agents/`
- adaptadores especificos de assistente devem ser gerados a partir de `.agents/`, nunca mantidos manualmente em paralelo
- runtime local de IA continua fora do Git

### Camada 4. Validacao

`scripts/validate-ai-assets.ps1` valida:

- frontmatter das skills
- metadata dos agentes
- estrutura minima de `.agents/cards/`
- estrutura minima de `.agents/registry/`
- presenca de `.agents/config.toml`
- presenca de `.agents/README.md`
- presenca de `.codex/README.md`
- presenca de orchestration, rules e evals
- estrutura minima dos cartoes
- presenca dos docs estruturais de WIP
- presenca do contrato de licoes aprendidas
- presenca do inventario versionado de auditoria cross-repo
- coerencia minima do contrato de auditoria exaustiva
- ausencia de placeholders e `TODO`

### Camada 5. Automacao

- `task ai:validate`
- `task ai:chat:intake`
- `task ai:route`
- `task ai:delegate`
- `task ai:eval:smoke`
- `task ai:lessons:check`
- `task ai:rules:check`
- `task ai:install:codex`
- `task ai:worklog:check`
- `task ai:worklog:close:gate`
- `task ci:workflow:sync:check`
- workflow `AI Governance`

`task ai:worklog:check` tambem atua como guardrail de commit checkpoint entre
rodadas: se a worktree estiver suja e nao houver item ativo em `Doing`, a
proxima rodada deve ser bloqueada ate existir commit do contexto anterior.

### Camada 6. Catalogos e fluxo

Os catalogos humanos versionados ficam em:

- `docs/AI-AGENTS-CATALOG.md`
- `docs/AI-SKILLS-CATALOG.md`
- `docs/AI-DELEGATION-FLOW.md`
- `docs/AI-GOVERNANCE-AND-REGRESSION.md`

Esses documentos nao sao "marketing" do sistema; eles sao contratos de operacao e precisam refletir o estado real da camada declarativa.

## Politica de versionamento

### Versionar

- `AGENTS.md`
- `LICOES-APRENDIDAS.md`
- `.agents/**`
- `docs/AI-SOURCE-AUDIT.md`
- `docs/AI-WIP-TRACKER.md`
- `docs/ROADMAP.md`
- `docs/ROADMAP-DECISIONS.md`
- prompts e docs declarativos do repo
- templates estaveis que precisem ser materializados pelo bootstrap

### Nao versionar

- `.gemini/`
- sessoes, historico, caches, bancos sqlite e memoria local
- perfis de navegador
- tokens, auth, cookies, state files e configuracoes geradas por login
- artefatos locais de ferramentas fora da arvore canonica `.agents/`

## Decisao sobre `~/.gemini`

Com base na estrutura local inspecionada, `~/.gemini` mistura:

- browser profile
- historico de conversas
- estado interno do agente
- arquivos gerados por execucao

Isso torna a pasta inadequada como fonte de verdade do repo. O que faz sentido versionar e somente a camada declarativa e portavel, por exemplo um `GEMINI.md` mantido no repo e depois materializado no `HOME` por bootstrap. A pasta inteira nao deve entrar no Git.

## Estrutura no repo

Como `df/` guarda apenas o que sera utilizado na maquina apos o bootstrap, os artefatos de governanca do projeto ficam fora dele. Neste repo:

- `AGENTS.md` define o contrato global do projeto
- `.agents/cards/` guarda cartoes versionados de agentes
- `.agents/skills/` guarda skills versionadas do projeto
- `.agents/prompts/` guarda prompt packs versionados e historico de contexto
- `.agents/registry/`, `.agents/orchestration/`, `.agents/rules/` e `.agents/evals/` guardam a camada declarativa
- `.codex/README.md` deixa explicito que adaptadores de assistente nao sao fonte de verdade
- `docs/AI-WIP-TRACKER.md` guarda o estado incremental do trabalho de IA
- `df/` continua reservado aos dotfiles e assets materializados no ambiente

## Estrategia de evolucao

1. Manter `AGENTS.md` curto.
2. Criar skills pequenas e especializadas.
3. Acionar gates paralelos de arquitetura/modernizacao e integracoes criticas nas analises substantivas.
4. Empurrar detalhes para `references/`.
5. Validar mudancas em CI.
6. Tratar `LICOES-APRENDIDAS.md` como contrato revisado a cada fechamento de worklog.
7. Reusar workflows e tasks sempre que possivel.
8. Auditar exaustivamente antes de importar governanca de outro repo.

## Fontes

- OpenAI Prompting: https://platform.openai.com/docs/guides/prompting
- OpenAI Evals: https://platform.openai.com/docs/guides/evals
- OpenAI Evaluation Best Practices: https://platform.openai.com/docs/guides/evaluation-best-practices
- GitHub Actions reusable workflows: https://docs.github.com/en/actions/reference/workflows-and-actions/reusing-workflow-configurations
- GitHub Actions avoiding duplication: https://docs.github.com/actions/concepts/workflows-and-actions/avoiding-duplication
