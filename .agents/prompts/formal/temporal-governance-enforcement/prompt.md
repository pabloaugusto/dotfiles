# Prompt Para Implementacao - Governanca Temporal E Regionalizacao

## Missao

Implementar, de ponta a ponta, a correcao definitiva, perene e bloqueante da
camada de data/hora/locale/regionalizacao deste repositorio, eliminando drift
em chat, startup, restart, logs, arquivos gerados, docs, comentarios,
docstrings, templates, contratos declarativos, prompts, cards, skills,
workflows, tasks, validadores e testes.

Esta entrega nao e ajuste cosmetico.
Ela deve resolver a causa raiz, formalizar o contrato correto, materializar
enforcement real e impedir regressao futura.

## Regra zero

Antes de qualquer mudanca relevante:

1. executar o startup oficial do projeto, como task, script ou fluxo canonico
   equivalente
2. executar o preflight oficial de WIP, worklog ou continuidade, se existir
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

## Problema real

Hoje o repositorio apresenta drift de data/hora em multiplas camadas:

- horario incorreto no chat em relacao ao relogio real do host e/ou ao fuso
  configurado
- uso inconsistente de timezone, locale e regionalizacao em startup, restart,
  ledgers e logs
- varios pontos assumindo `UTC` como default sem contrato explicito
- comentarios, docstrings, docs, exemplos e templates perpetuando o padrao
  errado
- mistura indevida entre horario tecnico de auditoria, horario de exibicao para
  operador e tokens temporais estaveis de maquina

Isso deve ser corrigido em todo o repositorio, nao apenas em codigo executavel.

## Regra perene global

Neste repositorio, a regra padrao passa a ser:

- toda geracao, serializacao, exibicao, comparacao, parsing, documentacao,
  validacao ou uso semantico de data/hora deve respeitar a configuracao
  canonica de regionalizacao, locale e timezone do projeto e do host em
  runtime
- `UTC` deixa de ser default implicito
- `UTC` so pode existir por excecao explicita, rastreavel e semanticamente
  correta
- fora dessas excecoes, o padrao obrigatorio e a regionalizacao canonica do
  projeto

### Excecoes validas para UTC

`UTC` so pode ser usado quando houver uma destas condicoes:

- ordem direta do usuario para aquela rotina, log ou arquivo
- contrato declarativo ou versionado marcando explicitamente a superficie como
  UTC
- necessidade tecnica real de auditoria, interoperabilidade, integracao externa
  ou protocolo, com naming claro de que aquele dado e UTC

Se uma rotina, log, arquivo, campo ou integracao precisar usar `UTC`, isso deve
ficar:

- explicitamente contratado
- semanticamente nomeado
- tecnicamente justificado
- coberto por validacao e teste

## Fronteira obrigatoria das superficies temporais

Toda superficie do repositorio que lide com tempo deve ser classificada
explicitamente em uma destas classes:

- `default_regionalized`
- `explicit_utc`
- `stable_machine_token`

### Significado das classes

#### `default_regionalized`

Usar para tudo que for camada visivel ao operador ou contexto humano, incluindo:

- chat
- resumos
- relatorios de startup e restart
- mensagens operacionais
- docs
- comentarios
- docstrings
- templates user-facing
- ledgers e logs de leitura humana quando nao houver contrato tecnico de UTC

#### `explicit_utc`

Usar apenas quando a superficie tiver contrato explicito de UTC.

Exemplos tipicos:

- trilhas tecnicas de auditoria com necessidade real de UTC
- integracoes ou protocolos que exijam UTC
- campos historicos explicitamente nomeados como UTC e ainda semanticamente
  corretos

#### `stable_machine_token`

Usar para identificadores ou tokens tecnicos de maquina, por exemplo:

- sufixos estaveis de arquivo
- slugs
- ids
- nomes tecnicos de bundles
- seeds temporais
- tokens de ordenacao

Esses tokens nao devem ser confundidos com horario de exibicao.

## Escopo total da auditoria

