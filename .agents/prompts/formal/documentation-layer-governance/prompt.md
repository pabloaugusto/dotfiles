# PROMPT PARA CODEX -- ESTRUTURA E GOVERNANCA DA CAMADA DOCUMENTAL POR AGENTES DE IA

## METADADOS OBRIGATORIOS

### Titulo exato da task principal no Jira

**PROMPT: Estrutura e governanca da camada documental por agentes de IA**

### Naming de branches

Se houver branch para esta trilha, usar o padrao canonico do repo:

`<type>/<jira-key>-<slug-curto-em-ingles>`

Sugestoes de slug:

- `doc-layer-governance`
- `doc-governance-rollout`
- `doc-agent-structure`
- `doc-layer-refactor`

---

# 1. DEPENDENCIAS DE PACKS E ORDEM SEGURA DE EXECUCAO

Este prompt NAO deve ser executado de forma isolada quando os pre-requisitos
nao tiverem sido satisfeitos.

## 1.1. Preflight packs que precisam ser checados antes

- `startup-alignment`

## 1.2. Prerequisite packs que precisam existir e ser validados antes

- `sync-outbox-foundation`

## 1.3. Ordem segura de execucao

1. checar `startup-alignment` quando a sessao vier sem continuidade
   comprovadamente integra
2. executar ou validar `sync-outbox-foundation`
3. so depois executar `documentation-layer-governance`

## 1.4. Regra obrigatoria de composicao

Este prompt documental e uma camada de governanca de dominio.

Ele:

- consome a fundacao oficial de sync
- nao compete com a fundacao oficial de sync
- nao a reimplementa
- nao a substitui
- nao cria arquitetura paralela de persistencia, outbox, retries ou `ack`

---

# 2. CONTEXTO E OBJETIVO

Este repositorio ja possui uma malha real de governanca de IA, com:

- `Jira` como fonte primaria do fluxo vivo
- `Confluence` como superficie documental cross-surface
- docs versionadas no repo
- cards, skills, prompts e contracts em [`.agents/`](../../README.md)
- ledgers vivos
- tasks e validators
- reviewers especializados
- gate de arquitetura
- gate de processo
- gate consultivo de ortografia
- worklog, lessons e controle de continuidade

O objetivo desta iniciativa nao e criar uma camada paralela de "agentes de
documentacao". O objetivo correto e consolidar uma camada documental canonica,
clara, auditavel, rastreavel e sem ambiguidades, capaz de governar de forma
consistente:

- documentacao versionada no repo
- paginas do `Confluence`
- comentarios estruturados do `Jira`
- docstrings
- comentarios inline e de bloco
- help texts
- mensagens de erro
- mensagens de warning
- strings legiveis em configuracao
- logs vivos em Markdown
- terminologia e ortografia tecnica
- source of truth por superficie
- placement entre repo, Jira, Confluence e logs vivos
- lifecycle documental e textual
- backlog consultivo de findings nao bloqueantes
- classificacao de findings bloqueantes vs nao bloqueantes
- sincronismo operacional e rastreabilidade entre superficies

O problema real a resolver nao e apenas "escrever melhor". O problema central e
a combinacao de:

- knowledge sprawl
- drift entre repo, Jira e Confluence
- sobreposicao de papeis
- ownership difuso
- falta de uma matriz explicita de superficies textuais
- ausencia de regras unificadas para comments, docstrings, help texts,
  mensagens e strings
- ausencia de um desenho sem ambiguidades para saber qual agente deve fazer o
  que
- risco de que papeis atuais continuem colidindo por heranca historica de
  escopo
- concentracao excessiva de responsabilidades no antigo papel documental
- confusao entre decidir, escrever, revisar, governar e sincronizar

A meta principal desta iniciativa e deixar a camada documental com fronteiras
tao claras que, ao olhar qualquer demanda, fique obvio:

- quem revisa linguagem
- quem escreve
- quem revisa qualidade documental
- quem governa source of truth, placement e lifecycle
- quem executa o sincronismo e a rastreabilidade cross-surface
- quem valida corretude tecnica do texto embutido no codigo
- quem apenas fiscaliza, arbitra ou consolida sem invadir ownership alheio

---

# 3. CONTEXTO OBRIGATORIO DO REPO

Voce deve partir do estado real atual do repositorio. Nao trate esta trilha
como greenfield.

## 3.1. Contratos e ativos existentes que precisam ser respeitados

- `Jira` e a fonte primaria do fluxo vivo
- [`docs/AI-WIP-TRACKER.md`](../../../../docs/AI-WIP-TRACKER.md) e fallback
  contingencial, nao fonte primaria
- `Confluence` ja e superficie oficial para a malha cross-surface
- [`.agents/`](../../README.md) e a fonte canonica da camada declarativa
- `Pascoalete` ja existe como trilha consultiva de ortografia e `cspell`
- `Escrivao` ja existe como papel documental, embora hoje concentre escopos
  demais
- `Curador Repo` ja existe como guardiao do plano repo-local
- `ai-reviewer-config-policy` ja existe como reviewer declarativo/estrutural
- `ai-reviewer` ja existe como gate transversal
- `ai-tech-lead` ja existe como aprovador oficial de PR e origem equivalente
- `ai-scrum-master` ja existe como gate global de processo, board, WIP,
  ownership, comments e cerimonias
- `ai-product-owner` ja existe como owner de backlog, intake e narrativa de
  demanda
- reviewers tecnicos por familia ja existem
- ledgers vivos ja existem:
  - [`docs/AI-ORTHOGRAPHY-LEDGER.md`](../../../../docs/AI-ORTHOGRAPHY-LEDGER.md)
  - [`docs/AI-REVIEW-LEDGER.md`](../../../../docs/AI-REVIEW-LEDGER.md)
  - [`docs/AI-SCRUM-MASTER-LEDGER.md`](../../../../docs/AI-SCRUM-MASTER-LEDGER.md)
- tasks e validators canonicos ja existem:
  - `task ai:startup:session`
  - `task ai:worklog:check`
  - `task docs:check`
  - `task spell:dictionary:audit`
  - `task spell:review`
  - `task ai:review:record`
  - `task ai:review:check`
  - `task ai:validate`
  - `task ai:eval:smoke`
  - `task ci:workflow:sync:check`
  - `task ai:lessons:check`
  - `task ai:worklog:close:gate`

## 3.2. Regra central desta iniciativa

A implementacao final deve:

