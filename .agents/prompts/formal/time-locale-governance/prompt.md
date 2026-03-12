# PROMPT PARA CODEX -- FORMALIZAR GOVERNANCA TEMPORAL, TIMEZONE, LOCALE E REGIONALIZACAO

## NATUREZA DESTA INICIATIVA

Esta rodada deve apenas:

- formalizar o prompt
- endurecer o escopo
- explicitar contratos
- preparar a futura implementacao

Esta rodada nao deve:

- executar a implementacao
- abrir PR de execucao tecnica
- misturar este tema com outra entrega em andamento
- absorver este escopo em branch, issue ou task de outro assunto
- fazer migracao temporal parcial "aproveitando" outra trilha

A execucao desta iniciativa deve acontecer depois, via task nova, apartada e
propria, podendo citar outras demandas apenas como referencia, dependencia
informacional, analise comparativa ou rastreabilidade cruzada.

---

## TITULO RECOMENDADO DA FUTURA TASK NO JIRA

**PROMPT: Formalizar governanca temporal, timezone, locale e regionalizacao**

### Observacao importante sobre rastreabilidade

- a task de prompt deve ser propria
- a task de implementacao deve ser propria
- se houver issue funcional ja existente cobrindo parte do problema de datas,
  horas, locale ou timezone, ela pode ser usada como referencia relacionada
- essa issue funcional nao deve absorver automaticamente a formalizacao do pack
  de prompt, nem o pack deve substituir o work item funcional

---

## BRANCH NAMING RECOMENDADO PARA A EXECUCAO FUTURA

Quando a execucao desta trilha realmente comecar, usar o padrao canonico do
repo para prompt packs:

`prompt/<jira-key>-time-locale-governance`

Sugestoes de slug curto:

- `time-locale-governance`
- `temporal-governance`
- `time-locale-normalization`

---

# 1. CONTEXTO E OBJETIVO

Este repositorio ja possui uma malha real de governanca de IA, com:

- `Jira` como fonte primaria do fluxo vivo
- `Confluence` como superficie cross-surface
- docs versionadas no repo
- startup e restart oficiais
- worklog e ledgers vivos
- tasks e validators
- reviewers especializados
- control plane declarativa
- prompt packs formais
- governanca documental em evolucao
- fundacao formal de sync, outbox e fonte perene

O objetivo desta iniciativa nao e fazer um ajuste cosmetico de formatacao de
datas.

O objetivo correto e formalizar e depois implementar, de ponta a ponta, a
correcao definitiva, perene, retroativa e auditavel da camada de:

- data
- hora
- timezone
- locale
- regionalizacao
- exibicao temporal
- serializacao temporal
- tokens temporais tecnicos
- contratos e exemplos que ensinam o comportamento temporal correto

Esta entrega precisa eliminar drift em:

- chat gerado e controlado pelo repo
- startup
- restart
- resumos operacionais
- worklog
- ledgers
- logs versionados
- artefatos gerados
- docs
- comentarios
- docstrings
- templates
- contratos declarativos
- prompts
- cards
- skills
- workflows
- tasks
- validadores
- testes

Esta entrega nao pode parar em analise.
Ela deve resolver a causa raiz, formalizar o contrato correto, materializar
enforcement real e bloquear regressao futura por design.

---

# 2. REFERENCIAS RELACIONADAS, MAS SEM FUNDIR ESCOPO

Esta iniciativa pode referenciar, para consulta e analise, itens relacionados do
repo, mas nao deve absorver escopo deles nem ser absorvida por eles sem decisao
formal especifica.

Referencias provaveis:

- `startup-alignment`
- `sync-outbox-foundation`
- `documentation-layer-governance`
- issue funcional existente para locale, dates ou timezone, se houver
- backlog, roadmap, auditorias e findings relacionados a datas, horas,
  timezone e idioma

## Regra importante

- estas referencias sao insumos de analise e dependencia informacional
- esta iniciativa deve ter sua propria trilha de execucao quando for rodada
- nao executar "de carona" em outro prompt pack ou issue funcional ja em curso

---

# 3. REGRA ZERO

Antes de qualquer mudanca relevante na futura execucao:

