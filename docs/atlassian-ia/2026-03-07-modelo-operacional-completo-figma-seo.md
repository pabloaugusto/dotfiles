# Modelo Operacional Completo com Figma e SEO

- Status: `input-do-usuario`
- Origem: contexto adicional enviado em 2026-03-07
- Curadoria: consolidado em formato rastreavel para a trilha Atlassian + IA
- Relacionados:
  - [`docs/atlassian-ia/README.md`](README.md)
  - [`docs/atlassian-ia/2026-03-07-parecer-e-plano-inicial.md`](2026-03-07-parecer-e-plano-inicial.md)

## Objetivo do contexto

Estender o modelo do `AI Product Owner System` para um time agil completo
operado por IA, incluindo:

- Jira para backlog e execucao
- Confluence para documentacao
- repositorio para codigo
- Figma para design e prototipacao
- CI/CD para validacao e automacao
- ferramentas de SEO para validacao tecnica e estrategica

## Fontes de verdade e ferramentas auxiliares

O contexto reafirma tres fontes oficiais:

- Jira para backlog e workflow
- Confluence para documentacao
- repositorio para codigo

Ferramentas auxiliares propostas:

- Figma
- ferramentas de SEO

Markdown no repo continua tratado como artefato derivado sincronizado.

## Papeis propostos

- `AI Product Owner`
- `AI Architect`
- `AI Designer`
- `AI UX / CRO Analyst`
- `AI Developers Especializados`
- `AI QA`
- `AI Reviewer`
- `AI DevOps`
- `AI Documentation Agent`
- `AI SEO Specialist`

## Identidade por agente

O contexto pede service accounts distintas, por exemplo:

- `ai-product-owner`
- `ai-architect`
- `ai-designer`
- `ai-ux`
- `ai-dev-python`
- `ai-dev-js-front`
- `ai-dev-js-back`
- `ai-dev-shell-linux`
- `ai-dev-shell-windows`
- `ai-qa`
- `ai-reviewer`
- `ai-devops`
- `ai-docs`
- `ai-seo`

## Regra central de backlog

Regra proposta:

- apenas o `AI Product Owner` cria e prioriza issues principais
- outros agentes podem sugerir trabalho e propor novas demandas
- qualquer agente pode criar subtasks dentro de uma issue existente

## Papel das subtasks

Subtasks passam a servir para:

- quebrar tarefas complexas
- registrar trabalho tecnico menor
- dividir responsabilidade
- organizar execucao
- registrar atividades emergentes

Exemplos citados:

- developers criando implementacoes e testes unitarios
- QA criando subtasks de regressao ou validacao por ambiente
- SEO criando subtasks de meta tags, semantica ou imagens
- DevOps criando subtasks de CI, pipeline e lint

## Estrutura de backlog proposta

Dois niveis principais:

- `Backlog bruto`
- `Backlog refinado`

O fluxo de preparacao sugerido e:

```text
Backlog -> Refinement -> Ready
```

Somente itens em `Ready` podem ser puxados pelos developers.

## Definition of Ready proposta

Para um item entrar em `Ready`, o contexto pede:

- descricao clara
- contexto tecnico
- criterios de aceitacao
- definicao de escopo
- documentacao relevante
- design quando necessario
- impacto SEO considerado quando aplicavel

## Workflow expandido

Fluxo proposto:

- `Backlog`
- `Refinement`
- `Ready`
- `Doing`
- `Testing`
- `Review`
- `SEO Review`
- `Changes Requested`
- `Done`

Movimentacao sugerida:

- `Product Owner`: `Backlog -> Refinement -> Ready`
- `Developers`: `Ready -> Doing`
- `QA`: `Doing -> Testing`
- `Reviewer`: `Testing -> Review`
- `SEO Specialist`: `Review -> SEO Review`
- `Done`: `SEO Review -> Done`

Falhas:

- `Testing -> Changes Requested`
- `Review -> Changes Requested`
- `SEO Review -> Changes Requested`
- `Changes Requested -> Doing`

## Papel do refinamento

O refinamento e conduzido por:

- `AI Product Owner`
- `AI Architect`
- `AI UX`
- `AI Designer`, quando necessario

Nessa etapa, devem ser definidos:

- escopo
- requisitos
- criterios de aceitacao
- impacto tecnico
- dependencias
- design ou UX
- documentacao relevante
- implicacoes SEO quando aplicavel

## Capacidade por papel

### AI Architect

- decisoes arquiteturais
- padroes tecnicos
- validacao estrutural
- ADRs no Confluence

### AI Designer

- wireframes
- prototipos
- layouts
- fluxos de interacao via Figma

### AI UX / CRO Analyst

- experiencia do usuario
- conversao
- usabilidade
- clareza de fluxos

### Developers especializados

O contexto pede developers seniores por especialidade, como:

- Python
- JavaScript frontend
- JavaScript backend
- shell Linux
- shell Windows
- infraestrutura

### AI SEO Specialist

O contexto posiciona o SEO como ultimo reviewer antes do `Done`, com uso de:

- Google Search Console
- Google Analytics
- Amplitude
- Screaming Frog
- SEMrush
- Python
- APIs das plataformas
- documentacao oficial Google Search

Validacoes citadas:

- Core Web Vitals
- EEAT
- YMYL
- Google Search Essentials
- Technical SEO

## Artefatos derivados sugeridos

- espelho local de backlog
- espelho local de roadmap
- espelho local de arquitetura
- espelho local de SEO

## Tese de conclusao

O contexto fecha o modelo com estas regras:

- apenas o Product Owner cria e prioriza issues
- qualquer agente pode criar subtasks
- desenvolvimento so com item refinado
- developers especializados executam implementacao
- QA valida
- reviewer revisa
- SEO valida qualidade final quando aplicavel
- documentacao e sincronizada
- todas as acoes sao registradas