- preservar o que ja funciona
- explicitar o que hoje esta difuso
- reduzir sobreposicoes
- evitar proliferacao desnecessaria de novos papeis
- endurecer fronteiras
- manter compatibilidade operacional com a malha atual do repo
- ajustar explicitamente os papeis existentes para minimizar colisoes com os
  novos papeis nucleares
- nao deixar escopo implicito, presumido ou "parece obvio"

---

# 4. DEPENDENCIA FORMAL DA FUNDACAO DE SYNC

Esta camada documental NAO deve reinventar a infraestrutura de sincronismo.
Ela depende formalmente do prompt pack:

- [`sync-outbox-foundation/prompt.md`](../sync-outbox-foundation/prompt.md)
- [`sync-outbox-foundation/context.md`](../sync-outbox-foundation/context.md)
- [`sync-outbox-foundation/meta.yaml`](../sync-outbox-foundation/meta.yaml)

## 4.1. Regra de composicao obrigatoria

O pack `sync-outbox-foundation` continua sendo a camada responsavel por definir:

- `repo declarativo -> outbox local duravel -> fonte perene remota`
- `workspace_id`
- `runtime_environment_id`
- `~/.ai-control-plane/workspaces/<workspace-id>/`
- `outbox/`
- `status/`
- `checkpoints/`
- `dead-letter/`
- eventos `jsonl`
- `ack`
- retry
- `retention_policy`
- o manifest `sync-targets.yaml` em [`config/ai/`](../../../../config/ai/)
- classificacao de artefatos elegiveis para sincronismo perene

Este prompt documental continua sendo a camada responsavel por definir:

- ownership por superficie textual
- papeis e fronteiras de agentes documentais
- rules de decisao sobre docs, comments, docstrings, help e mensagens
- source of truth documental por superficie
- lifecycle documental
- criterios de severidade documentais
- quando e por que um artefato documental deve entrar ou nao no fluxo de sync

## 4.2. Regras negativas obrigatorias

Este prompt documental nao pode:

- criar uma arquitetura paralela de sync
- criar um manifest documental separado de sync
- redefinir `workspace_id`
- redefinir `runtime_environment_id`
- redefinir o root de outbox local
- redefinir `ack`, retry, `dead-letter` ou `retention_policy`
- bypassar o outbox local duravel quando a fundacao exigir o fluxo oficial
- tratar `Confluence` como destino obrigatorio para tudo sem classificacao
  previa
- mover todos os `.md` vivos para remoto sem classificacao aderente ao prompt
  foundation

## 4.3. Regra de heranca obrigatoria

Sempre que esta camada documental precisar de sync, persistencia, publicacao
cross-surface ou trilha remota perene, ela deve:

1. usar a arquitetura-base definida no prompt foundation
2. escrever ou consumir entradas no manifest `sync-targets.yaml` em
   [`config/ai/`](../../../../config/ai/)
3. respeitar a classificacao de artefatos do foundation
4. usar `ai-documentation-sync` como operador documental dessa fundacao
5. nao criar atalhos locais ad hoc

---

# 5. DIRETRIZ CENTRAL DE ARQUITETURA

A camada documental final deve ser modelada por **competencia dominante**.

Cada agente deve ter:

- uma pergunta propria
- um escopo dominante
- inputs claros
- outputs claros
- ownership explicito
- limites claros
- pontos de integracao claros
- regras anticolisao explicitas
- skills claras
- modo de acionamento claro
- criterio explicito do que ele nao pode fazer sozinho

Nao pode haver situacao em que dois agentes diferentes parecam igualmente
corretos para executar a mesma responsabilidade dominante.

Toda sobreposicao inevitavel deve ser tratada como interface formal entre
papeis, nunca como zona cinzenta.

---

# 6. ARQUITETURA FINAL RECOMENDADA

A camada final recomendada deve conter exatamente estes cinco agentes nucleares:

1. `ai-linguistic-reviewer`
2. `ai-documentation-writer`
3. `ai-documentation-reviewer`
4. `ai-documentation-manager`
5. `ai-documentation-sync`

Os papeis de suporte ja existentes devem continuar, mas com escopos ajustados e
fronteiras endurecidas para minimizar colisoes.

---

# 7. AGENTE NUCLEAR 1 -- `ai-linguistic-reviewer`

## 7.1. Identidade

- nome tecnico final: `ai-linguistic-reviewer`
- apelido preservado: `Pascoalete`
- base atual: evolucao formal do papel hoje exercido por `pascoalete`

## 7.2. Missao

Garantir qualidade linguistica e textual fina em qualquer superficie textual do
projeto.

## 7.3. Pergunta que responde

"O texto esta linguisticamente correto, claro, consistente e aderente ao guia
terminologico e de estilo do repo?"

## 7.4. Escopo dominante

- ortografia
- gramatica
- pontuacao
- sintaxe
- fluidez
- microcopy
- terminologia
- style guide enforcement
- consistencia linguistica
- ambiguidade textual local
- higiene de dicionario `cspell`
- revisao de:
  - docs Markdown
  - comentarios
  - docstrings
  - help texts
  - mensagens de erro
  - mensagens de warning
  - strings legiveis
  - descricoes textuais em configs
  - textos operacionais
  - titulos e descricoes quando houver componente linguistico relevante

## 7.5. Skills esperadas

- orthography review
- grammar review
- punctuation review
- sentence clarity
- terminology normalization
- microcopy refinement
- style-guide enforcement
- ambiguity detection at local sentence level
- technical orthography governance
- `cspell` governance
- bilingual consistency if applicable in future contexts

## 7.6. Inputs

- textos ou trechos textuais
- glossario oficial
- dicionario `cspell`
- guias de estilo
- convencoes terminologicas
- contexto do publico-alvo

## 7.7. Outputs

- texto linguisticamente corrigido
- findings linguisticos
- sugestoes terminologicas
- alertas de ambiguidade local
- parecer consultivo
- backlog consultivo quando restar pendencia nao corrigida

## 7.8. Limites duros

Este agente:

- nao escreve como owner do conteudo
- nao estrutura documento como papel principal
- nao gerencia acervo
- nao sincroniza
- nao publica
- nao salva
- nao decide placement
- nao decide source of truth
- nao decide lifecycle
- nao valida corretude tecnica
- nao aprova completude documental
- nao substitui reviewer tecnico
- nao substitui reviewer documental
- nao substitui manager documental
- nao substitui agente de sync

## 7.9. Regra anticolisao obrigatoria

- corretude tecnica de comments, docstrings, help e mensagens continua com o
  reviewer tecnico da familia