1. executar o startup oficial do repositorio, se existir
2. executar o preflight oficial de WIP, worklog e continuidade, se existir
3. respeitar a regra de concluir ou destravar primeiro o trabalho ja ativo
4. usar a ferramenta primaria de rastreabilidade do projeto como fonte de
   verdade do fluxo vivo
5. antes de criar nova demanda, executar dedupe e reaproveitamento do
   agrupador pai adequado, se o projeto usar esse modelo
6. identificar backlog, roadmap, issue, card ou demanda ja existente para este
   tema e reutilizar a trilha oficial quando ela ja cobrir o escopo
7. carregar as skills, guias, contratos e reviewers mais proximos do escopo
8. acionar revisores especializados por familia de arquivo afetada
9. como este escopo toca texto versionado, docs, comentarios e docstrings,
   acionar tambem a revisao ortografica consultiva, se existir

---

# 4. DEPENDENCIAS E ORDEM SEGURA DE EXECUCAO

Esta iniciativa e transversal e nao deve ser executada de forma isolada,
ignorando a malha formal ja existente.

## Preflight obrigatorio

Antes de qualquer operacao relevante na execucao futura:

1. checar a camada formal de `startup-alignment`
2. executar o startup oficial do repositorio quando a sessao vier sem
   continuidade confiavel
3. executar o preflight oficial de WIP, worklog e continuidade
4. respeitar a regra de concluir ou destravar primeiro o trabalho ja ativo
5. usar a ferramenta primaria de rastreabilidade do projeto como fonte de
   verdade do fluxo vivo
6. antes de criar nova demanda, executar dedupe e reaproveitamento do agrupador
   pai adequado
7. identificar backlog, roadmap, issue, card ou demanda ja existente para este
   tema e reutilizar a trilha oficial quando ela ja cobrir o escopo
8. carregar as skills, guias, contratos e reviewers mais proximos do escopo
9. acionar revisores especializados por familia de arquivo afetada
10. como este escopo toca texto versionado, docs, comentarios e docstrings,
    acionar tambem a revisao ortografica consultiva

## Dependencias formais por tipo de superficie

- se a rodada tocar docs, comments, docstrings, prompts, cards, skills e
  strings legiveis, respeitar a camada formal de governanca documental
- se a rodada tocar artefatos persistidos, ledgers sincronizaveis,
  `documentation-link`, outbox, publication ou historico remoto, respeitar a
  fundacao oficial de sync
- esta iniciativa nao pode reimplementar arquitetura de sync paralela

## Regra de issue e pack

Se esta trilha tocar a arvore formal de prompt packs, obedecer o namespace
operacional `prompt`, com issue Jira apropriada do tipo `PROMPT:` e label
`prompt`, sem confundir o work item funcional com o work item de prompt pack.

---

# 5. PROBLEMA REAL

Hoje o repositorio apresenta drift temporal em multiplas camadas, incluindo:

- uso inconsistente de timezone
- uso inconsistente de locale
- mistura de horario tecnico e horario humano
- varios pontos assumindo `UTC` sem classificacao formal unificada
- comentarios, docstrings, docs, exemplos e templates perpetuando comportamentos
  temporais inconsistentes
- mistura indevida entre:
  - horario de exibicao humana
  - horario tecnico de auditoria
  - token temporal estavel de maquina
- inexistencia atual de uma policy declarativa unica, central e canonica para
  timezone, locale e regionalizacao

Este problema precisa ser tratado como bug estrutural de governanca, nao como
ajuste pontual.

---

# 6. PRINCIPIO CENTRAL DA SOLUCAO

A solucao correta deve separar com rigor tres coisas diferentes:

1. **tempo de exibicao humana**
2. **tempo tecnico de auditoria e interoperabilidade**
3. **token temporal estavel de maquina**

Essas tres camadas nao podem continuar misturadas.

Toda superficie temporal do repo deve ser explicitamente classificada e passar a
obedecer um contrato canonico unico.

---

# 7. POLICY DECLARATIVA CENTRAL OBRIGATORIA

A implementacao futura deve criar ou consolidar uma fonte canonica unica de
configuracoes globais do projeto em um arquivo TOML global canonico.

```text
Arquivo alvo planejado: config/config.toml
```