Nao limite a correcao a codigo executavel.

Audite e corrija, quando aplicavel:

- scripts
- bibliotecas
- tasks
- workflows
- validadores
- testes
- docs
- comentarios
- docstrings
- templates
- ledgers
- logs versionados
- prompts
- cards
- skills
- contratos
- configs declarativas
- artefatos gerados

Se houver qualquer texto ensinando `UTC` como padrao sem que isso ainda seja
verdade, trate como bug de governanca e corrija.

Se houver exemplos, snippets, templates ou comentarios perpetuando o padrao
errado, corrija tambem.

## Diretriz arquitetural obrigatoria

- centralizar a politica temporal em helpers, contratos e validadores oficiais
- eliminar logica temporal paralela espalhada pelo repositorio
- eliminar hardcodes de `UTC`, `timezone.utc`, `strftime(... UTC)`, `Get-Date`
  sem contrato, formatos inline soltos e helpers duplicados
- preservar `UTC` apenas onde ele for explicitamente devido
- nao converter silenciosamente campos legitimamente UTC sem decisao contratual
- quando houver nomes como `Data/Hora UTC`, `Inicio UTC`, `Concluido UTC` e
  similares, trata-los com rigor contratual:
  - ou continuam explicitamente UTC com justificativa
  - ou sao migrados junto com a mudanca formal do contrato

## Reviewer oficial bloqueante

Implementar ou formalizar um reviewer oficial especializado em tempo, timezone,
locale e regionalizacao.

Este papel:

- nao e lembrador de chat
- nao e apenas consultivo
- deve ser implementador, garantidor, revisor e enforcement
- deve entrar formalmente no time oficial de reviewers do projeto
- deve ser bloqueante quando houver superficie temporal tocada

### Escopo desse reviewer

Ele deve revisar qualquer diff ou artefato gerado com semantica temporal,
independentemente da extensao do arquivo, incluindo:

- codigo
- docs
- comentarios
- docstrings
- logs
- templates
- prompts
- contratos declarativos
- configs
- artefatos gerados

### Poder de bloqueio

Esse reviewer deve poder reprovar mudancas que introduzam:

- drift temporal
- `UTC` implicito indevido
- hardcode temporal sem contrato
- helper paralelo fora da camada oficial
- docs, comentarios e docstrings ensinando regra errada
- mistura indevida entre `default_regionalized`, `explicit_utc` e
  `stable_machine_token`

### Se necessario, crie ou ajuste

- card
- registry
- skill
- reviewer policy
- contratos declarativos
- docs e catalogos
- ledger ou rastreabilidade correspondente

Fechamento sem parecer aprovado desse reviewer, quando houver superficie
temporal tocada, deve ser invalido.

## Enforcement obrigatorio

Nao deixe isso apenas em texto.

Implemente enforcement real com backend do projeto.

### Enforcement minimo esperado

- verificacao no startup
- verificacao no restart
- verificacao nos pontos de emissao de mensagens e resumos
- validator dedicado para scan de repo e artefatos gerados
- testes automatizados
- gate de CI
- review especializado bloqueante
- rastreabilidade de inconformidades

### Regra de honestidade tecnica

Se o runtime atual nao suportar monitor literal em tempo real, nao fingir que
existe.

Nesse caso, implementar a combinacao mais forte realmente auditavel e
sustentavel, em vez de prometer uma cobertura inexistente.

## Startup e restart

Startup e restart devem passar a:

- carregar explicitamente a politica temporal do projeto
- expor timezone efetivo
- expor locale efetivo
- expor a fonte da configuracao
- validar se a sessao esta coerente com a politica canonica
- registrar drift, excecao ou anomalia quando houver

O startup deve ajudar a impedir rodada operando com hora errada sem deteccao.

## Camada de chat

O timestamp do chat deve:

- usar o horario local real do sistema
- ser gerado no momento do envio
- nao depender de cache temporal antigo
- nao sair em `UTC` por acidente
- respeitar a regionalizacao canonica do projeto

