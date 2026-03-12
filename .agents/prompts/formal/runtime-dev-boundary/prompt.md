# Prompt Para Codex - Formalizar a separacao da camada runtime da app e da camada de desenvolvimento do repo

## Missao

Implementar no repo [`dotfiles`](../../../../README.md) a separacao arquitetural
entre:

- a camada runtime da app/workstation, hoje representada principalmente por
  [`bootstrap/`](../../../../bootstrap/) e [`df/`](../../../../df/)
- a camada de desenvolvimento, governanca e suporte do repo

O objetivo desta rodada nao e centralizar toda a configuracao do projeto em
[`config/`](../../../../config/). O objetivo desta rodada e primeiro corrigir a
fronteira arquitetural do repositorio, criando uma camada `app/` explicita para
o runtime. A centralizacao da configuracao da camada de desenvolvimento deve
ficar para a trilha posterior ja rastreada em
[`DOT-209`](https://pabloaugusto.atlassian.net/browse/DOT-209).

## Por que este pack existe

Este pack existe porque o repo ja deixou claro, na pratica, que ha duas
camadas distintas convivendo no mesmo espaco visual:

- runtime da app/workstation, hoje representado principalmente por
  [`bootstrap/`](../../../../bootstrap/) e [`df/`](../../../../df/)
- desenvolvimento, governanca, tooling e suporte do repo

O problema atual nao e so organizacao de pastas. O problema atual e
arquitetural: a fronteira entre runtime e desenvolvimento ainda nao esta
explicitamente refletida na topologia do repositorio.

## Origem imediata e origem normativa

### Origem imediata

Esta frente surgiu da necessidade de preparar corretamente a futura
centralizacao da camada de desenvolvimento em [`config/`](../../../../config/),
sem cometer o erro de consolidar configuracao em cima de uma fronteira
arquitetural ainda confusa.

### Origem normativa

As evidencias versionadas do repo ja apontam essa separacao conceitual:

- [`CONTEXT.md`](../../../../CONTEXT.md) descreve
  [`bootstrap/`](../../../../bootstrap/) e [`df/`](../../../../df/) como
  runtime real do workstation
- [`README.md`](../../../../README.md) diferencia bootstrap, `df`,
  [`config/`](../../../../config/) e
  [`pyproject.toml`](../../../../pyproject.toml)
- [`pyproject.toml`](../../../../pyproject.toml) ja esta corretamente
  posicionado como ownership da toolchain/dev Python

Este pack existe para transformar esse racional em fronteira fisica,
documentada e implementavel.

## Para que este pack serve e o que esperamos resolver

Ao executar este pack, esperamos resolver:

- a ambiguidade entre runtime da app e camada de desenvolvimento
- a leitura confusa de que [`config/`](../../../../config/) poderia absorver
  runtime da app
- a dificuldade de IA, scripts e manutencao humana em distinguir
  provisionamento/workstation de desenvolvimento/governanca
- o risco de centralizar configuracao cedo demais sobre uma arquitetura ainda
  semanticamente errada

## Regra zero

Antes de editar qualquer arquivo versionado:

1. verificar no `Jira` se ja existe issue aberta cobrindo a **implementacao**
   desta separacao arquitetural
2. reutilizar a issue existente se ela ja cobrir o escopo real
3. se nao existir issue suficiente, criar uma `Task` filha do
   [`DOT-71`](https://pabloaugusto.atlassian.net/browse/DOT-71)
4. nao reutilizar [`DOT-209`](https://pabloaugusto.atlassian.net/browse/DOT-209)
   para esta rodada, porque `DOT-209` ficou reservada para a etapa seguinte:
   centralizar a configuracao da camada de desenvolvimento em
   [`config/`](../../../../config/)
5. nao criar `Epic` novo
6. manter a rodada isolada em branch e worktree proprios, sem piggyback em WIP
   ativo de outro tema

## Evidencias versionadas obrigatorias

Use como evidencias minimas:

- [`CONTEXT.md`](../../../../CONTEXT.md) ja descreve
  [`bootstrap/`](../../../../bootstrap/) e [`df/`](../../../../df/) como
  runtime real do workstation
- [`README.md`](../../../../README.md) ja diferencia bootstrap, `df`,
  [`config/`](../../../../config/) e
  [`pyproject.toml`](../../../../pyproject.toml)
- [`pyproject.toml`](../../../../pyproject.toml) ja concentra toolchain,
  dependencias, lint, testes e configuracao de desenvolvimento nao-runtime
- [`bootstrap/README.md`](../../../../bootstrap/README.md) e
  [`docs/bootstrap-flow.md`](../../../../docs/bootstrap-flow.md) comprovam que a
  camada bootstrap e runtime/provisionamento, nao infraestrutura abstrata de
  desenvolvimento
- [`docs/config-reference.md`](../../../../docs/config-reference.md) mostra que
  parte importante da configuracao atual ainda esta acoplada ao runtime do
  bootstrap, o que reforca a necessidade de corrigir a fronteira antes da
  consolidacao futura de config dev

## Decisao arquitetural obrigatoria

Ao final da implementacao, o repo deve deixar explicito que:

- [`pyproject.toml`](../../../../pyproject.toml) continua dono da toolchain
  Python, dependencias, lint, testes e configuracao de desenvolvimento
  nao-runtime
- runtime da app/workstation nao pertence ao eixo
  [`config/`](../../../../config/) + [`pyproject.toml`](../../../../pyproject.toml)
- runtime deve morar em `app/`
- [`config/`](../../../../config/) deve permanecer reservado para configuracao
  da camada de desenvolvimento, suporte, control plane e governanca

## Estrutura alvo

Implementar a seguinte topologia:

```text
app/
  bootstrap/
  df/
config/
  ...
pyproject.toml
```

Resultado esperado da fronteira:

- `app/bootstrap/` concentra entrypoints, parser de config do bootstrap,
  scripts de provisionamento e artefatos ligados ao runtime da app
- `app/df/` concentra os dotfiles e assets que vao para a maquina
- [`config/`](../../../../config/) deixa de competir semanticamente com o
  runtime da app
- [`pyproject.toml`](../../../../pyproject.toml) preserva suas atribuicoes
  atuais

## Fora de escopo desta rodada

- centralizar a configuracao da camada de desenvolvimento em um arquivo
  principal dentro de [`config/`](../../../../config/)
- redesenhar toda a arvore [`config/ai/`](../../../../config/ai/)
- mover segredos reais para Git
- reescrever a toolchain de qualidade do repo
- deslocar para [`pyproject.toml`](../../../../pyproject.toml) algo que hoje ja
  e runtime da app

## Ondas de implementacao

### 1. Formalizar a fronteira em contratos e docs

- atualizar os contratos e docs que descrevem a arquitetura do repo
- explicar de forma perene que `app/` e runtime
- explicar de forma perene que [`config/`](../../../../config/) e camada de
  desenvolvimento/suporte
- explicar de forma perene que
  [`pyproject.toml`](../../../../pyproject.toml) continua como ownership da
  toolchain Python

### 2. Introduzir `app/`

- criar `app/`
- mover [`bootstrap/`](../../../../bootstrap/) para `app/bootstrap/`
- mover [`df/`](../../../../df/) para `app/df/`
- manter compatibilidade temporaria somente quando realmente necessaria para
  nao quebrar bootstrap, tests e automacoes no meio da rodada

### 3. Atualizar todos os consumidores da camada runtime

- [`Taskfile.yml`](../../../../Taskfile.yml)
- scripts Python, PowerShell e shell
- docs e catalogos
- validadores
- startup e governanca quando houver referencia estrutural a runtime
- harnesses e testes de bootstrap, relink, `checkEnv` e sincronismo

### 4. Validar a nova fronteira

- garantir que runtime deixou de ficar solto na raiz
- garantir que [`config/`](../../../../config/) nao virou deposito de runtime
- garantir que [`pyproject.toml`](../../../../pyproject.toml) nao perdeu
  atribuicoes
- garantir paridade Windows/WSL
- garantir idempotencia de bootstrap e relink

### 5. Fechar a rodada sem deixar delta conceitual

- remover compatibilidades temporarias desnecessarias
- atualizar referencias remanescentes
- fechar docs e validadores em paridade com a nova topologia
- registrar explicitamente que a proxima etapa arquitetural e
  [`DOT-209`](https://pabloaugusto.atlassian.net/browse/DOT-209)

## Arquivos e areas provaveis de impacto

- [`CONTEXT.md`](../../../../CONTEXT.md)
- [`README.md`](../../../../README.md)
- [`AGENTS.md`](../../../../AGENTS.md)
- [`Taskfile.yml`](../../../../Taskfile.yml)
- [`bootstrap/`](../../../../bootstrap/)
- [`df/`](../../../../df/)
- [`docs/bootstrap-flow.md`](../../../../docs/bootstrap-flow.md)
- [`docs/config-reference.md`](../../../../docs/config-reference.md)
- [`docs/ai-operating-model.md`](../../../../docs/ai-operating-model.md)
- [`scripts/`](../../../../scripts/)
- [`tests/`](../../../../tests/)

## Criterios de aceite

1. o repo passa a ter uma camada `app/` explicita para runtime
2. [`bootstrap/`](../../../../bootstrap/) e [`df/`](../../../../df/) deixam de
   ficar soltos na raiz
3. [`config/`](../../../../config/) nao recebe runtime da app nesta rodada
4. [`pyproject.toml`](../../../../pyproject.toml) preserva integralmente o papel
   de toolchain e desenvolvimento nao-runtime
5. tasks, scripts, docs, startup e testes passam a apontar para `app/bootstrap`
   e `app/df`
6. a fronteira runtime vs desenvolvimento fica explicitamente documentada
7. a proxima etapa de centralizacao da camada de desenvolvimento permanece
   rastreada por [`DOT-209`](https://pabloaugusto.atlassian.net/browse/DOT-209)

## Validacoes minimas esperadas

- `task ai:worklog:check PENDING_ACTION=concluir_primeiro`
- `task ai:validate`
- `task docs:check`
- `task ai:eval:smoke`
- validacoes e testes de bootstrap, relink e `checkEnv` cabiveis
- harnesses Windows e WSL cabiveis para a fatia

## Instrucao final

Implemente esta separacao por ondas pequenas, com barra alta de resiliencia e
sem improvisar atalhos conceituais.

- nao misture runtime da app com configuracao de desenvolvimento
- nao use [`config/`](../../../../config/) como deposito generico
- nao retire do [`pyproject.toml`](../../../../pyproject.toml) responsabilidades
  que ja sao legitimamente dele
- nao abra `Epic` novo
- nao deixe a etapa seguinte de centralizacao da camada de desenvolvimento
  acoplada a esta rodada
