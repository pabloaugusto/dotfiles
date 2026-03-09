# Spike: cobertura de agentes, review especializado e priorizacao continua

- Status: `consolidado-incremental`
- Data-base: `2026-03-08`
- Epic Jira: [`DOT-71`](https://pabloaugusto.atlassian.net/browse/DOT-71)
- Task pai original: [`DOT-97`](https://pabloaugusto.atlassian.net/browse/DOT-97)
- Spike Jira ativa: [`DOT-105`](https://pabloaugusto.atlassian.net/browse/DOT-105)
- Atualizado em: `2026-03-09`

## Perguntas de pesquisa

- O reviewer generico deve continuar como unico gate de revisao tecnica do sistema?
- O `ai-tech-lead` deve absorver toda a revisao de codigo para ganhar velocidade?
- Qual desenho traz mais qualidade e menos gargalo para um fluxo autonomo?
- O que um spike maduro precisa registrar para de fato reduzir incerteza?
- Como o `AI Product Owner` deve atuar na ordenacao do backlog e do timeline?
- Como garantir paridade entre `dev especializado` e `reviewer especializado`?
- Quais papeis ainda faltam na malha declarativa de [`.agents/`](../../.agents/)?
- Quando `Markdown`, `Confluence` e artefatos documentais devem ser tratados como
  escopo do [`ai-documentation-agent`](../../config/ai/agents.yaml)?

## Fontes oficiais consultadas

### Atlassian

- [What are code reviews and how do they save time?](https://www.atlassian.com/br/agile/software-development/code-reviews)
- [Working with specialists](https://www.atlassian.com/br/agile/teams/working-with-specialists)
- [Backlog refinement meeting](https://www.atlassian.com/br/agile/project-management/backlog-refinement-meeting)
- [Definition of Ready](https://www.atlassian.com/br/agile/project-management/definition-of-ready)
- [Acceptance criteria](https://www.atlassian.com/work-management/project-management/acceptance-criteria)
- [Epics, stories, themes, and initiatives](https://www.atlassian.com/br/agile/project-management/epics-stories-themes)

### GitHub

- [About pull request reviews](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/about-pull-request-reviews)
- [About code owners](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)

### Fontes internas relacionadas

- [`2026-03-08-manual-agilidade-control-plane.md`](2026-03-08-manual-agilidade-control-plane.md)
- [`artifacts/jira-writing-standards.md`](artifacts/jira-writing-standards.md)
- [`artifacts/agent-operations.md`](artifacts/agent-operations.md)
- [`artifacts/reviewer-standards-catalog.md`](artifacts/reviewer-standards-catalog.md)
- [`artifacts/reviewer-decision-model.md`](artifacts/reviewer-decision-model.md)
- [`artifacts/python-quality-review-agent.md`](artifacts/python-quality-review-agent.md)
- [`artifacts/universal-engineering-standards-stack.md`](artifacts/universal-engineering-standards-stack.md)
- [`../../config/ai/agents.yaml`](../../config/ai/agents.yaml)
- [`../../config/ai/agent-operations.yaml`](../../config/ai/agent-operations.yaml)
- [`../../config/ai/jira-model.yaml`](../../config/ai/jira-model.yaml)
- [`../../config/ai/reviewer-policies.yaml`](../../config/ai/reviewer-policies.yaml)
- [`../../config/ai/reviewer-standards.yaml`](../../config/ai/reviewer-standards.yaml)
- [`../../.agents/config.toml`](../../.agents/config.toml)
- [`../../.agents/orchestration/capability-matrix.yaml`](../../.agents/orchestration/capability-matrix.yaml)
- [`../../.agents/orchestration/routing-policy.yaml`](../../.agents/orchestration/routing-policy.yaml)

## Achados

### 1. Reviewer generico sozinho nao entrega a profundidade necessaria

Um reviewer unico pode validar coerencia geral, risco sistemico e aderencia ao
processo, mas tende a perder profundidade quando precisa revisar ao mesmo tempo:

- Python
- PowerShell
- automacao e CI
- YAML, JSON, TOML, schemas e contratos declarativos

Para um sistema autonomo, isso vira gargalo e reduz a confianca da aprovacao.

### 2. Tech lead nao deve virar reviewer universal

O `Tech Lead` precisa preservar capacidade para:

- decompor trabalho
- orientar a implementacao
- coordenar handoffs
- arbitrar trade-offs e excecoes

Se ele absorver toda a revisao detalhada, o fluxo perde throughput e cria
dependencia excessiva em um unico papel.

### 3. O desenho mais forte e especialista + gate transversal

O modelo mais robusto para este piloto e:

- developers especialistas por familia de entrega executam o trabalho tecnico
- revisores especialistas por familia de arquivo fazem a revisao profunda
- `ai-reviewer` consolida ou atua em revisoes cross-cutting
- `ai-tech-lead` entra quando houver duvida arquitetural, excecao ou conflito

Isso aproxima o fluxo do uso de especialistas recomendado pela Atlassian e do
modelo de ownership por areas de codigo formalizado pelo GitHub com reviewers e
`CODEOWNERS`.

### 3.1. Paridade obrigatoria entre dev e reviewer especializados

O fluxo fica mais robusto quando cada familia relevante de trabalho tem um par
explicito:

- `ai-developer-python` <-> `ai-reviewer-python`
- `ai-developer-powershell` <-> `ai-reviewer-powershell`
- `ai-developer-automation` <-> `ai-reviewer-automation`
- `ai-developer-config-policy` <-> `ai-reviewer-config-policy`

Para `Markdown`, `Confluence`, runbooks, ADRs e documentacao viva, a melhor
paridade pratica e:

- `ai-documentation-agent` como developer especializado
- `ai-reviewer-config-policy` como reviewer especializado
- `ai-reviewer` como gate transversal quando o impacto for cross-cutting

### 3.2. Um unico `Doing` global nao faz sentido; um `Doing` por agente faz

Para uma operacao autonoma madura:

- pode haver mais de uma issue em `Doing`
- cada issue em `Doing` precisa ter um agente ativo explicito
- um mesmo agente nao deve carregar mais de uma execucao real em `Doing`
- quando a execucao parar, a issue deve sair de `Doing` para `Paused`

### 4. Spikes atuais ainda estao superficiais demais

O schema minimo anterior cobria:

- perguntas
- achados
- riscos
- alternativas
- recomendacao
- referencias

Isso e insuficiente para um refinamento maduro. Faltavam itens recorrentes que o
usuario vem cobrando corretamente:

- evidencias
- viabilidade
- ganhos esperados
- custo operacional
- pendencias abertas

### 5. O PO precisa manter prioridade e calendario como trabalho continuo

As fontes de backlog refinement e `DoR` reforcam que o backlog nao e uma fila
estatica. Se entra algo novo, o item precisa cair no ponto certo da prioridade.

Para este projeto, isso implica que o `AI Product Owner` deve:

- reordenar `Backlog`, `Refinement` e `Ready` continuamente
- recalcular `Priority`, `Start date` e `Due date`
- manter timeline e roadmap em paridade com o estado real do fluxo

### 6. A malha declarativa ainda esta incompleta

O repositorio ja possui uma boa base para reviewers especialistas e contracts de
review, mas o estado real ainda mostra gaps importantes:

- [`.agents/registry/`](../../.agents/registry/) ainda nao contem todos os
  papeis da control plane do `Jira`
- [`.agents/cards/`](../../.agents/cards/) ainda nao cobre todos os papeis
  ativos do tenant
- a camada local de agentes esta mais madura para reviewers do que para devs
  especializados
- falta formalizar o papel transversal de paridade `Jira <-> fluxo de IA`
- skills, schemas e templates-base ainda nao refletem toda a nova complexidade
  da malha especializada

### 7. O reviewer de config-policy vira peca critica

Como o fluxo agora depende muito de:

- YAML
- JSON
- TOML
- Markdown
- schemas declarativos
- contratos operacionais

o `ai-reviewer-config-policy` deixa de ser opcional e passa a ser gate real para
esse tipo de mudanca. Sem ele, qualquer issue que altere
[`../../config/ai/`](../../config/ai/), documentacao governada ou contracts
declarativos tende a ficar com review incompleto.

## Evidencias

- Inventario de lacunas operacionais em [`DOT-97`](https://pabloaugusto.atlassian.net/browse/DOT-97)
- Spike ativa em [`DOT-105`](https://pabloaugusto.atlassian.net/browse/DOT-105)
- Modelo atual da control plane ja descreve pares especializados em
  [`../../config/ai/agents.yaml`](../../config/ai/agents.yaml), mas a camada de
  [`.agents/registry/`](../../.agents/registry/) e [`.agents/cards/`](../../.agents/cards/)
  ainda nao esta em paridade total com esse catalogo
- O repo ja possuia revisores especialistas fora da camada Jira/Confluence em
  [`../../docs/AI-AGENTS-CATALOG.md`](../../docs/AI-AGENTS-CATALOG.md)
- O modelo formal de review Python foi consolidado em
  [`artifacts/python-quality-review-agent.md`](artifacts/python-quality-review-agent.md)
- A base normativa transversal dos reviewers foi consolidada em
  [`artifacts/reviewer-standards-catalog.md`](artifacts/reviewer-standards-catalog.md)
- A stack normativa ampla que deve alimentar os reviewers especializados foi
  consolidada em
  [`artifacts/universal-engineering-standards-stack.md`](artifacts/universal-engineering-standards-stack.md)

## Viabilidade

Alta.

O repo ja possui boa parte das pecas:

- contratos formais de review, severidade e decisao
- catalogo normativo dos reviewers especializados
- cards e registry de parte dos revisores especialistas
- contratos de comentario estruturado
- custom fields `Current Agent Role` e `Next Required Role`
- automacao Jira suficiente para refletir novos papeis

O trabalho principal e alinhar as camadas declarativas e o tenant.

## Riscos

- criar revisores demais sem criterio pode burocratizar o fluxo
- criar developers especialistas sem refletir isso em routing, cards e Jira gera
  ownership fantasma
- manter reviewer generico como unico gate continua produzindo aprovacoes rasas
- usar `tech lead` como reviewer universal cria gargalo e dependencia excessiva
- deixar `ai-documentation-agent` fora da paridade dev/reviewer para Markdown e
  Confluence enfraquece rastreabilidade
- manter spikes superficiais enfraquece refinamento e piora previsibilidade

## Alternativas

### Alternativa A - manter apenas `ai-reviewer`

Simples, mas fraca em profundidade tecnica.

### Alternativa B - transferir tudo para `ai-tech-lead`

Melhora consistencia tecnica, mas cria gargalo forte.

### Alternativa C - especialista por familia + gate transversal

Melhor equilibrio entre:

- profundidade
- throughput
- ownership
- rastreabilidade

### Alternativa D - reviewers especialistas sem developers especialistas

Melhora parte da revisao, mas mantem difuso quem realmente executa cada familia
de entrega.

## Ganhos esperados

- reviews mais tecnicos e defensaveis
- menos gargalo no `Tech Lead`
- maior paridade entre familias de arquivo e agentes especializados
- mais de uma demanda pode avancar em paralelo sem falsificar o `Doing`
- spikes mais uteis para refinamento real
- backlog e timeline mais confiaveis para roadmap, release e deploy

## Custo operacional

Moderado.

Custos principais:

- criar ou adaptar cards e registry para developers especializados
- expandir opcoes de `Current Agent Role` e `Next Required Role`
- atualizar contracts, workflow e filtros do `Jira`
- criar ou adaptar automacoes para apontar o reviewer especializado correto
- atualizar skills, schemas, templates e capability matrix
- reescrever descricoes de spikes e historias mais antigas quando necessario

## Pendencias abertas

- decidir se `ai-reviewer` permanece obrigatorio em todo fluxo ou apenas em
  cenarios cross-cutting
- formalizar o conjunto minimo de developers especializados na camada
  [`.agents/`](../../.agents/)
- refletir os novos papeis no tenant do `Jira`
- revisar backlog retroativo para identificar itens com reviewer incorreto
- avaliar `CODEOWNERS` e required reviewers quando a frente GitHub voltar a ser prioritaria

## Recomendacao

Adotar imediatamente:

1. revisores especialistas por familia de arquivo
2. developers especialistas por familia de entrega, em paridade com os reviewers
3. `ai-documentation-agent` como dev especializado para Markdown e doc viva
4. `ai-reviewer` como gate transversal, nao reviewer unico
5. `ai-tech-lead` como coordenador tecnico e arbitro de excecao
6. `Spike` enriquecida com evidencia, viabilidade, ganhos, custo e pendencias
7. `AI Product Owner` como responsavel continuo por prioridade e timeline dos
   itens acima de subtarefa

## Proximos passos recomendados

- formalizar developers e reviewers especializados no schema da control plane,
  em [`.agents/`](../../.agents/) e no `Jira`
- criar tasks de implementacao para cards, registry, skills, templates e
  capability matrix
- endurecer o contrato do `PO` para reordenacao continua de backlog e timeline
- usar este spike como referencia oficial para elevar a qualidade de futuras
  `Story`, `Task` e `Spike`