Se houver limitacao estrutural do runtime para controlar isso com precisao
absoluta, documentar a limitacao e implementar a melhor mitigacao tecnica
disponivel.

## Descoberta obrigatoria do contexto do projeto

Antes de editar, descubra e mapeie:

- onde o projeto define startup e restart oficial
- onde o projeto define trackers de WIP, worklog ou continuidade
- onde a governanca oficial de reviewers vive
- quais tasks, scripts, workflows e validadores cobrem governanca
- qual a fonte primaria de rastreabilidade do trabalho
- onde a configuracao canonica de locale, timezone e regionalizacao esta
  definida
- quais arquivos hoje geram timestamps, datas, horas ou exibicoes temporais
- quais superficies precisam continuar em `UTC` por contrato legitimo

Nao assuma naming, paths, tasks ou artefatos fixos sem antes descobrir o que o
repositorio realmente usa.

## Hotspots iniciais obrigatorios

Auditar no minimo:

- bibliotecas e scripts que geram timestamps
- startup e restart oficial
- camada de chat e resumos operacionais
- ledgers, logs e relatorios versionados
- contratos declarativos e policies de reviewers
- docs, prompts, skills, cards e comentarios que ensinem a regra temporal
- tasks, workflows, validadores e testes conectados a essas camadas

## Pistas concretas a procurar no repositorio

Use como pontos de partida de auditoria:

- regras ja existentes exigindo horario local real no chat
- relatorios gerados sem timezone explicito
- usos de `datetime.now(timezone.utc)`, `strftime(... UTC)`, `astimezone()`,
  `Get-Date` ou equivalentes
- campos nomeados como `UTC`
- helpers temporais divergentes entre si
- mistura entre timestamp tecnico, timestamp de exibicao e token tecnico

## Entregas obrigatorias

Entregar, no minimo:

- politica canonica unica de tempo e locale
- helpers oficiais centralizados
- classificacao explicita das superficies temporais
- correcao real dos pontos com drift
- startup e restart endurecidos
- chat corrigido
- reviewer oficial bloqueante para semantica temporal
- validator ou gate automatizado contra regressao
- docs, contratos, prompts, cards, skills, scripts, tasks, workflows e testes
  em paridade

## Criterios de aceite

A entrega so conta como concluida se:

1. o horario do chat bater com o relogio local real do sistema no momento do
   envio
2. startup e restart validarem e reportarem explicitamente a politica temporal
3. nenhum ponto user-facing relevante continuar exibindo `UTC` por acidente
4. nenhum texto do projeto continuar ensinando `UTC` como padrao sem excecao
   explicita
5. comentarios, docstrings, docs, logs, templates e contratos ficarem alinhados
6. campos explicitamente UTC permanecerem apenas quando houver contrato claro
7. o projeto ganhar uma autoridade perene de enforcement contra drift temporal
8. os ambientes suportados pelo projeto permanecerem coerentes
9. qualquer limitacao estrutural do runtime ficar documentada e mitigada com o
   melhor enforcement disponivel

## Validacao minima

Rodar no minimo:

- startup oficial do projeto
- validacao oficial de governanca do projeto
- validacao documental
- smoke ou eval de governanca, se existir
- typecheck, se existir
- testes automatizados relevantes
- testes novos necessarios para:
  - helpers temporais
  - startup e restart
  - chat
  - validator temporal
  - reviewer temporal
  - contratos e artefatos gerados

## Forma de trabalho

- nao parar em analise
- nao entregar apenas plano
- nao fazer correcao cosmetica ou parcial
- nao criar framework paralelo
- nao quebrar a governanca oficial do projeto
- nao esconder limitacoes do runtime
- resolver a causa raiz
- formalizar a regra
- implementar enforcement real
- deixar a regressao bloqueada por design

## Saida final esperada

Ao final, entregar um resumo curto com:

- causa raiz
- politica adotada
- arquivos tocados
- reviewer ou guardiao temporal criado ou endurecido
- enforcement adicionado
- testes executados
- risco residual