Este arquivo deve concentrar as configuracoes gerais do projeto e, entre elas,
a politica global de regionalizacao, idioma, timezone, formatos temporais e
calendario.

## Regra de consolidacao

Se ja existir configuracao espalhada que cumpra parcialmente esse papel:

- nao deixar a fonte de verdade fragmentada
- consolidar a configuracao no arquivo TOML global canonico do projeto
- ajustar referencias existentes para apontar para a nova fonte canonica
- nao manter duplicacao silenciosa de configuracoes globais

## Observacao de padrao de locale

O identificador recomendado para idioma e locale padrao e:

`pt-BR`

Formato correto:
- lingua em minusculo
- regiao em maiusculo

Este padrao segue a convencao BCP 47.

## Esqueleto minimo esperado do arquivo TOML global

```toml
version = 1

[project]
name = "dotfiles"
language_tag = "pt-BR"

[regionalization]
language_tag = "pt-BR"
timezone_name = "America/Sao_Paulo"
inherit_runtime_timezone = false
inherit_runtime_locale = false
human_date_format = "dd/MM/yyyy"
human_time_format = "HH:mm:ss"
human_datetime_format = "dd/MM/yyyy HH:mm:ss"

[regionalization.calendar]
week_start_day = "monday"
week_end_day = "sunday"
calendar_start_year = 2018
calendar_end_year = 2035

[temporal]
default_surface_class = "default_regionalized"
allow_explicit_utc = true
allow_stable_machine_token = true
retroactive_migration_enabled = true
require_surface_registry = true
require_validator_allowlist = true

[temporal.runtime]
expose_effective_timezone = true
expose_effective_locale = true
detect_runtime_policy_drift = true
```

## Regra de uso do arquivo

- o arquivo TOML global canonico passa a ser a fonte de verdade das
  configuracoes globais do projeto
- qualquer helper, validator, startup, restart, task ou workflow que dependa de
  configuracao temporal deve ler essa fonte canonica, direta ou indiretamente
- docs, comments, prompts e contratos devem refletir esse arquivo como source of
  truth

---

# 8. REGISTRY TEMPORAL POR SUPERFICIE

A policy global do projeto nao substitui o inventario e a
classificacao por superficie.

A implementacao futura deve criar um registry temporal especifico,
preferencialmente em um arquivo YAML proprio.

```text
Arquivo alvo planejado: config/time-surfaces.yaml
```

Este registry deve listar as superficies temporais relevantes do repositorio e a
classificacao semantica de cada uma.

## Regras do registry

- toda superficie temporal relevante precisa aparecer no registry
- nenhuma superficie pode permanecer sem classificacao
- o registry deve ser consumido pelo validator temporal
- o registry deve ser usado para diferenciar:
  - `default_regionalized`
  - `explicit_utc`
  - `stable_machine_token`
- o registry deve permitir migracao retroativa orientada por contrato

## Esqueleto inicial recomendado do registry temporal

```yaml
version: 1

surfaces:
  - surface_id: startup-session-report
    path_pattern:
      - "scripts/ai_session_startup_lib.py"
      - "docs/AI-STARTUP-AND-RESTART.md"
    surface_kind: startup_report
    class: default_regionalized
    human_visible: true
    owner_contract: startup-governance
    timezone_policy: project_default
    locale_policy: project_default
    migration_mode: retroactive
    validator_profile: human_display
    notes: "Startup e restart devem exibir timezone e locale efetivos."

  - surface_id: ai-worklog-ledger
    path_pattern:
      - "docs/AI-WIP-TRACKER.md"
      - "scripts/ai-worklog.py"
    surface_kind: operational_ledger
    class: default_regionalized
    human_visible: true
    owner_contract: worklog-governance
    timezone_policy: project_default
    locale_policy: project_default
    migration_mode: retroactive
    validator_profile: human_display
    notes: "Auditar campos historicamente nomeados como UTC."

  - surface_id: sync-outbox-events
    path_pattern:
      - "scripts/ai_sync_foundation_lib.py"
      - "config/ai/sync-targets.yaml"
    surface_kind: sync_event
    class: explicit_utc
    human_visible: false
    owner_contract: sync-foundation
    timezone_policy: explicit_utc
    locale_policy: not_applicable
    migration_mode: keep_if_justified
    validator_profile: technical_utc
    utc_justification: "Eventos tecnicos de sincronismo e interoperabilidade."
    notes: "So permanece em UTC se o contrato foundation continuar exigindo."
```