- completude, utilidade e risco semantico continuam com o reviewer documental
- placement, source of truth e lifecycle continuam com o manager documental
- save, publicacao, attachment, `documentation-link` e evidencias continuam com
  o agente de sync
- se houver ambiguidade com risco operacional, `ai-linguistic-reviewer` apenas
  sinaliza e escala
- este agente nunca deve voltar a absorver escrita, sync, save, publication ou
  governance

---

# 8. AGENTE NUCLEAR 2 -- `ai-documentation-writer`

## 8.1. Identidade

- nome tecnico final: `ai-documentation-writer`
- apelido preservado: `Escrivao`
- base atual: reaproveitamento da parte de escrita do antigo
  `ai-documentation-agent`

## 8.2. Missao

Escrever, reescrever, consolidar e estruturar texto sob demanda para qualquer
outro papel.

## 8.3. Pergunta que responde

"Como transformar este contexto em texto claro, util, rastreavel e aderente ao
padrao do projeto?"

## 8.4. Escopo dominante

- escrita de documentacao nova
- reescrita de documentacao existente
- consolidacao de conhecimento disperso
- transformacao de conhecimento tacito em conhecimento explicito
- adaptacao de conteudo a templates
- organizacao de explicacoes operacionais
- apoio de escrita para:
  - runbooks
  - playbooks
  - ADRs
  - docs de arquitetura
  - docs operacionais
  - textos maiores em comments
  - docstrings extensas
  - explicacoes estruturadas no Jira
  - textos para Confluence
  - consolidacoes de logs vivos em artefatos mais estaveis

## 8.5. Natureza operacional correta

Este agente deve ser tratado como **subagente auxiliar de escrita**, quase como
uma funcao de redacao a servico de outros papeis.

Exemplos corretos:

- `PO` usa o `Escrivao` para melhorar narrativa de issue
- `Arquiteto` usa o `Escrivao` para estruturar ADR
- `Devops` usa o `Escrivao` para redigir runbook
- `Manager documental` usa o `Escrivao` para consolidar uma pagina
- developer usa o `Escrivao` para reescrever texto maior quando o escopo sair
  do ajuste local simples

## 8.6. Skills esperadas

- technical writing
- structured writing
- process writing
- runbook writing
- ADR writing support
- information synthesis
- transformation of tacit knowledge into explicit documentation
- template-based writing
- audience-oriented writing
- consolidation of fragmented notes into maintainable documentation

## 8.7. Inputs

- contexto fornecido por outro agente
- rascunhos
- notas
- decisoes
- evidencias
- templates
- standards do repo
- destino previsto do artefato

## 8.8. Outputs

- rascunhos
- reescritas
- secoes estruturadas
- consolidacoes textuais
- versoes preparadas para review

## 8.9. Limites duros

Este agente:

- nao gerencia
- nao sincroniza
- nao publica
- nao salva
- nao fecha fluxo
- nao decide placement
- nao decide source of truth
- nao decide lifecycle
- nao assume ownership do contexto
- nao aprova conteudo
- nao revisa tecnicamente como papel principal
- nao revisa linguisticamente como papel principal
- nao registra `documentation-link`
- nao anexa bundles
- nao executa publication pipeline
- nao cria nem altera semantica da fundacao de sync

## 8.10. Transparencia operacional

Mesmo sendo subagente auxiliar, ele pode se manifestar no chat quando executar
sua parte, para manter transparencia do processo.

## 8.11. Regra anticolisao obrigatoria

- o agente chamador continua dono do contexto
- o agente chamador continua dono da decisao
- o agente chamador continua dono do destino
- o agente chamador continua dono do save
- o agente chamador continua dono do sync
- o agente chamador continua dono da publicacao
- o agente chamador continua dono do fechamento
- `ai-documentation-writer` so redige
- este agente nunca deve recuperar responsabilidades de sync, publication,
  save, bundle ownership ou traceability closure

---

# 9. AGENTE NUCLEAR 3 -- `ai-documentation-reviewer`

## 9.1. Identidade

- nome tecnico final: `ai-documentation-reviewer`
- base atual recomendada: novo papel dedicado

## 9.2. Missao

Revisar a qualidade documental e textual em nivel estrutural, semantico e
operacional.

## 9.3. Pergunta que responde

"Este artefato esta correto, completo, coerente, util, aderente ao padrao e
seguro para uso?"

## 9.4. Escopo dominante

- completude
- clareza global
- consistencia entre secoes
- adequacao ao publico
- utilidade operacional
- aderencia a templates e standards documentais
- precisao de instrucoes, exemplos, comandos e fluxos
- validacao de que comments/docstrings/strings representam corretamente o
  comportamento esperado no nivel documental e operacional
- classificacao de findings bloqueantes e nao bloqueantes

## 9.5. Skills esperadas

- documentation review
- completeness analysis
- consistency analysis
- audience adequacy review
- ambiguity detection at document level
- documentation risk review
- operational safety review for instructions and commands
- documentation severity classification
- readiness evaluation

## 9.6. Inputs

- texto preparado para revisao
- contexto tecnico
- contexto operacional
- templates e standards
- publico-alvo
- artefatos relacionados
- decisoes do manager documental quando placement/lifecycle/source of truth
  forem relevantes

## 9.7. Outputs

- parecer documental
- findings documentais
- bloqueios documentais
- debt documental nao bloqueante
- recomendacao de aprovacao ou retorno

## 9.8. Limites duros

Este agente:

- nao governa o acervo
- nao decide sozinho placement
- nao decide sozinho source of truth
- nao faz sync
- nao publica
- nao salva como responsabilidade dominante
- nao substitui reviewer tecnico da familia
- nao substitui linguistic reviewer
- nao escreve como papel principal
- nao substitui `ai-reviewer-config-policy` na camada declarativa/estrutural

## 9.9. Regra anticolisao obrigatoria

- `ai-reviewer-config-policy` continua reviewer estrutural/declarativo
- `ai-reviewer` continua gate transversal
- `Tech Lead` continua aprovador final de fluxo tecnico
- `ai-documentation-reviewer` e o owner da revisao documental semantica,
  estrutural e operacional

---

# 10. AGENTE NUCLEAR 4 -- `ai-documentation-manager`

## 10.1. Identidade

- nome tecnico final: `ai-documentation-manager`
- base atual recomendada: novo papel dedicado, com interface forte com
  `Curador Repo`

## 10.2. Missao

Governar o sistema documental como produto vivo.

## 10.3. Pergunta que responde

"Esta informacao esta no lugar certo, com owner certo, lifecycle certo, sem
duplicidade, sem conflito e com source of truth explicita?"

