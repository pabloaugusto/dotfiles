# Operacao de Jira e Confluence por Agentes de IA

- Status: `input-do-usuario`
- Origem: contexto adicional enviado em 2026-03-07
- Curadoria: consolidado em formato versionado para rastreabilidade local
- Relacionados:
  - [`README.md`](README.md)
  - [`2026-03-07-parecer-e-plano-inicial.md`](2026-03-07-parecer-e-plano-inicial.md)

## Escopo

Definir como os agentes de IA devem operar Jira e Confluence reproduzindo o
comportamento de um time agil real.

A tese do contexto e clara:

- os agentes nao apenas movem cards
- os agentes devem executar toda a operacao tipica de um time agil

## Principio operacional

Os agentes nao devem operar fora das ferramentas oficiais de governanca:

- `Jira` para execucao do trabalho
- `Confluence` para documentacao e conhecimento

## Identidade dos agentes

Cada agente deve possuir identidade propria nas ferramentas, por exemplo:

- `ai-product-owner`
- `ai-developer`
- `ai-qa`
- `ai-reviewer`
- `ai-devops`
- `ai-architect`
- `ai-docs`

O objetivo e garantir:

- auditoria
- rastreabilidade
- separacao de responsabilidades

## Operacao agil completa

O contexto pede que os agentes ajam como membros reais do time:

- movimentando cards
- comentando tecnicamente
- registrando decisoes
- registrando progresso
- documentando problemas
- registrando testes
- registrando revisoes
- anexando evidencias

## Tipos de interacao nas issues

Cada interacao deve ser registrada como comentario estruturado. Tipos citados:

- progresso
- decisao tecnica
- descoberta inesperada
- mudanca de escopo
- mudanca de prioridade
- evidencia de teste
- falha de teste
- sucesso de teste
- revisao tecnica
- bloqueio
- proposta de melhoria

## Cadencia obrigatoria de comentarios

O comentario do agente nao deve acontecer apenas ao final da sua participacao.

Para toda issue rastreada no `Jira`, a regra correta passa a ser:

- comentar quando iniciar a propria atuacao
- comentar ao longo da execucao sempre que houver marco relevante, descoberta,
  decisao ou mudanca de estado
- comentar antes de handoff, pausa, aprovacao, reprovacao ou encerramento da
  participacao naquele item
- atualizar o status da issue em tempo real, em paridade com o comentario mais
  recente e com o estado real da demanda

## Registros operacionais esperados

### Progresso

Durante implementacao, o agente de desenvolvimento deve registrar:

- estado atual
- contexto da acao em curso
- proximo passo

### Decisoes tecnicas

Cada decisao relevante deve registrar:

- decisao tomada
- motivo
- impacto

### Descobertas inesperadas

Problemas ou comportamentos nao previstos devem registrar:

- descoberta
- impacto
- acao tomada

### Mudancas de escopo

O `AI Product Owner` deve registrar:

- o que mudou no escopo
- por que mudou
- impacto esperado

### Mudancas de prioridade

O `AI Product Owner` tambem deve registrar:

- prioridade anterior
- nova prioridade
- motivo da mudanca

## Registros de testes

O contexto pede que `AI QA` documente:

- ambiente
- teste executado
- resultado
- evidencias

Em caso de falha:

- anexar ou linkar log
- descrever o problema
- mover a issue para `Changes Requested`

Em caso de sucesso:

- listar os cenarios testados
- explicitar que passaram

## Registros de revisao

O `AI Reviewer` deve registrar:

- resultado da revisao
- observacoes tecnicas
- aprovacao ou `changes requested`

## Registros de bloqueio

Bloqueios devem registrar:

- dependencia
- acao sugerida
- eventual necessidade de nova task

## Evidencias esperadas

O contexto pede rastreabilidade por:

- logs
- outputs
- prints
- links de pipeline
- links de commits

## Relacao entre Jira e Confluence

O modelo proposto pede um grafo de conhecimento entre:

- paginas de documentacao
- issues
- epicos
- decisoes tecnicas

Uma pagina deve referenciar issues relacionadas, e uma issue deve apontar para
as paginas de documentacao relevantes.

## Fluxo Kanban assumido

O contexto reutiliza o fluxo:

- `Backlog`
- `Ready`
- `Doing`
- `Testing`
- `Review`
- `Changes Requested`
- `Done`

## Beneficios esperados

- transparencia
- rastreabilidade
- auditabilidade
- governanca
- historico completo do desenvolvimento

## Conclusao do contexto

O modelo defendido e que agentes de IA realmente operem como uma equipe agil
real:

- dentro das ferramentas
- registrando tudo
- preservando rastreabilidade
- seguindo um fluxo operacional completo