## Campos minimos esperados por entrada

Cada entrada do registry deve poder declarar, no minimo:

- `surface_id`
- `path_pattern`
- `surface_kind`
- `class`
- `human_visible`
- `owner_contract`
- `timezone_policy`
- `locale_policy`
- `migration_mode`
- `validator_profile`
- `utc_justification` quando `class = explicit_utc`
- `token_justification` quando `class = stable_machine_token`
- `notes`

---

# 9. REGRA GLOBAL DA INICIATIVA

Neste repositorio, a regra correta passa a ser:

- toda geracao, serializacao, exibicao, comparacao, parsing, documentacao,
  validacao ou uso semantico de data e hora deve obedecer a policy temporal
  canonica do projeto
- o locale e timezone padrao do projeto devem ser explicitamente configurados e
  rastreaveis na fonte canonica global do projeto
- toda superficie humana deve usar, por default, o locale e timezone canonico
  do projeto
- `UTC` deixa de ser aceito como default implicito em superficies humanas
- todo uso legitimo de `UTC` deve ser explicitamente contratado, nomeado,
  justificado e testado
- tokens tecnicos de maquina nao devem ser tratados como horario de exibicao

## Regra retroativa

Esta iniciativa deve assumir desde ja migracao retroativa, porque a base ainda e
pequena o suficiente para isso.

Portanto:

- toda superficie temporal historica hoje em `UTC` deve ser auditada
- toda superficie humana hoje em `UTC` deve ser migrada retroativamente para o
  locale e timezone canonico do projeto, salvo excecao contratual legitima
- toda superficie que permanecer em `UTC` deve ficar explicitamente marcada e
  documentada
- nao deixar "corrigir depois" como estrategia principal

---

# 10. MATRIZ DE PRECEDENCIA CANONICA

Esta iniciativa deve formalizar uma matriz de precedencia explicita para evitar
ambiguidade.

A ordem correta de decisao deve ser esta:

## Nivel 1 -- contrato explicito da superficie

Se uma superficie temporal especifica tiver contrato explicito, ele vence.

Exemplos:

- um campo marcado como `explicit_utc`
- um token tecnico marcado como `stable_machine_token`
- um ledger explicitamente reclassificado para exibicao regionalizada

## Nivel 2 -- policy temporal canonica do projeto

Se a superficie nao tiver contrato proprio, vale a policy temporal central do
projeto, definida na fonte canonica global do projeto.

Essa policy deve dizer, no minimo:

- timezone canonico
- locale canonico
- formato humano padrao
- politica de tokens tecnicos
- allowlist de excecoes `UTC`
- criterios de migracao retroativa
- classificacao oficial das superficies temporais

## Nivel 3 -- runtime efetivo permitido pela policy

Se a policy central definir que certo valor deve herdar do host ou runtime,
entao o runtime efetivo entra como fonte de resolucao.

Exemplos:

- herdar timezone do host quando a policy mandar
- herdar locale do ambiente quando a policy mandar
- detectar anomalia quando runtime e policy divergirem

## Nivel 4 -- override explicito e rastreavel da execucao atual

Uma execucao pontual pode usar excecao explicita apenas quando houver:

- ordem direta do usuario
- contrato declarativo
- necessidade tecnica real e rastreavel

Esse override nao cria novo default.

## Nivel 5 -- fallback seguro

Se nenhuma camada acima resolver a semantica temporal, a execucao deve falhar
com drift explicito ou entrar em modo seguro auditavel, nunca assumir
silenciosamente `UTC` ou algum horario local arbitrario.

## Objetivo da matriz

Essa matriz existe para responder, sem ambiguidade:

- qual timezone usar aqui?
- esta superficie e exibicao humana ou auditoria tecnica?
- este timestamp pode ser migrado retroativamente?
- este `UTC` atual continua valido ou precisa ser removido?
- este token representa horario de exibicao ou apenas identificador tecnico?

---

# 11. CLASSES OBRIGATORIAS DE SUPERFICIE TEMPORAL