## 10.4. Escopo dominante

- taxonomia documental
- source of truth
- placement repo vs Jira vs Confluence vs logs vivos
- lifecycle
- ownership documental
- deduplicacao
- obsolescencia
- consolidacao de backlog documental
- politica de sincronizacao documental
- governanca de logs vivos
- Definition of Done documental
- impacto documental de mudancas em codigo, processo, policy e automacao
- classificacao documental alinhada a fundacao de sync

## 10.5. Skills esperadas

- documentation governance
- information architecture
- source-of-truth management
- documentation placement strategy
- lifecycle management
- deduplication
- obsolescence detection
- cross-surface conflict detection
- documentation backlog curation
- live-log governance
- change-impact analysis for documentation
- sync eligibility classification for documentation artifacts

## 10.6. Inputs

- inventario documental
- estrutura do repo
- contexto Jira/Confluence
- artefatos dos outros agentes
- politicas do repo
- mudancas em processo, sistema ou operacao
- fundacao e manifest de sync existentes

## 10.7. Outputs

- decisoes de placement
- matriz de source of truth
- politica de lifecycle
- backlog documental
- alertas de conflito
- alertas de duplicidade
- alertas de obsolescencia
- ownership e classificacao do acervo
- decisoes de consolidacao e sync
- politica de acionamento do agente de sync
- decisao sobre se o artefato documental:
  - permanece canonico no repo
  - vira candidato a runtime ledger sincronizavel
  - nao e elegivel para sync remoto

## 10.8. Limites duros

Este agente:

- nao e writer primario
- nao e linguistic reviewer
- nao e reviewer documental primario
- nao substitui `Curador Repo` em higiene de contrato local
- nao substitui `Scrum Master` em fiscalizacao de processo
- nao substitui `PO` em backlog de produto
- nao substitui `Arquiteto` em ownership de conteudo tecnico de arquitetura
- nao executa publication/sync como seu papel dominante
- nao redefine a infraestrutura-base do prompt foundation

## 10.9. Regra anticolisao obrigatoria

- `Curador Repo` governa o plano repo-local, links, contracts e organizacao
  local
- `ai-documentation-manager` governa a malha documental cross-surface, source
  of truth, placement, lifecycle e policy documental de sync
- `Curador Repo` nao deve absorver sozinho a governanca cross-surface
- `ai-documentation-manager` nao deve absorver sozinho a governanca de
  contracts gerais do repo
- `ai-documentation-sync` executa a sync/persistencia; o manager decide o que
  deve ser sincronizado
- a fundacao de sync continua definindo o protocolo, a semantica do outbox e a
  infraestrutura-base

---

# 11. AGENTE NUCLEAR 5 -- `ai-documentation-sync`

## 11.1. Identidade

- nome tecnico final: `ai-documentation-sync`
- base atual recomendada: extraido da parte operacional do antigo
  `ai-documentation-agent`

## 11.2. Missao

Executar o sincronismo, a persistencia e a rastreabilidade operacional da
camada documental entre repo, Jira e Confluence, sempre obedecendo as decisoes
do manager documental, o conteudo aprovado pelas camadas de escrita/revisao e a
arquitetura-base definida pelo prompt foundation de sync.

## 11.3. Pergunta que responde

"O que precisa ser criado, atualizado, anexado, linkado, espelhado, registrado
e evidenciado nas superficies corretas, e isso ja foi executado corretamente
segundo a fundacao oficial de sync?"

## 11.4. Escopo dominante

- executar sync repo <-> Jira <-> Confluence dentro da arquitetura oficial de
  outbox/sync
- publicar ou atualizar paginas quando isso ja estiver decidido
- publicar ou atualizar comentarios estruturados documentais
- registrar `documentation-link`
- garantir backlinks
- anexar bundles e artefatos
- refletir evidencias de publicacao e sync
- garantir que o artefato aprovado e o artefato efetivamente publicado
- confirmar a materializacao da trilha documental cross-surface
- gravar e consumir eventos conforme o foundation quando isso couber ao fluxo
  documental
- respeitar o manifest `sync-targets.yaml` em [`config/ai/`](../../../../config/ai/)
  como manifest oficial

## 11.5. Skills esperadas

- documentation sync execution
- backlink management
- cross-surface traceability
- Confluence publication operations
- Jira documentation comment operations
- attachment and bundle handling
- documentation-link enforcement
- sync verification
- publication evidence capture
- foundation-aligned outbox execution

## 11.6. Inputs

- decisao de placement e source of truth do manager documental
- artefato escrito/revisado/aprovado
- contexto Jira/Confluence
- policy documental de sync
- requisitos de evidencias e backlinks
- contratos da fundacao de sync
- o manifest `sync-targets.yaml` em [`config/ai/`](../../../../config/ai/)

## 11.7. Outputs

- pagina criada/atualizada
- comentario criado/atualizado
- attachment anexado
- `documentation-link` registrado
- backlinks conferidos
- evidencias de sync materializadas
- eventos de sync processados conforme a fundacao oficial

## 11.8. Limites duros

Este agente:

- nao decide source of truth
- nao decide placement
- nao decide lifecycle
- nao escreve como papel principal
- nao revisa qualidade documental
- nao revisa linguagem
- nao governa repo-local contracts
- nao substitui `Curador Repo`
- nao substitui manager documental
- nao redefine conteudo aprovado
- nao redefine `workspace_id`
- nao redefine `runtime_environment_id`
- nao redefine `ack`, retry, `dead-letter`, `retention_policy` ou estrutura do
  outbox
- nao cria manifest paralelo de sync

## 11.9. Regra anticolisao obrigatoria

- manager documental decide
- writer redige
- linguistic reviewer revisa linguagem
- documentation reviewer revisa qualidade documental
- sync agent executa publication, linkage, attachment, `documentation-link`,
  persistencia operacional e evidence
- este agente resolve a lacuna de "quem fecha operacionalmente a trilha
  documental"
- este agente consome a fundacao de sync; nao compete com ela

---

# 12. AJUSTES OBRIGATORIOS NOS AGENTES EXISTENTES PARA MINIMIZAR COLISOES

## 12.1. `pascoalete`

Transformar formalmente em `ai-linguistic-reviewer`, preservando o apelido
`Pascoalete`.

Ajustes obrigatorios:

- manter escopo apenas de revisao linguistica
- explicitar que nao escreve
- explicitar que nao gerencia
- explicitar que nao sincroniza
- explicitar que nao publica
- explicitar que nao salva
- explicitar que nao revisa corretude tecnica
- explicitar que nao aprova completude documental

