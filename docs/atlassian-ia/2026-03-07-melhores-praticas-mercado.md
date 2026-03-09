# Desenvolvimento Autonomo com IA + Jira + Confluence

- Status: `input-do-usuario`
- Origem: contexto adicional enviado em 2026-03-07
- Observacao: este arquivo preserva o insumo do usuario; a validacao oficial e
  o parecer consolidado ficam em
  [`2026-03-07-parecer-e-plano-inicial.md`](2026-03-07-parecer-e-plano-inicial.md)
- Relacionados:
  - [`README.md`](README.md)
  - [`2026-03-07-blueprint-ai-product-owner-system.md`](2026-03-07-blueprint-ai-product-owner-system.md)

## Escopo do contexto

Este contexto amplia o blueprint com boas praticas de mercado para:

- agentes de IA
- Jira
- Confluence
- repositorios de codigo
- pipelines CI/CD
- fluxo agil

## Tese central

O modelo defendido e de `AI-native software development`, em que a IA evolui de
assistente pontual para parte integrada do ciclo completo de produto e
engenharia.

Evolucao resumida:

1. IA assistindo desenvolvedores
2. IA executando tarefas isoladas
3. sistemas multiagente coordenando o ciclo de desenvolvimento
4. IA integrada ao ciclo completo de produto e negocio

## Papel da IA na gestao de projetos

O contexto destaca que a IA pode apoiar:

- automacao de tarefas
- acompanhamento de progresso
- analise do estado do projeto
- identificacao de riscos
- recomendacao de acoes
- geracao de relatorios
- otimizacao de recursos

## Ecossistema Atlassian

O contexto aponta que a propria Atlassian vem construindo capacidades para:

- organizar issues
- gerar documentacao
- criar planos tecnicos
- analisar codigo
- sugerir melhorias

Tambem traz como direcao:

- uso de `Rovo Dev`
- integracao com `MCP`
- acesso seguro ao contexto organizacional em Jira e Confluence

## Arquitetura multiagente defendida

O modelo de mercado destacado pelo contexto favorece agentes especializados,
como:

- `Planner`
- `Coder`
- `Debugger`
- `Reviewer`

O raciocinio e que diferentes agentes reduzem erro e elevam qualidade ao se
revisarem mutuamente.

## Padroes de orquestracao citados

- `prompt chaining`
- `routing`
- `parallelization`
- `planner-critic`

## Human in the loop

Este contexto reforca uma regra importante:

- a IA executa, sugere e analisa
- o humano continua como autoridade final para decisoes estrategicas

Modelo defendido:

```text
Humano define objetivos
IA executa tarefas
IA sugere melhorias
Humano valida decisoes estrategicas
```

## Melhores praticas resumidas

- integrar a IA ao ciclo de vida completo
- centralizar backlog em ferramenta rastreavel como Jira
- usar agentes especializados em vez de um unico agente generalista
- dar acesso da IA ao contexto real da organizacao
- manter governanca, auditoria e explicabilidade
- usar IA para gerar e manter documentacao
- automatizar tarefas repetitivas de backlog, changelog e analise

## Riscos destacados

- codigo gerado por IA pode introduzir vulnerabilidades
- uso sem supervisao cria falsa sensacao de precisao
- planejamento e priorizacao sem dados completos continuam arriscados

## Modelo recomendado pelo contexto

```text
Repository Intelligence
        |
        v
AI Product Owner
        |
        v
Backlog Platform (Jira)
        |
        v
Delivery Agents
        |
        v
Workflow Kanban
        |
        v
Confluence Documentation
```

Com suporte de:

- `MCP`
- `CI/CD`
- agentes especializados

## Implicacao para este repo

O contexto considera que o blueprint esta alinhado com:

- multi-agent architecture
- human-in-the-loop
- Jira como backlog source of truth
- Confluence como knowledge source of truth
- rastreabilidade e governanca

## Proxima evolucao sugerida pelo contexto

- arquitetura interna do sistema de agentes
- memoria dos agentes
- modelo de eventos
- banco de dados
- contratos dos adapters
- politicas de backlog
- formato dos espelhos Markdown
- seguranca e auditoria