Toda superficie temporal do repositorio deve ser classificada explicitamente em
uma destas classes:

- `default_regionalized`
- `explicit_utc`
- `stable_machine_token`

## `default_regionalized`

Usar para superficies humanas e de leitura operacional.

Exemplos:

- chat gerado pelo repo
- startup report
- restart report
- resumos operacionais
- docs
- comentarios
- docstrings
- help texts
- templates user-facing
- ledgers de leitura humana
- logs de leitura humana
- comentarios estruturados
- textos de status
- cabecalhos e colunas human-readable

## `explicit_utc`

Usar somente quando houver justificativa legitima, declarada e testada.

Exemplos possiveis:

- campos de interoperabilidade
- auditoria tecnica que precise permanecer em UTC
- integracoes externas que exijam UTC
- eventos de outbox e sync cujo contrato tecnico exija UTC
- snapshots tecnicos com naming explicito de UTC

## `stable_machine_token`

Usar para tokens tecnicos que nao sao horario de exibicao.

Exemplos:

- ids
- slugs
- sufixos tecnicos de bundle
- seeds
- chaves de ordenacao
- nomes tecnicos de arquivo
- tokens estaveis usados por automacao

## Regra importante

Toda superficie atual deve ser auditada com vies de migracao para
`default_regionalized`.

Ela so pode permanecer como `explicit_utc` ou `stable_machine_token` se a
auditoria provar que essa classificacao ainda e semanticamente correta.

---

# 12. REGRA ESPECIFICA PARA AJUSTE RETROATIVO

Esta iniciativa deve assumir ajuste retroativo imediato enquanto a base ainda e
pequena.

Isso significa que:

- worklog atual deve ser auditado e reclassificado
- ledgers de review devem ser auditados e reclassificados
- fallback ledger deve ser auditado e reclassificado
- scrum master ledger e logs de cerimonia devem ser auditados e reclassificados
- camada de backfill deve ser auditada e reclassificada
- fundacao de sync deve ser auditada e reclassificada
- docs, prompts, cards, skills e contratos que ensinem `UTC` como default devem
  ser corrigidos retroativamente

## Regra de reclassificacao

O trabalho nao pode migrar essas superficies por chute.

Ele deve:

1. classificar formalmente cada superficie
2. decidir se ela deve migrar para `default_regionalized`
3. manter `explicit_utc` apenas quando a justificativa for valida
4. manter `stable_machine_token` apenas quando nao houver semantica de exibicao
5. ajustar retroativamente o historico e os contratos correspondentes

---

# 13. DIRETRIZ ARQUITETURAL OBRIGATORIA

- centralizar a politica temporal em contratos, helpers e validadores oficiais
- eliminar logica temporal paralela espalhada pelo repo
- eliminar hardcodes temporais sem contrato
- eliminar `UTC` implicito em exibicao humana
- preservar `UTC` apenas onde ele continuar explicitamente correto
- nao converter silenciosamente um campo que deva continuar `explicit_utc`
- quando houver nomes como:
  - `Data/Hora UTC`
  - `Inicio UTC`
  - `Concluido UTC`
  - `generated_on_utc`
  - `updated_at_utc`
  - `occurred_at`
  e similares:
  - ou continuam explicitamente UTC com justificativa formal
  - ou sao migrados retroativamente junto com a mudanca de contrato
  - ou sao renomeados para refletir a nova semantica corretamente

---

# 14. CAMADA DE CHAT

O tratamento correto da camada de chat deve seguir estas regras:

- todo timestamp gerado pelo repo para chat, resumo, comentario estruturado,
  startup report, restart report ou artefato textual de operacao deve usar a
  policy temporal canonica do projeto
- esses timestamps devem ser gerados no momento da emissao
- nao devem depender de cache temporal antigo
- nao devem sair em `UTC` por acidente quando forem superficies humanas
- devem respeitar o locale e timezone canonico do projeto

## Limite estrutural obrigatorio

Se a UI nativa da plataforma ou do app renderizar seu proprio timestamp fora do
controle do repo, nao fingir que o repositorio controla isso.

Nesse caso, a implementacao deve:

- documentar a limitacao estrutural
- diferenciar timestamp nativo da plataforma de timestamp emitido pelo repo
- implementar a melhor mitigacao tecnica realmente auditavel
- garantir que tudo que o repo controla siga a policy correta

---

# 15. STARTUP E RESTART

Startup e restart devem passar a:

- carregar explicitamente a policy temporal do projeto
- expor timezone efetivo
- expor locale efetivo
- expor a fonte da configuracao temporal
- expor divergencias entre runtime e policy
- validar coerencia da sessao com a policy canonica
- registrar drift, excecao ou anomalia quando houver

O startup deve impedir rodada operando com semantica temporal errada sem
deteccao.

## Dependencia formal

Esta camada deve se integrar ao startup oficial ja existente e nao criar um
startup paralelo.

---

# 16. REVIEWER TEMPORAL OFICIAL BLOQUEANTE

Implementar ou formalizar um reviewer oficial especializado em:

- tempo
- timezone
- locale
- regionalizacao
- semantica temporal

## Escopo real desse reviewer

Este reviewer valida **apenas a semantica temporal**.

Ele nao deve absorver o papel dos outros reviewers.

Os demais reviewers continuam responsaveis por suas competencias normais.

## O que esse reviewer valida

- classificacao correta da superficie temporal
- semantica correta de locale e timezone
- separacao correta entre exibicao humana, auditoria tecnica e token de maquina
- ausencia de `UTC` implicito indevido
- aderencia a fonte canonica global do projeto
- aderencia ao registry e allowlist de excecoes
- docs, comments, docstrings, prompts e contratos ensinando a regra correta

## O que ele nao substitui

- reviewer tecnico de familia
- reviewer declarativo ou estrutural
- reviewer documental
- reviewer linguistico
- aprovador final tecnico

## Poder de bloqueio

Esse reviewer deve poder reprovar qualquer diff ou artefato que introduza:

- drift temporal
- `UTC` implicito indevido
- helper temporal paralelo fora da camada oficial
- docs, comentarios ou docstrings ensinando regra errada
- mistura indevida entre classes temporais
- classificacao inconsistente no registry temporal

---

# 17. VALIDATOR TEMPORAL OBRIGATORIO

Nao usar grep cego de `UTC`.

Implementar validator temporal com:

- registry e allowlist oficial
- classificacao por superficie
- regras por classe temporal
- excecoes justificadas
- mapeamento de nomes herdados
- deteccao de drift entre contrato e implementacao

## O validator deve conseguir distinguir

- `UTC` legitimo e explicitamente contratado
- `UTC` indevido em superficie humana
- token tecnico que nao representa horario de exibicao
- naming herdado que exige migracao ou justificativa
- serializacao tecnica valida
- exibicao humana incorreta
- artefato elegivel para migracao retroativa

## Enforcement minimo do validator

- scan do repo
- scan de contratos
- scan de docs, comments e docstrings
- scan de helpers temporais
- scan de artefatos gerados relevantes
- gate automatizado
- cobertura de testes

---

# 18. DESCOBERTA OBRIGATORIA DO CONTEXTO DO REPO

Antes de editar, descobrir e mapear:

- onde o projeto define startup e restart oficial
- onde o projeto define trackers de WIP, worklog e continuidade
- onde a governanca oficial de reviewers vive
- quais tasks, scripts, workflows e validadores cobrem governanca
- qual a fonte primaria de rastreabilidade do trabalho
- quais arquivos hoje geram timestamps, datas, horas ou exibicoes temporais
- quais superficies precisam continuar em `UTC` por contrato legitimo
- quais superficies hoje estao em `UTC` apenas por heranca historica
- quais superficies humanas ja podem ser migradas imediatamente
- se existe alguma configuracao previa espalhada que deva ser consolidada na
  fonte canonica global do projeto

Nao assumir naming, paths, tasks ou artefatos fixos sem descobrir o que o repo
realmente usa.

---

# 19. HOTSPOTS INICIAIS OBRIGATORIOS

Auditar no minimo:

- startup e restart oficial
- camada de chat e resumos operacionais emitidos pelo repo
- worklog
- ledgers de review
- fallback ledger
- scrum master ledger
- logs de cerimonia
- camada de backfill Jira e Confluence
- fundacao de sync
- scripts e bibliotecas que geram timestamps
- contratos declarativos e policies de reviewers
- docs, prompts, skills, cards e comentarios que ensinem a regra temporal
- tasks, workflows, validadores e testes conectados a essas camadas

