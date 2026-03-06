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

## Arquitetura local

### Camada 1. Contrato global

- `AGENTS.md`
- `CONTEXT.md`
- `docs/test-strategy.md`
- `docs/ai-operating-model.md`

### Camada 2. Skills do repo

As skills ficam em `ai/skills/` e seguem o contrato:

- `SKILL.md` curto e acionavel
- `agents/openai.yaml` com metadata reutilizavel
- `references/` para detalhes que nao precisam poluir o prompt principal

### Camada 3. Cartoes de agentes

Os papeis operacionais ficam em `ai/agents/`. Cada cartao define:

- objetivo
- quando usar
- entradas
- saidas
- fluxo
- guardrails
- criterio de conclusao

Esses cartoes funcionam como prompt-base para subagentes humanos ou de IA.

### Camada 4. Validacao

`scripts/validate-ai-assets.ps1` valida:

- frontmatter das skills
- metadata dos agentes
- estrutura minima dos cartoes
- ausencia de placeholders e `TODO`

### Camada 5. Automacao

- `task ai:validate`
- `task ai:install:codex`
- workflow `AI Governance`

## Politica de versionamento

### Versionar

- `AGENTS.md`
- `ai/skills/**`
- `ai/agents/**`
- prompts e docs declarativos do repo
- templates estaveis que precisem ser materializados pelo bootstrap

### Nao versionar

- `.codex/`
- `.gemini/`
- `.agents/`
- sessoes, historico, caches, bancos sqlite e memoria local
- perfis de navegador
- tokens, auth, cookies, state files e configuracoes geradas por login

## Decisao sobre `~/.gemini`

Com base na estrutura local inspecionada, `~/.gemini` mistura:

- browser profile
- historico de conversas
- estado interno do agente
- arquivos gerados por execucao

Isso torna a pasta inadequada como fonte de verdade do repo. O que faz sentido versionar e somente a camada declarativa e portavel, por exemplo um `GEMINI.md` mantido no repo e depois materializado no `HOME` por bootstrap. A pasta inteira nao deve entrar no Git.

## Estrategia de evolucao

1. Manter `AGENTS.md` curto.
2. Criar skills pequenas e especializadas.
3. Empurrar detalhes para `references/`.
4. Validar mudancas em CI.
5. Reusar workflows e tasks sempre que possivel.

## Fontes

- OpenAI Prompting: https://platform.openai.com/docs/guides/prompting
- OpenAI Evals: https://platform.openai.com/docs/guides/evals
- OpenAI Evaluation Best Practices: https://platform.openai.com/docs/guides/evaluation-best-practices
- GitHub Actions reusable workflows: https://docs.github.com/en/actions/reference/workflows-and-actions/reusing-workflow-configurations
- GitHub Actions avoiding duplication: https://docs.github.com/actions/concepts/workflows-and-actions/avoiding-duplication