## 12.2. `ai-documentation-agent`

O antigo papel deve ser formalmente decomposto em dois:

- `ai-documentation-writer`
- `ai-documentation-sync`

Ajustes obrigatorios:

- mover escrita e consolidacao textual para `ai-documentation-writer`
- mover `documentation-link`, save, publication, backlinks, attachments e sync
  para `ai-documentation-sync`
- remover do antigo papel qualquer concentracao ambigua de escrita +
  governance + sync
- manter compatibilidade transicional apenas se necessario, com sunset
  explicito

## 12.3. `repo-governance-authority` / `Curador Repo`

Ajustar contrato para deixar claro:

- continua dono da higiene repo-local
- continua dono de links internos/externos no plano do repo
- continua dono de contracts, catalogos e organizacao local
- nao vira dono integral da malha documental cross-surface
- nao absorve sozinho source of truth para Confluence/Jira/logs vivos
- nao e fundido ao `ai-documentation-sync`
- continua sendo owner de linkagem repo-local, enquanto o sync documental
  responde por `documentation-link` e backlinks cross-surface

## 12.4. `ai-reviewer-config-policy`

Ajustar contrato para deixar claro:

- continua reviewer estrutural/declarativo
- continua cobrindo Markdown governado, YAML, JSON, TOML, schemas e compliance
- nao vira reviewer documental semantico principal
- nao substitui o `ai-documentation-reviewer`

## 12.5. `ai-reviewer`

Ajustar contrato para deixar claro:

- continua gate transversal
- continua consolidando reviews especializados
- continua avaliando paridade cross-cutting
- nao vira reviewer documental default
- nao substitui `ai-documentation-reviewer`

## 12.6. `ai-tech-lead`

Ajustar contrato para deixar claro:

- continua aprovador final de PR/origem equivalente
- continua arbitro tecnico
- nao vira writer
- nao vira linguistic reviewer
- nao vira documentation manager
- nao vira documentation sync
- nao vira reviewer documental default

## 12.7. `ai-scrum-master`

Ajustar contrato para deixar claro:

- continua fiscalizando aderencia do processo
- pode cobrar compliance documental
- nao decide source of truth
- nao decide placement
- nao decide lifecycle
- nao decide taxonomia documental
- nao executa sync documental

## 12.8. `ai-product-owner`

Ajustar contrato para deixar claro:

- continua dono do backlog e narrativa da issue
- pode acionar `Escrivao` para melhorar narrativa
- nao vira owner da documentacao canonica
- nao substitui writer documental como papel proprio

## 12.9. `ai-engineering-architect`

Ajustar contrato para deixar claro:

- continua owner do conteudo tecnico de arquitetura
- pode usar `Escrivao` para estruturar texto
- nao perde ownership tecnico
- nao se torna manager documental
- nao se torna sync owner

## 12.10. Reviewers tecnicos de familia

Ajustar contratos de:

- `ai-reviewer-python`
- `ai-reviewer-powershell`
- `ai-reviewer-automation`

Para deixar claro:

- continuam donos da corretude tecnica de docstrings, comments, help e
  mensagens locais ao codigo
- `ai-linguistic-reviewer` revisa linguagem
- `ai-documentation-reviewer` entra apenas quando houver impacto documental ou
  operacional mais amplo

---

# 13. ROTEAMENTO DECISORIO

## 13.1. Quando chamar `ai-linguistic-reviewer`

Chamar quando o problema principal for:

- ortografia
- gramatica
- pontuacao
- sintaxe
- fluidez
- terminologia
- microcopy
- ambiguidade textual local
- consistencia linguistica

## 13.2. Quando chamar `ai-documentation-writer`

Chamar quando o problema principal for:

- escrever texto novo
- reescrever texto existente
- consolidar notas em documento
- estruturar explicacao
- transformar contexto em artefato textual
- ajudar outro agente a redigir melhor

## 13.3. Quando chamar `ai-documentation-reviewer`

Chamar quando o problema principal for:

- verificar completude
- verificar clareza global
- verificar utilidade operacional
- verificar consistencia
- verificar se o texto esta seguro para uso
- classificar findings documentais

## 13.4. Quando chamar `ai-documentation-manager`

Chamar quando o problema principal for:

- decidir onde o conteudo deve viver
- decidir fonte canonica
- decidir lifecycle
- evitar duplicidade
- evitar conflito entre superficies
- definir policy documental de sync
- governar logs vivos
- avaliar impacto documental no DoD
- classificar elegibilidade documental para sync remoto

## 13.5. Quando chamar `ai-documentation-sync`

Chamar quando a pergunta principal for:

- o que precisa ser salvo, publicado, anexado ou atualizado?
- qual comentario documental precisa ser registrado?
- qual backlink ou `documentation-link` precisa ser materializado?
- o que precisa ser refletido no Jira ou Confluence?
- a sync e a trilha documental operacional foram realmente executadas?
- o fluxo documental precisa materializar um evento, `ack` ou registro conforme
  a fundacao oficial?

## 13.6. Quando chamar reviewer tecnico da familia

Chamar reviewer tecnico quando a pergunta principal for:

- o texto embutido no codigo esta tecnicamente correto?
- a docstring corresponde ao comportamento real?
- a mensagem de erro, warning ou help esta alinhada ao comportamento do sistema?
- o texto local ao codigo ainda representa o contrato real?

## 13.7. Quando chamar `ai-reviewer-config-policy`

Chamar quando a pergunta principal for:

- o artefato declarativo esta correto?
- o schema esta aderente?
- o Markdown governado esta estruturalmente correto?
- os links e references estao consistentes?
- a compliance declarativa esta integra?

## 13.8. Quando chamar `ai-reviewer`

Chamar quando a pergunta principal for:

- os reviewers corretos foram acionados?
- existe risco cross-cutting?
- existe paridade entre repo, Jira, Confluence e fluxo?
- a decisao final precisa consolidar achados de varias frentes?

## 13.9. Quando chamar `ai-tech-lead`

Chamar quando a pergunta principal for:

- quem arbitra este conflito tecnico?
- o PR/origem equivalente pode ser aprovado?
- qual o handoff tecnico correto?
- como resolver uma ambiguidade de fronteira tecnica entre papeis?

## 13.10. Quando chamar `ai-scrum-master`

Chamar quando a pergunta principal for:

- o processo esta sendo seguido?
- existe drift de ownership, WIP, comments ou board?
- a camada documental foi seguida?
- ha anomalia de fluxo ou compliance?

