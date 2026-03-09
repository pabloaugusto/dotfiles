# Atlassian Product Discovery como Intake Opcional

- Status: `aprovado-para-roadmap`
- Data-base: `2026-03-07`
- Contexto relacionado:
  - [`2026-03-07-parecer-e-plano-inicial.md`](2026-03-07-parecer-e-plano-inicial.md)
  - [`2026-03-07-blueprint-ai-product-owner-system.md`](2026-03-07-blueprint-ai-product-owner-system.md)
  - [`../../ROADMAP.md`](../../ROADMAP.md)

## Decisao

- `Atlassian Product Discovery` entra como camada opcional de discovery e
  intake para novas ideias, oportunidades, hipoteses e descobertas de agentes
  ou do proprio `AI Product Owner`
- `Jira` continua como fonte canonica do backlog executavel, do workflow e das
  issues principais
- apenas o `AI Product Owner` promove uma ideia aprovada em `Product Discovery`
  para `Epic`, `Feature`, `Task`, `Bug` ou outro tipo principal no `Jira`

## Papel no modelo operacional

`Product Discovery` nao substitui `Jira`.

Ele atua antes do backlog executavel, como trilha de:

- intake de ideias
- avaliacao de oportunidades
- consolidacao de hipoteses
- priorizacao de descobertas ainda nao refinadas

Fluxo conceitual sugerido:

```text
Agent insight / stakeholder input / PO idea
    -> Atlassian Product Discovery
    -> triagem e discovery
    -> decisao do AI Product Owner
    -> promocao para Jira
    -> execucao no workflow oficial
```

## Regras operacionais

- ideias criadas por outros agentes podem nascer em `Product Discovery` quando
  ainda forem descobertas, hipoteses, propostas ou oportunidades
- se a demanda ja estiver pronta para execucao, ela deve entrar direto no
  `Jira` pelo `AI Product Owner`
- toda promocao de `Product Discovery` para `Jira` deve manter link cruzado
  entre a ideia original e a issue criada
- `Confluence` continua como fonte de documentacao oficial para ADRs, RFCs,
  analises e decisoes consolidadas

## Impacto arquitetural

O plano passa a prever uma terceira abstracao opcional para discovery:

```python
class DiscoveryPlatform:
    def create_idea(...)
    def update_idea(...)
    def add_comment(...)
    def search(...)
    def promote_to_issue(...)
    def link_delivery_issue(...)
```

Implementacao futura sugerida:

- `AtlassianProductDiscoveryAdapter`

## Campos e links sugeridos

Quando a integracao entrar, o fluxo deve prever pelo menos:

- `Discovery Source`
- `Discovery Status`
- `Discovery Link`
- `Hypothesis`
- `Opportunity Score`
- `Promoted Jira Issue`

## Enquadramento no piloto

No piloto deste repo, `Product Discovery` deve entrar como capacidade
configuravel por `control plane`, nao como dependencia obrigatoria do nucleo
`Jira + Confluence + repo`.

Isso preserva o bootstrap da fabrica de software autonoma sem acoplar a
arquitetura a um unico dominio de produto.
