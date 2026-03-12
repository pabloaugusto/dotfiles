# Analise da Fronteira `/app` para Runtime

- Status: `analise-concluida`
- Data-base: `2026-03-08`
- Relacionados:
  - [`2026-03-07-parecer-e-plano-inicial.md`](2026-03-07-parecer-e-plano-inicial.md)
  - [`../../CONTEXT.md`](../../CONTEXT.md)
  - [`../../docs/bootstrap-flow.md`](../../docs/bootstrap-flow.md)
  - [`../../docs/user-home-structure.md`](../../docs/user-home-structure.md)
  - [`../../Taskfile.yml`](../../Taskfile.yml)

## Objetivo

Avaliar se criar uma pasta [`/app`](../../) para concentrar o runtime
materializado do piloto melhora a separacao entre:

- a fabrica automatizada de software orientada por IA
- o aplicativo efetivamente desenvolvido dentro deste repo

## Resumo da recomendacao

Recomendacao inicial:

- `sim` para a direcao arquitetural
- `nao` para uma migracao fisica imediata nesta v1

O repo ainda tem acoplamento estrutural demais com os nomes [`df/`](../../app/df/)
e [`bootstrap/`](../../app/bootstrap/). Mover isso agora para [`/app`](../../)
traria custo alto e risco real de regressao em bootstrap, relink, docs, tests e
integracoes criticas.

O caminho mais seguro e faseado:

1. introduzir a fronteira conceitual de runtime
2. parametrizar paths e contratos hoje hardcoded
3. migrar consumidores
4. so depois decidir o move fisico para [`/app`](../../)

## Mapa de acoplamento observado

Contagem objetiva desta rodada:

- [`../../Taskfile.yml`](../../Taskfile.yml): `12` referencias a
  [`df/`](../../app/df/) e `8` referencias a [`bootstrap/`](../../app/bootstrap/)
- [`../../bootstrap/`](../../app/bootstrap/): `34` referencias diretas a
  [`df/`](../../app/df/)
- [`../../scripts/`](../../scripts/): `4` referencias diretas a
  [`df/`](../../app/df/)
- [`../../tests/`](../../tests/): `7` referencias diretas a [`df/`](../../app/df/)
- [`../../docs/`](../../docs/): `62` referencias a [`df/`](../../app/df/) e `45` a
  [`bootstrap/`](../../app/bootstrap/)

Superficies mais sensiveis:

- bootstrap Windows e WSL
- `Taskfile` e funcoes de sync/checkEnv
- harnesses de integracao e Docker
- docs que descrevem a home final e os links materializados
- refs de secrets, signer Git e integracoes criticas

## O que uma pasta `/app` resolveria

- deixaria mais explicita a separacao entre control plane e runtime do piloto
- prepararia o repo para virar template/base da fabrica automatizada
- reduziria a leitura equivocada de que tudo no repo pertence ao runtime do
  dotfiles

## O que uma pasta `/app` quebraria hoje

Se o move fisico fosse feito agora, o impacto mais provavel estaria em:

- links criados pelo bootstrap para `HOME`
- scripts PowerShell e Bash que assumem [`df/`](../../app/df/) como raiz
  materializada
- testes de integracao que validam alvos exatos em [`df/`](../../app/df/)
- documentacao operacional e diagramas de home structure
- [`../../Dockerfile`](../../Dockerfile) e harnesses que assumem workdir dentro
  de [`df/`](../../app/df/)
- lookup de refs em [`../../df/secrets/secrets-ref.yaml`](../../app/df/secrets/secrets-ref.yaml)

## Estrategia recomendada

### Fase A. Nomear a fronteira sem mover

- declarar em contrato que o runtime materializado e uma categoria separada do
  control plane
- introduzir o conceito `runtime_root` na camada
  [`../../config/`](../../config/) e dev-time antes de qualquer move fisico
- revisar scripts e tasks para reduzir dependencias de path literal

### Fase B. Criar camada de compatibilidade

- ensinar bootstrap, tests e docs a consumirem `runtime_root`
- manter aliases ou ponte temporaria para [`df/`](../../app/df/) durante a
  transicao
- impedir breakage em Windows host e Ubuntu WSL

### Fase C. Decidir o layout fisico

Opcoes realistas:

- [`app/`](../../app/) como container do runtime materializado
- um subdiretorio `runtime` dentro de [`app/`](../../app/) para deixar a intencao ainda mais explicita

Opcao que hoje parece mais segura:

- manter [`bootstrap/`](../../app/bootstrap/) fora de [`/app`](../../)
- mover apenas o runtime materializado de [`df/`](../../app/df/) para um novo root quando a
  camada de compatibilidade estiver pronta

## Decisao preliminar

No estado atual do repo:

- nao recomendo renomear [`df/`](../../app/df/) para [`app/`](../../) de imediato
- recomendo colocar isso como trilha de maturidade da arquitetura portavel
- recomendo que a primeira entrega concreta seja reduzir o acoplamento por
  path, nao mover pasta

## Criterios para promover a mudanca

A migracao fisica so deve ser considerada quando:

- [`bootstrap/`](../../app/bootstrap/) nao depender mais de [`df/`](../../app/df/)
  hardcoded
- `Taskfile`, tests e scripts aceitarem um `runtime_root` canonico
- docs principais puderem ser atualizadas sem ambiguidade
- a paridade Windows/WSL estiver coberta por harness de regressao

## Proximo passo recomendado

- considerar [`DOT-76`](https://pabloaugusto.atlassian.net/browse/DOT-76) como
  analise concluida em `Done`
- transformar esta recomendacao em plano faseado de desacoplamento por path sob
  o epic [`DOT-74`](https://pabloaugusto.atlassian.net/browse/DOT-74)
- so abrir implementacao quando o custo de migracao estiver quebrado em
  stories e subtasks pequenas, com `runtime_root` como primeiro corte