---

# 14. ROTEAMENTO ESPECIFICO ENTRE `ai-documentation-reviewer` E `ai-reviewer-config-policy`

## 14.1. Chamar apenas `ai-documentation-reviewer` quando

- o artefato for principalmente prosa, documentacao, guia, runbook ou playbook
- a pergunta principal for completude, clareza, utilidade e seguranca de uso
- nao houver componente estrutural declarativo relevante alem do normal

## 14.2. Chamar apenas `ai-reviewer-config-policy` quando

- o artefato for principalmente YAML, JSON, TOML ou schema
- a pergunta principal for sintaxe, schema, compliance, links, frontmatter ou
  integridade declarativa
- nao houver necessidade de avaliacao documental semantica mais ampla

## 14.3. Chamar ambos em paralelo quando

- o artefato for Markdown governado com componente declarativo forte
- houver frontmatter, contracts, metadata, links, schemas ou compliance
  estrutural
- e tambem houver necessidade de avaliar completude, utilidade, publico e
  risco semantico

Esta fronteira deve ficar declarada em contracts, routing policy e docs de
operacao.

---

# 15. CLASSIFICACAO DOCUMENTAL ALINHADA AO PROMPT FOUNDATION

Toda superficie textual ou documental relevante deve ser classificada pelo
`ai-documentation-manager`, alinhada ao modelo do prompt foundation, em tres
grupos:

## 15.1. Grupo 1 -- Permanece canonico e versionado no repo

Usar para:

- docs tecnicas versionadas
- contracts
- policies
- prompts
- cards
- skills
- docstrings/comments cuja fonte canonica seja o proprio codigo
- artefatos cujo valor canonico depende do Git

## 15.2. Grupo 2 -- Candidato a runtime ledger sincronizavel

Usar para:

- trilhas documentais cross-surface
- certos comentarios estruturados do Jira
- certos registros perenes de review, `documentation-link` e evidencia
- certos logs vivos promovidos para historico remoto
- artefatos documentais cujo historico perene deve viver em superficie remota
  segundo o foundation

## 15.3. Grupo 3 -- Nao elegivel para sync remoto

Usar para:

- artefatos efemeros
- observacoes transitorias
- logs locais de baixa relevancia historica
- rascunhos locais sem valor perene
- redundancias que nao merecem publicacao remota

Nenhuma migracao ou sync documental pode ocorrer sem esta classificacao.

---

# 16. OWNERSHIP POR SUPERFICIE

## 16.1. Docs Markdown versionadas

- placement, source of truth e lifecycle: `ai-documentation-manager`
- escrita: `ai-documentation-writer`
- revisao documental: `ai-documentation-reviewer`
- revisao linguistica: `ai-linguistic-reviewer`
- review estrutural/compliance quando aplicavel: `ai-reviewer-config-policy`
- save/publicacao cross-surface quando aplicavel: `ai-documentation-sync`
- governanca repo-local, links e contracts: `Curador Repo`

## 16.2. Comments em codigo

- owner do contexto: developer/reviewer tecnico da familia
- escrita auxiliar quando houver reescrita maior: `ai-documentation-writer`
- revisao linguistica: `ai-linguistic-reviewer`
- revisao documental quando houver impacto operacional mais amplo:
  `ai-documentation-reviewer`
- corretude tecnica: reviewer tecnico da familia
- sync: nao aplicavel por default

## 16.3. Docstrings

- owner do contexto: developer/reviewer tecnico da familia
- escrita auxiliar quando houver reescrita estrutural: `ai-documentation-writer`
- revisao linguistica: `ai-linguistic-reviewer`
- revisao documental quando houver impacto operacional, onboarding ou contrato
  mais amplo: `ai-documentation-reviewer`
- corretude tecnica: reviewer tecnico da familia
- sync: nao aplicavel por default

## 16.4. Help texts

- owner do contexto: developer/reviewer tecnico da familia
- escrita auxiliar: `ai-documentation-writer`
- revisao linguistica: `ai-linguistic-reviewer`
- revisao documental quando o help tiver impacto operacional relevante:
  `ai-documentation-reviewer`
- corretude tecnica: reviewer tecnico da familia
- sync: nao aplicavel por default

## 16.5. Mensagens

Inclui:

- mensagens de erro
- warning
- mensagens ao usuario
- strings legiveis de operacao

Ownership:

- owner do contexto tecnico: developer/reviewer tecnico da familia
- escrita auxiliar: `ai-documentation-writer`
- revisao linguistica: `ai-linguistic-reviewer`
- revisao documental quando a mensagem tiver papel operacional ou documental
  relevante: `ai-documentation-reviewer`
- corretude tecnica: reviewer tecnico da familia
- sync: nao aplicavel por default

## 16.6. Jira comments

- owner do contexto: agente executor da issue
- escrita auxiliar, se necessario: `ai-documentation-writer`
- revisao linguistica, se fizer sentido: `ai-linguistic-reviewer`
- revisao documental quando o comment materializar instrucao, decision log ou
  artefato documental relevante: `ai-documentation-reviewer`
- manager documental entra quando houver impacto de source of truth, placement
  ou lifecycle
- `ai-documentation-sync` executa comment update ou publication quando isso
  fizer parte da trilha documental oficial
- `documentation-link` operacional pertence ao `ai-documentation-sync`

## 16.7. Confluence pages

- placement, source of truth e lifecycle: `ai-documentation-manager`
- escrita: `ai-documentation-writer`
- revisao documental: `ai-documentation-reviewer`
- revisao linguistica: `ai-linguistic-reviewer`
- owner do conteudo tecnico, quando aplicavel, permanece com o papel de
  dominio correspondente
- publicacao, update, backlinks e evidencia: `ai-documentation-sync`
- a publicacao deve obedecer a fundacao de sync quando o artefato for elegivel
  ao fluxo oficial

## 16.8. Logs vivos

- policy, consolidacao e lifecycle: `ai-documentation-manager`
- owner do tracker operacional: role operacional correspondente
- consolidacao textual em artefato mais estavel: `ai-documentation-writer`
- revisao linguistica: `ai-linguistic-reviewer`
- revisao documental quando houver promocao para doc canonica:
  `ai-documentation-reviewer`
- publication/backlinks quando houver promocao cross-surface:
  `ai-documentation-sync`

## 16.9. `documentation-link`, backlinks e evidencias de sync

- decisao sobre necessidade: `ai-documentation-manager`
- materializacao operacional: `ai-documentation-sync`
- conteudo textual associado, quando necessario: `ai-documentation-writer`
- revisao semantica do conteudo associado, quando relevante:
  `ai-documentation-reviewer`