---

# 20. PISTAS CONCRETAS A PROCURAR

Usar como ponto de partida de auditoria:

- campos nomeados como:
  - `Data/Hora UTC`
  - `Inicio UTC`
  - `Concluido UTC`
  - `generated_on_utc`
  - `updated_at_utc`
  - `occurred_at`
- usos de:
  - `datetime.now(timezone.utc)`
  - `strftime(...UTC)`
  - `astimezone()`
  - `Get-Date`
  - formatos inline soltos
  - helpers temporais divergentes
- textos ensinando que `UTC` e o padrao do repo
- mistura entre timestamp tecnico, timestamp de exibicao e token tecnico

---

# 21. ENTREGAS OBRIGATORIAS

Entregar, no minimo:

- um arquivo TOML global como fonte canonica de configuracoes do projeto
- a sessao de regionalizacao e temporal devidamente formalizada nessa fonte
  canonica
- um registry temporal YAML por superficie
- policy temporal canonica unica
- matriz de precedencia canonica
- classificacao explicita de todas as superficies temporais relevantes
- helpers oficiais centralizados
- correcao real dos pontos com drift
- migracao retroativa das superficies humanas incorretamente em `UTC`
- startup e restart endurecidos
- tratamento correto da camada de chat sob controle do repo
- reviewer temporal oficial bloqueante
- validator temporal com allowlist e registry
- docs, contratos, prompts, cards, skills, scripts, tasks, workflows e testes
  em paridade

---

# 22. CRITERIOS DE ACEITE

A entrega so conta como concluida se:

1. todo timestamp emitido pelo repo para superficie humana relevante obedecer ao
   locale e timezone canonico do projeto
2. startup e restart validarem e reportarem explicitamente a politica temporal
3. nenhuma superficie user-facing relevante continuar exibindo `UTC` por
   acidente
4. nenhum texto do projeto continuar ensinando `UTC` como padrao sem excecao
   explicita
5. comments, docstrings, docs, logs, templates e contratos ficarem alinhados
6. superficies explicitamente `UTC` permanecerem apenas quando houver contrato
   claro
7. o projeto ganhar uma autoridade perene de enforcement contra drift temporal
8. ambientes suportados permanecerem coerentes
9. qualquer limitacao estrutural do runtime ficar documentada e mitigada com o
   melhor enforcement disponivel
10. a classificacao retroativa das superficies atuais tiver sido concluida
11. o validator temporal distinguir corretamente `explicit_utc`,
    `default_regionalized` e `stable_machine_token`
12. a fonte canonica global e o registry temporal por superficie estiverem em
    uso real e refletidos pelos contratos relevantes

---

# 23. VALIDACAO MINIMA

Rodar no minimo:

- startup oficial do projeto
- validacao oficial de governanca do projeto
- validacao documental
- smoke ou eval de governanca, se existir
- typecheck, se existir
- testes automatizados relevantes
- testes novos necessarios para:
  - a fonte canonica global em TOML
  - o registry temporal por superficie
  - policy temporal central
  - matriz de precedencia
  - helpers temporais
  - startup e restart
  - chat sob controle do repo
  - validator temporal
  - reviewer temporal
  - contratos e artefatos gerados

---

# 24. FORMA DE TRABALHO

- nao parar em analise
- nao entregar apenas plano
- nao fazer correcao cosmetica ou parcial
- nao criar framework paralelo
- nao quebrar a governanca oficial do projeto
- nao esconder limitacoes do runtime
- nao usar grep cego como enforcement principal
- resolver a causa raiz
- formalizar a regra
- implementar enforcement real
- deixar a regressao bloqueada por design

---

# 25. SAIDA FINAL ESPERADA

Ao final, entregar um resumo curto com:

- causa raiz
- policy adotada
- matriz de precedencia adotada
- arquivo canonico da policy temporal
- arquivo do registry temporal por superficie
- superficies reclassificadas
- arquivos tocados
- reviewer temporal criado ou endurecido
- validator temporal adicionado
- enforcement adicionado
- testes executados
- risco residual
