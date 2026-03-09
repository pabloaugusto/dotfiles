# Agent Operations

- Status: `artifact-first`
- Data-base: `2026-03-07`
- Fonte canonica:
  [`../../../config/ai/agent-operations.yaml`](../../../config/ai/agent-operations.yaml)
- Sincronizacao alvo:
  - pagina operacional dedicada no `Confluence`
  - issue de governanca e comentarios tecnicos no `Jira`

## Regra central

Cada agente deve registrar sua atuacao de forma estruturada no `Jira` e, quando
houver documentacao correspondente, refletir isso tambem no `Confluence`.

Comentario solto sem prova nao conta como trabalho concluido.

## Campos obrigatorios em comentarios de atividade

- `Agent`
- `Interaction Type`
- `Status`
- `Contexto`
- `Evidencias`
- `Proximo passo`

## Evidencias aceitas

- attachment no `Jira`
- link para comentario anterior no `Jira`
- link de commit ou pull request
- link de pipeline ou job
- log de teste
- screenshot
- link da pagina do `Confluence`
- attachment do migration bundle

## Regras globais do Jira

- nenhuma transicao vale sem comentario estruturado
- todo papel que atuar deve atualizar `Current Agent Role` e `Next Required Role`
- todo papel que atuar deve anexar evidencia ou registrar `n/a` explicito
- mudanca documental relevante deve aparecer tambem na issue correspondente

## Regras globais do Confluence

- toda pagina gerada por trabalho deve linkar a issue correspondente no `Jira`
- atualizacao documental relevante deve ser mencionada na issue correspondente
- o `AI Documentation Agent` governa a arvore de paginas, backlinks e espelhos

## Passo a passo por papel

### `ai-product-owner`

- cria e prioriza issues principais no `Jira`
- registra escopo, prioridade, criterio de aceite e evidencia de intake
- garante link para pagina relevante no `Confluence` ou `n/a`
- move `Backlog -> Refinement -> Ready`

### `ai-engineering-architect`

- registra decisao arquitetural e riscos no `Jira`
- cria ou atualiza `ADR` no `Confluence` quando a decisao for perene
- linka issue e pagina nos dois sentidos
- pode reprovar em `Review -> Changes Requested`

### `ai-engineering-manager`

- registra bloqueios, riscos e replanejamento no `Jira`
- usa evidencia operacional, dependencia concreta ou dado de fila
- atualiza runbooks/processo no `Confluence` quando a regra mudar

### `ai-tech-lead`

- decompõe trabalho em subtasks
- registra plano tecnico, handoff e dependencias no `Jira`
- referencia playbooks e runbooks no `Confluence`
- governa `Ready -> Doing` e retornos `Changes Requested -> Doing`

### `ai-developer-python`

- implementa codigo Python
- registra progresso, decisoes e achados no `Jira`
- anexa commit, diff, log ou teste como evidencia
- pede apoio documental quando a mudanca exigir pagina ou ADR

### `ai-developer-powershell`

- implementa codigo PowerShell
- registra progresso, compatibilidade e achados no `Jira`
- anexa dry-run, log ou saida de `Pester`
- referencia runbook operacional quando necessario

### `ai-developer-automation`

- implementa tasks, workflows e automacoes
- registra risco operacional, rollback e progresso no `Jira`
- anexa logs de CI, validacoes e diffs declarativos
- atualiza runbooks do `Confluence` quando o fluxo mudar

### `ai-developer-config-policy`

- ajusta schemas, contratos e politicas de configuracao
- registra impacto de schema e governanca no `Jira`
- anexa validacao YAML ou artefato declarativo
- atualiza a pagina de schema correspondente no `Confluence`

### `ai-qa`

- executa testes e validacoes
- registra cenarios cobertos, falhas ou sucesso no `Jira`
- anexa logs, screenshots, pipeline ou checklist
- move `Testing -> Review` ou `Testing -> Changes Requested`

### `ai-reviewer`

- revisa implementacao e aderencia ao contrato
- registra feedback ou aprovacao com evidencia no `Jira`
- exige links para `ADR` ou pagina relevante quando aplicavel
- move `Review -> Done` ou `Review -> Changes Requested`

### `ai-devops`

- opera pipelines, infra e automacoes de entrega
- registra risco de ambiente, rollback e progresso no `Jira`
- anexa links de pipeline, ambiente ou runbook
- atualiza paginas operacionais do `Confluence` quando necessario

### `ai-documentation-agent`

- cria e atualiza paginas oficiais no `Confluence`
- garante backlinks `Jira <-> Confluence`
- registra comentario `documentation-link` com prova no `Jira`
- so libera `Done` quando a rastreabilidade estiver completa

### `ai-browser-validator`

- ativa a capacidade por config somente apos estabilizacao da fase base
- prioriza validacao browser-level de `Jira` e `Confluence` quando a rodada
  exigir evidencia visual objetiva
- executa `Playwright` quando a capacidade estiver ativa
- registra resultado no `Jira`
- anexa screenshot, video, trace ou relatorio
- publica evidencia permanente no `Confluence` quando fizer sentido

### `ai-designer`

- registra handoff visual e necessidade de design no `Jira`
- anexa link de `Figma`, wireframe ou guideline
- reflete guideline visual no `Confluence` quando necessario

### `ai-ux-cro-analyst`

- registra impacto de UX/CRO e recomendacoes no `Jira`
- anexa hipoteses, benchmarks ou analise de usabilidade
- reflete recomendacoes permanentes no `Confluence`

### `ai-seo-specialist`

- valida SEO quando a capacidade estiver ativa
- registra auditoria e evidencias no `Jira`
- anexa relatorio tecnico, screenshot ou metrica relevante
- atualiza guideline SEO no `Confluence` quando a regra mudar