- revisao linguistica do conteudo associado, quando relevante:
  `ai-linguistic-reviewer`

## 16.10. Manifest `sync-targets.yaml` em [`config/ai/`](../../../../config/ai/)

- infraestrutura-base e semantica geral: prompt foundation
- classificacao e necessidades documentais que exijam entradas novas:
  `ai-documentation-manager`
- atualizacao estrutural/compliance do manifest: `ai-reviewer-config-policy`
- execucao operacional a partir do manifest: `ai-documentation-sync`

---

# 17. POLICY DE NAO SOBREPOSICAO

As seguintes regras sao obrigatorias e devem ser incorporadas nos contracts:

- `ai-linguistic-reviewer` nunca escreve como owner
- `ai-documentation-writer` nunca gerencia, publica, sincroniza ou salva como
  ownership funcional
- `ai-documentation-reviewer` nunca substitui reviewer tecnico da familia
- `ai-documentation-manager` nunca substitui writer ou reviewer como papel
  dominante
- `ai-documentation-sync` nunca decide source of truth, placement ou lifecycle
- `ai-reviewer-config-policy` nunca substitui o reviewer documental semantico
- `ai-reviewer` nunca substitui todos os reviewers especializados
- `ai-tech-lead` nunca substitui writer, linguistic reviewer, reviewer
  documental, manager documental ou sync documental
- `ai-scrum-master` nunca decide placement, source of truth ou lifecycle
- `PO` nunca vira owner da documentacao canonica
- `Arquiteto` continua owner do conteudo tecnico de arquitetura
- reviewers tecnicos continuam donos da corretude tecnica do texto embutido no
  codigo
- a fundacao de sync continua dona do protocolo/base de sincronismo; a camada
  documental nao a reimplementa

---

# 18. POLICY DE ESCALACAO

- erro linguistico simples -> `ai-linguistic-reviewer`
- ambiguidade textual com risco de interpretacao -> `ai-linguistic-reviewer`
  sinaliza + `ai-documentation-reviewer` classifica
- texto tecnicamente incorreto em codigo -> reviewer tecnico da familia
- texto documental incompleto ou inseguro -> `ai-documentation-reviewer`
- conflito entre repo e Confluence -> `ai-documentation-manager`
- duvida de placement, source of truth ou lifecycle -> `ai-documentation-manager`
- necessidade de publicacao, update, backlinks, attachment ou
  `documentation-link` -> `ai-documentation-sync`
- conflito de ownership, handoff ou fluxo -> `ai-scrum-master`
- conflito tecnico final ou aprovacao de PR -> `ai-tech-lead`

---

# 19. POLICY DE SOURCE OF TRUTH

Formalize explicitamente que:

- repo e fonte canonica de:
  - docs tecnicas versionadas
  - contracts
  - cards
  - skills
  - prompts
  - policies
  - comments, docstrings e texto local ao codigo quando a superficie canonica
    for o proprio codigo
- Confluence e superficie oficial de:
  - navegacao cross-surface
  - hubs documentais
  - consolidacao institucional
  - espelhos estruturados quando a policy mandar
  - certos historicos perenes elegiveis segundo o prompt foundation
- Jira e fonte canonica de:
  - fluxo vivo
  - ownership
  - handoffs
  - comments estruturados
  - backlog
  - evidencias operacionais
- logs vivos sao:
  - memoria operacional
  - trilha incremental
  - nunca substituto silencioso de documentacao estavel

Quando houver conteudo em mais de uma superficie, a fonte canonica precisa
ficar explicita.

---

# 20. POLICY PARA DOCSTRINGS, COMMENTS, HELP E STRINGS

A camada final deve cobrir oficialmente:

- docstrings
- comments inline
- comments de bloco
- help texts
- mensagens de erro
- warning texts
- strings de usuario
- descricoes textuais em configuracao
- texto legivel em tasks/workflows quando materializar contrato ou operacao

Regras minimas:

- mudanca de comportamento em codigo exige avaliacao de impacto textual
- comments redundantes ou enganosos devem ser removidos ou corrigidos
- docstrings nao podem divergir do comportamento real
- help text nao pode divergir da operacao real
- reviewer tecnico valida corretude
- linguistic reviewer valida linguagem
- documentation reviewer valida utilidade e risco documental quando aplicavel
- documentation writer apoia reescrita quando necessario
- documentation manager define quando um texto deixa de ser apenas local e passa
  a exigir policy documental
- documentation sync atua apenas se houver reflexo cross-surface real e
  elegivel ao fluxo oficial

---

# 21. POLICY PARA LOGS VIVOS

Formalize explicitamente:

- quando log vivo e permitido
- quando log vivo deve ser consolidado
- como separar log operacional de doc canonica
- quem decide a promocao do conhecimento
- quem governa lifecycle do log
- como evitar crescimento caotico
- como cross-linkar log e doc canonica
- quando o log precisa virar page, comment, artifact ou runbook
- quando o log passa a ser elegivel ao fluxo do prompt foundation

O owner do tracker operacional nao pode ser absorvido pelo manager documental.
O manager documental define a policy; o owner operacional continua dono do
tracker.

---

# 22. POLICY DE TERMINOLOGIA E ORTOGRAFIA

A implementacao deve incluir:

- glossario vivo
- politica terminologica
- politica de sinonimos aceitaveis e proibidos
- politica de `cspell`
- criterio de quando adicionar palavra nova
- criterio de quando achado consultivo continua consultivo
- criterio de quando ambiguidade linguistica vira blocker documental

Regra importante:

`ai-linguistic-reviewer` continua consultivo por natureza, mas qualquer problema
semantico com risco operacional deve ser escalado para classificacao bloqueante
pelo `ai-documentation-reviewer` ou pelo reviewer tecnico apropriado.

---

# 23. POLICY DE LIFECYCLE

Formalize lifecycle explicito com no minimo:

- Draft
- Active
- Deprecated
- Superseded
- Archived

Para cada status, definir:

- quando entra
- quem decide
- como sai
- como aponta substituto
- como sinaliza obsolescencia
- como evita consulta acidental do conteudo errado
- como isso se aplica a repo, Confluence, logs vivos e artefatos textuais
  embutidos

---

# 24. POLICY DE SEVERIDADE DOS FINDINGS

Padronizar findings em pelo menos:

- bloqueante
- nao bloqueante
- debt/backlog
- nit linguistico

### Regra importante de mapeamento

