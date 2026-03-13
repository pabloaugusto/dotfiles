# Plano Aprovado -- Concentracao De Configs Por Contexto

## Resumo executivo

O repo deve concentrar configuracao por contexto em tres raizes canonicas:

- [config/](../../../../config/) para dev, integracoes de dev e defaults
  globais do projeto
- a futura pasta `config` sob [app/](../../../../app/) para runtime do produto
  dotfiles
- a futura pasta `config` sob [`.agents/`](../../../) para a camada
  declarativa da IA

O foco principal e drenar a pulverizacao atual da camada de IA, hoje espalhada
entre [config/ai/](../../../../config/ai/) e
[`.agents/config.toml`](../../../config.toml), e mover valores configuraveis
que ainda vivem em prose para a config canonica.

## Topologia alvo

```text
config/
  config.toml
  dev.toml
  integrations.toml
  quality.toml
  time-surfaces.yaml

app/config/
  config.toml
  runtime.toml
  bootstrap.toml
  links.toml

.agents/config/
  config.toml
  agents.toml
  communication.toml
  startup.toml
  orchestration.toml
  reviews.toml
  prompts.toml

pyproject.toml
```

## Ownership por contexto

- [config/](../../../../config/) concentra configuracao de desenvolvimento,
  integracoes de dev e defaults globais do projeto
- a futura pasta `config` sob [app/](../../../../app/) concentra configuracao
  de runtime
- a futura pasta `config` sob [`.agents/`](../../../) concentra configuracao
  declarativa da IA
- [pyproject.toml](../../../../pyproject.toml) permanece exclusivo da toolchain
  Python

## Regra de classificacao

- configuracao de IA vai para a futura pasta `config` sob [`.agents/`](../../../)
- configuracao de dev e integracoes de dev vai para
  [config/](../../../../config/)
- configuracao de runtime vai para a futura pasta `config` sob
  [app/](../../../../app/)
- configuracao da toolchain Python fica em
  [pyproject.toml](../../../../pyproject.toml)

## Root regionalization hub

O arquivo futuro `config.toml` dentro de [config/](../../../../config/) deve
ser o hub global do projeto para:

- locale
- idioma
- moeda
- calendario
- timezone
- formatos humanos
- politica de heranca cross-layer

O arquivo futuro `time-surfaces.yaml` dentro de [config/](../../../../config/)
permanece como registry complementar por superficie temporal.

## Convencao `arquivo::chave`

Valores configuraveis passam a ser referenciados por `arquivo::chave`.

Regras:

- docs, rules e contracts deixam de repetir literals configuraveis
- cada fonte humana deve apontar explicitamente para a config canonica
- referencias estruturadas entre configs usam `config_ref`

## Drenagem de literais/configs espalhados

Cada definicao encontrada no repo deve ser classificada em:

- `valor canonico de config`
- `invariante normativa`
- `explicacao derivada`

Valores mutaveis, defaults, mappings, aliases, formatos e policies de heranca
devem migrar para config canonica.

## Hardeners obrigatorios

- biblioteca unica de config resolution
- schemas por contexto para configs TOML internas
- tabelas documentais geradas automaticamente da config canonica
- lint de `literal proibido fora da config`
- matriz versionada de migracao
- validadores anti-drift

## Matriz de migracao resumida

Primeira drenagem obrigatoria:

- [config/ai/agents.yaml](../../../../config/ai/agents.yaml),
  [config/ai/agent-enablement.yaml](../../../../config/ai/agent-enablement.yaml)
  e
  [config/ai/agent-runtime.yaml](../../../../config/ai/agent-runtime.yaml)
  convergem para o futuro `agents.toml` na pasta `config` sob
  [`.agents/`](../../../)
- contratos de chat, startup e orchestration migram para:
  - o futuro `communication.toml` na pasta `config` sob [`.agents/`](../../../)
  - o futuro `startup.toml` na pasta `config` sob [`.agents/`](../../../)
  - o futuro `orchestration.toml` na pasta `config` sob [`.agents/`](../../../)
- reviewer policies migram para
  o futuro `reviews.toml` na pasta `config` sob [`.agents/`](../../../)
- [config/ai/platforms.yaml](../../../../config/ai/platforms.yaml),
  [config/ai/jira-model.yaml](../../../../config/ai/jira-model.yaml),
  [config/ai/confluence-model.yaml](../../../../config/ai/confluence-model.yaml)
  e [config/ai/sync-targets.yaml](../../../../config/ai/sync-targets.yaml)
  permanecem no contexto dev em [config/](../../../../config/)
- [`.agents/config.toml`](../../../config.toml) vira ponte temporaria para
  o futuro `config.toml` na pasta `config` sob [`.agents/`](../../../)

## Criterios de aceite

- tres entrypoints canonicos de config por contexto
- root config como hub global de regionalizacao
- camada de IA concentrada na futura pasta `config` sob [`.agents/`](../../../)
- [pyproject.toml](../../../../pyproject.toml) preservado como toolchain Python
- docs e rules apontando para config em vez de repetir literals
- resolvedor unico, schemas, tabelas geradas, lint e matriz versionada sob
  enforcement

## Riscos residuais e oportunidades

Riscos residuais:

- trocar um caos por tres mini-caos se a fragmentacao por dominio for precoce
- manter caminhos legados vivos por tempo demais
- transformar regra normativa em knob indevido
- permitir excecoes demais no lint e esvaziar o enforcement

Oportunidades:

- gerar catalogos e tabelas diretamente da config canonica
- unificar a resolution de config em toda a stack do repo
- reduzir ambiguidade cross-layer, sobretudo na camada de IA
- preparar o repo para futuras migracoes de config com menor custo de drift
