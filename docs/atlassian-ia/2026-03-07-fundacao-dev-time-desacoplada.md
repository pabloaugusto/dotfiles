# Fundacao Dev-Time Desacoplada

- Status: `aprovado-pelo-usuario`
- Data-base: `2026-03-07`
- Contexto relacionado:
  - [`README.md`](README.md)
  - [`2026-03-07-parecer-e-plano-inicial.md`](2026-03-07-parecer-e-plano-inicial.md)
  - [`../../docs/ai-operating-model.md`](../../docs/ai-operating-model.md)

## Diretrizes aprovadas

- a camada de configuracao, secrets refs, contratos e artefatos de
  implementacao/dev nao deve morar em [`df/`](../../app/df/)
- essa camada tambem nao deve depender de [`bootstrap/`](../../app/bootstrap/)
- o repo atual e piloto, mas a fundacao precisa nascer portavel para servir de
  base a futuros projetos
- agentes opcionais, como design, UX/CRO, SEO e browser validation, devem ser
  ativados por configuracao e nao impostos ao fluxo-base
- `Playwright` pode entrar como camada adicional de evidencia quando for util
  validar pela interface que `Jira` e `Confluence` realmente refletiram as
  acoes esperadas
- o desenvolvimento deve seguir em cortes incrementais, com validacao e review
  por unidade entregue

## Implicacao arquitetural

O primeiro corte de implementacao deixa de estender o runtime do bootstrap e
passa a criar uma control plane propria em [`config/ai/`](../../config/ai/).

Essa control plane passa a concentrar:

- configuracao de plataformas
- contratos operacionais
- optionalidade de agentes e capacidades
- futuras politicas de evidencias, browser validation e adapters

## Decisao operacional

`Playwright` entra como capacidade opcional de verificacao final, e nao como
dependencia do nucleo dos adapters. O nucleo deve nascer sobre APIs oficiais;
browser validation so entra quando adicionar evidencia objetiva ao fluxo.