- erro puramente linguistico sem risco operacional -> consultivo
- ambiguidade que pode gerar interpretacao errada -> escalacao obrigatoria
- instrucoes incompletas ou incorretas -> bloqueante documental
- comment/docstring/help tecnicamente divergente -> bloqueante tecnico da
  familia
- placement errado, duplicidade critica ou source of truth conflitante ->
  bloqueante de governanca documental
- sync faltando, backlink faltando ou `documentation-link` ausente quando
  obrigatorio -> bloqueante de sincronismo documental

---

# 25. TASK PRINCIPAL E SUBTASKS NO JIRA

Criar a task principal com o titulo exato definido no topo.

Subtasks minimas:

1. Formalizar `ai-linguistic-reviewer` a partir de `Pascoalete`
2. Formalizar `ai-documentation-writer` a partir do `Escrivao`
3. Criar `ai-documentation-reviewer`
4. Criar `ai-documentation-manager`
5. Criar `ai-documentation-sync`
6. Declarar a dependencia formal deste prompt em relacao ao prompt foundation de
   sync
7. Ajustar o antigo `ai-documentation-agent` para decomposicao formal
8. Ajustar `Curador Repo` para fronteira repo-local explicita
9. Ajustar `ai-reviewer-config-policy` para limite estrutural/declarativo
   explicito
10. Ajustar `ai-reviewer` para papel transversal explicito
11. Ajustar `Tech Lead`, `Scrum Master`, `PO` e `Arquiteto` para endurecer
    fronteiras
12. Formalizar ownership por superficie
13. Formalizar source of truth
14. Formalizar policy para comments/docstrings/help/strings
15. Formalizar policy para logs vivos
16. Formalizar policy de terminologia e `cspell`
17. Formalizar lifecycle documental
18. Formalizar policy de severidade
19. Atualizar routing policy e capability matrix
20. Atualizar cards, registry, contracts e docs
21. Ajustar tasks, validators, ledgers e testes
22. Validar compatibilidade com o manifest `sync-targets.yaml` em
    [`config/ai/`](../../../../config/ai/)
23. Validar compatibilidade e fechar backlog residual

---

# 26. GATES E VALIDACOES OBRIGATORIOS

A implementacao final deve se integrar aos gates reais do repo.

No minimo:

- `task ai:startup:session`
- `task ai:worklog:check`
- `task docs:check`
- `task spell:dictionary:audit`
- `task spell:review`
- `task ai:review:record`
- `task ai:review:check`
- `task ai:validate`
- `task ai:eval:smoke`
- `task ci:workflow:sync:check`
- `task ai:lessons:check`
- `task ai:worklog:close:gate`

Tambem ajustar os revisores especializados da familia correspondente sempre que
houver codigo.

Quando a rodada tocar a integracao com a fundacao de sync, validar tambem:

- coerencia com o manifest `sync-targets.yaml` em [`config/ai/`](../../../../config/ai/)
- nao duplicacao de contracts de sync
- nao criacao de outbox paralelo
- compatibilidade com o state root e semantica definidos pelo foundation

---

# 27. ARTEFATOS QUE DEVEM SER AJUSTADOS

A implementacao deve refletir esta arquitetura em:

- cards
- registry
- skills
- contracts
- policies
- capability matrix
- routing policy
- ledgers
- docs catalogo
- tasks
- validators
- testes
- comments types e docs operacionais relacionados
- referencias formais ao prompt foundation de sync
- o manifest `sync-targets.yaml` em [`config/ai/`](../../../../config/ai/)
  quando houver necessidade documental real de novas entradas

---

# 28. ANTI-PATTERNS A EVITAR

- criar uma segunda malha paralela de agentes documentais
- fundir este prompt com o prompt foundation de sync
- deixar `Pascoalete` voltar a escrever ou gerir
- deixar `Escrivao` voltar a gerenciar, sincronizar, publicar ou salvar
- deixar o agente de sync decidir source of truth
- deixar o agente documental redefinir `workspace_id`, `runtime_environment_id`,
  outbox ou protocolo de `ack`
- deixar `ai-reviewer-config-policy` virar reviewer documental total
- deixar `ai-reviewer` virar reviewer generico default da camada documental
- deixar `Tech Lead` absorver review documental por inercia
- deixar `Scrum Master` decidir source of truth, placement ou lifecycle
- deixar `PO` virar owner da documentacao canonica
- deixar reviewers tecnicos perderem ownership sobre corretude tecnica do texto
  embutido no codigo
- deixar logs vivos virarem documentacao estavel por inercia
- duplicar corpo completo entre repo e Confluence sem fonte canonica explicita
- fundir `Curador Repo` com `ai-documentation-sync`
- criar manifest documental de sync paralelo ao foundation

---

# 29. RESULTADO ESPERADO

Ao final, o repositorio deve ter uma camada documental em que:

- `Pascoalete` e o reviewer linguistico oficial
- `Escrivao` e o writer auxiliar oficial
- exista um reviewer documental explicito
- exista um manager documental explicito
- exista um agente de sync documental explicito
- papeis de suporte nao colidam com a camada nuclear
- o roteamento fique deterministico
- ownership por superficie fique explicito
- source of truth fique explicita
- lifecycle fique explicito
- comments, docstrings, help e strings passem a fazer parte da governanca
  oficial
- a sync e a trilha operacional de publication, backlinks e `documentation-link`
  fiquem explicitamente owned
- a camada documental consuma a fundacao oficial de sync, sem competir com ela
- o fluxo fique claro o bastante para nao haver duvida sobre qual agente deve
  fazer o que

---

# 30. INSTRUCAO FINAL PARA O CODEX

Implemente exatamente esta arquitetura.

Nao reabrir a decisao de `Pascoalete` como `ai-linguistic-reviewer`.
Nao reabrir a decisao de `Escrivao` como `ai-documentation-writer`.
Nao permitir que esses dois papeis recuperem responsabilidades de gestao, sync,
publicacao, save ou ownership indevido.
Nao fundir `Curador Repo` com `ai-documentation-sync`.
Nao fundir este prompt documental com o prompt foundation de sync.
Nao criar arquitetura paralela de sincronismo.

A implementacao deve refletir esta arquitetura em:

- cards
- registry
- skills
- contracts
- policies
- capability matrix
- routing policy
- ledgers
- docs catalogo
- tasks
- validators
- testes

A meta principal e eliminar ao maximo colisoes, ambiguidades e duvidas na hora
de saber qual agente deve fazer o que, preservando a fundacao oficial de sync
como camada base.
