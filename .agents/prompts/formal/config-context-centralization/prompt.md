# PROMPT PARA CODEX -- FORMALIZAR CONCENTRACAO DE CONFIGS POR CONTEXTO

## NATUREZA DESTA INICIATIVA

Esta rodada deve apenas:

- formalizar o pack
- endurecer o escopo
- fixar o contrato de arquitetura
- preparar a futura execucao

Esta rodada nao deve:

- executar a migracao funcional
- misturar este tema com outra entrega em andamento
- absorver esta trilha em issue funcional previa
- tratar [DOT-209](https://pabloaugusto.atlassian.net/browse/DOT-209) ou
  [DOT-210](https://pabloaugusto.atlassian.net/browse/DOT-210) como dono deste
  pack
- usar [pyproject.toml](../../../../pyproject.toml) como hub generico de
  configuracao

A execucao futura desta iniciativa deve acontecer em task propria, apartada,
com branch, worklog, review e validacao proprios.

---

## TITULO RECOMENDADO DA FUTURA TASK JIRA DE EXECUCAO

**PROMPT: Formalizar concentracao de configs por contexto**

### Observacao importante sobre rastreabilidade

- a task de prompt e propria:
  [DOT-217](https://pabloaugusto.atlassian.net/browse/DOT-217)
- a task de implementacao futura deve ser propria
- [DOT-209](https://pabloaugusto.atlassian.net/browse/DOT-209) e
  [DOT-210](https://pabloaugusto.atlassian.net/browse/DOT-210) podem ser
  referencias relacionadas, nao owner deste pack
- o pack nao substitui o work item funcional que vier a executar a migracao

---

## BRANCH NAMING RECOMENDADO

Quando a execucao futura desta trilha realmente comecar, usar o padrao
canonico do repo para prompt packs:

`prompt/<jira-key>-config-context-centralization`

Sugestoes de slug curto:

- `config-context-centralization`
- `context-config-foundation`
- `config-context-boundary`

---

# 1. CONTEXTO E OBJETIVO

O repo [`dotfiles`](../../../../README.md) hoje carrega configuracoes espalhadas
entre varias superfices e formatos, com concentracao de drift principalmente na
camada de IA:

- [config/ai/](../../../../config/ai/)
- [`.agents/config.toml`](../../../config.toml)
- docs e contratos que repetem valores configuraveis
- scripts e validadores que ainda podem depender de literals repetidos

A realidade pos-migracao do repo agora e:

- [app/](../../../../app/) representa o runtime do produto dotfiles
- [config/](../../../../config/) representa a camada de desenvolvimento,
  integracoes de dev e defaults globais do projeto
- [`.agents/`](../../../) representa a camada declarativa da IA

O objetivo deste pack e formalizar uma arquitetura com tres raizes canonicas:

- [config/](../../../../config/) para dev, integracoes de dev e defaults globais
- a futura pasta `config` sob [app/](../../../../app/) para runtime
- a futura pasta `config` sob [`.agents/`](../../../) para configuracao
  declarativa da IA

Esta iniciativa deve tambem formalizar a drenagem de literais/configs
espalhados para config canonica, com referencia obrigatoria por
`arquivo::chave`, e elevar o futuro `config.toml` dentro de
[config/](../../../../config/) ao papel de hub global de regionalizacao.

---

# 2. REFERENCIAS RELACIONADAS, SEM FUNDIR ESCOPO

Este pack pode consumir como referencia informacional:

- [`startup-alignment`](../startup-alignment/prompt.md)
- [`runtime-dev-boundary`](../runtime-dev-boundary/prompt.md)
- [`agents-rules-centralization`](../agents-rules-centralization/prompt.md)
- [`documentation-layer-governance`](../documentation-layer-governance/prompt.md)
- [`time-locale-governance`](../time-locale-governance/prompt.md)

Regra importante:

- essas referencias sao insumos de analise e compatibilidade
- este pack deve manter issue, branch e execucao futura proprias
- nao executar esta consolidacao "de carona" em outra trilha

---

# 3. REGRA ZERO

Antes de qualquer execucao funcional futura:

1. executar o startup oficial do repo quando houver risco de retomada sem
   continuidade confiavel
2. executar o preflight de WIP e worklog
3. respeitar a regra de concluir ou destravar primeiro o trabalho ja ativo
4. tratar o Jira como fonte primaria do fluxo vivo
5. verificar issue aberta existente e epic aderente antes de criar nova demanda
6. como a trilha toca [`.agents/prompts/`](../../README.md), usar namespace
   `prompt`, titulo `PROMPT:` e label `prompt`

---

# 4. DEPENDENCIAS E ORDEM SEGURA

## prerequisite packs

- nenhum

## preflight packs

- [`startup-alignment`](../startup-alignment/prompt.md)
- [`runtime-dev-boundary`](../runtime-dev-boundary/prompt.md)
- [`agents-rules-centralization`](../agents-rules-centralization/prompt.md)
- [`documentation-layer-governance`](../documentation-layer-governance/prompt.md)
- [`time-locale-governance`](../time-locale-governance/prompt.md)

## Ordem segura

1. carregar startup e preflight da sessao
2. checar os packs listados acima
3. formalizar o contrato deste pack
4. so depois abrir a task funcional de execucao

---

# 5. PROBLEMA REAL

Hoje o repo sofre com configuracao pulverizada por contexto e por superficie.
Os sintomas mais evidentes sao:

- valores configuraveis repetidos entre docs, rules, contracts e runtime
- camada de IA espalhada entre [config/ai/](../../../../config/ai/) e
  [`.agents/config.toml`](../../../config.toml)
- falta de uma convencao unica para apontar a source of truth de cada valor
- risco de drift entre texto humano e valor configurado
- ambiguidade sobre onde ler defaults globais, especialmente para locale,
  idioma, moeda, timezone e calendario

O problema nao e apenas organizacao de pastas. O problema e discoverability,
manutenabilidade, ambiguidade e drift operacional.

---

# 6. PRINCIPIO CENTRAL DA SOLUCAO

A solucao correta e concentrar configuracao por contexto, sem transformar uma
unica pasta em deposito universal.

Regra central:

- [config/](../../../../config/) concentra dev, integracoes de dev e defaults
  globais do projeto
- a futura pasta `config` sob [app/](../../../../app/) concentra runtime
- a futura pasta `config` sob [`.agents/`](../../../) concentra a camada
  declarativa da IA
- [pyproject.toml](../../../../pyproject.toml) permanece exclusivo da toolchain
  Python

Complemento obrigatorio:

- valores configuraveis saem de prose e vao para config canonica
- docs, rules e contracts passam a apontar para config em vez de repetir
  literals

---

# 7. TOPOLOGIA ALVO POR CONTEXTO

Usar como alvo inicial:

- na raiz [config/](../../../../config/):
  `config.toml`, `dev.toml`, `integrations.toml`, `quality.toml` e
  `time-surfaces.yaml`
- na futura pasta `config` sob [app/](../../../../app/):
  `config.toml`, `runtime.toml`, `bootstrap.toml` e `links.toml`
- na futura pasta `config` sob [`.agents/`](../../../):
  `config.toml`, `agents.toml`, `communication.toml`, `startup.toml`,
  `orchestration.toml`, `reviews.toml` e `prompts.toml`

Regra:

- novos arquivos de dominio so nascem com motivo arquitetural claro
- o primeiro corte deve priorizar concentracao e nao fragmentacao excessiva

---

# 8. REGRA DE CLASSIFICACAO DE CONFIGURACOES

Classificacao obrigatoria:

- se responde como a IA opera, inicia, se identifica, delega, valida, roteia
  ou publica, vai para a futura pasta `config` sob [`.agents/`](../../../)
- se responde como o repo de desenvolvimento integra ferramentas, auth,
  qualidade, plataformas e defaults globais, vai para
  [config/](../../../../config/)
- se responde como o dotfiles instala, linka, provisiona e materializa assets
  no workstation, vai para a futura pasta `config` sob [app/](../../../../app/)
- se responde como o ecossistema Python do repo compila, testa, tipa ou
  empacota, fica em [pyproject.toml](../../../../pyproject.toml)

---

# 9. ROOT DO ARQUIVO CANONICO DE REGIONALIZACAO

O futuro `config.toml` dentro de [config/](../../../../config/) deve ser a
fonte global padrao de:

- locale
- idioma
- moeda
- calendario
- timezone
- formatos humanos
- politica de heranca cross-layer

O futuro `time-surfaces.yaml` dentro de [config/](../../../../config/)
permanece como registry complementar de superficies temporais.

Regra:

- `root config` e a source of truth default
- a futura pasta `config` sob [app/](../../../../app/) e a futura pasta
  `config` sob [`.agents/`](../../../) podem ter overlays quando houver
  justificativa legitima
- overlays nunca substituem o root global como default canonico

---

# 10. REGRA DE DRENAGEM DE LITERAIS/CONFIGS ESPALHADOS

Toda definicao encontrada em docs, rules, contracts, comentarios, templates ou
scripts deve ser classificada em:

- `valor canonico de config`
- `invariante normativa`
- `explicacao derivada`

Regras:

- valores mutaveis, defaults, mappings, formatos, aliases, surfaces e policies
  de heranca devem migrar para config
- obrigacoes normativas continuam em docs, rules e contracts
- textos humanos deixam de carregar o literal e passam a apontar para a config
  canonica

---

# 11. CONVENCAO `arquivo::chave`

Padrao obrigatorio do repo:

- docs, rules e contracts que mencionarem valor configuravel devem apontar para
  a config canonica em formato `arquivo::chave`
- fontes humanas devem ganhar secao `Config canonica`
- arquivos estruturados que apontarem para outra config devem usar `config_ref`

Exigencia minima:

- `arquivo`
- `chaves`
- `regra de leitura`
- indicacao explicita de que a fonte humana nao e source of truth do literal

---

# 12. BIBLIOTECA UNICA DE CONFIG RESOLUTION

A futura execucao deve criar uma biblioteca unica de resolution de config para:

- root config
- app config
- agents config
- referencias `arquivo::chave`
- precedencia e overlays

Regra dura:

- nenhum script pode criar loader paralelo quando existir resolvedor oficial
- startup, validadores e runtime devem consumir a mesma biblioteca

---

# 13. SCHEMAS POR CONTEXTO

Toda config TOML interna deve ter schema por contexto:

- schema do root config
- schema do app config
- schema da IA config

Esses schemas devem validar:

- chaves obrigatorias
- tipos
- enums
- ownership por contexto
- referencias `arquivo::chave`
- overlays permitidos

---

# 14. TABELAS DOCUMENTAIS GERADAS DA CONFIG CANONICA

Docs que espelham configuracao devem ser gerados a partir da config canonica,
nao editados manualmente.

Escopo inicial obrigatorio:

- aliases e nomes visiveis de agentes
- formatos visiveis de chat
- roots e precedencia por contexto
- defaults de regionalizacao
- mappings declarativos repetidos em catalogos e docs

`docs:check` e `ai:validate` devem falhar quando essas tabelas ficarem stale.

---

# 15. LINT DE LITERAL PROIBIDO FORA DA CONFIG

Criar lint estrutural para impedir a reintroducao de valores governados fora da
config canonica.

Escopo inicial:

- formato de prefixo de chat
- fallback order de nome visivel
- defaults de regionalizacao
- nomes visiveis governados de agentes e papeis
- campos Jira configurados e classificados como `config-managed`

O lint deve apontar a chave canonica que deveria ter sido referenciada.

---

# 16. MATRIZ VERSIONADA `origem -> destino -> justificativa -> owner -> status`

A execucao futura deve manter uma matriz versionada obrigatoria contendo:

- origem
- destino
- justificativa
- owner
- status
- tipo
- observacoes de compatibilidade

Essa matriz e o artefato de controle da drenagem e nao e opcional.

---

# 17. ONDAS DE IMPLEMENTACAO

1. criar os tres `config.toml` raiz e a biblioteca unica de resolution
2. definir schemas por contexto e a convencao `arquivo::chave`
3. criar a matriz versionada de migracao
4. migrar primeiro a camada de IA
5. consolidar a regionalizacao global no root config
6. reescrever rules/docs para apontarem para config
7. introduzir tabelas geradas e bloquear stale state
8. introduzir lint de literal proibido e validadores anti-drift
9. drenar caminhos legados somente depois que consumers, docs e testes
   apontarem para a nova fonte canonica

---

# 18. CRITERIOS DE ACEITE

Esta iniciativa so estara correta se:

1. existirem tres entrypoints canonicos por contexto
2. o futuro `config.toml` dentro de [config/](../../../../config/) for o hub
   global de regionalizacao
3. a camada de IA convergir para a futura pasta `config` sob [`.agents/`](../../../)
4. [pyproject.toml](../../../../pyproject.toml) permanecer exclusivo da
   toolchain Python
5. docs, rules e contracts apontarem para config em vez de repetir literals
6. a biblioteca unica de config resolution bloquear loaders paralelos
7. schemas por contexto validarem ownership, tipos e refs
8. tabelas documentais derivadas ficarem sob enforcement
9. o lint de literal proibido impedir regressao
10. a matriz de migracao rastrear a drenagem fim a fim

---

# 19. VALIDACAO MINIMA

Na execucao futura, rodar no minimo:

- `task ai:validate`
- `task docs:check`
- `task ai:eval:smoke`
- `task ai:prompts:jira:check`
- `python scripts/validate-ai-assets.py`
- suites Python de startup, validators e config resolution
- checks de bootstrap/runtime quando a fatia tocar
  a futura pasta `config` sob [app/](../../../../app/)

---

# 20. FORMA DE TRABALHO

- nao parar em analise
- nao entregar apenas organizacao cosmetica de pastas
- nao transformar regra normativa em knob desnecessario
- nao criar tres mini-caos em vez de concentracao por contexto
- nao manter caminhos legados como source of truth depois da drenagem
- nao usar [pyproject.toml](../../../../pyproject.toml) como atalho de
  configuracao generica

---

# 21. SAIDA FINAL ESPERADA

Ao final da execucao futura, entregar:

- tres raizes canonicas de config por contexto
- root config como hub global de regionalizacao
- convenao `arquivo::chave` em uso real
- biblioteca unica de resolution
- schemas por contexto
- tabelas documentais geradas
- lint de literal proibido
- matriz versionada de migracao
- docs, rules, contracts e runtime em paridade com a nova source of truth
