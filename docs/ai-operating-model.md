# AI Operating Model

## Objetivo

Criar uma camada local de IA que seja:

- versionada
- reutilizavel
- testavel
- curta e especifica
- segura para operar em worktree, CI e uso manual

## Principios

### 1. Instrucoes claras e curtas

As instrucoes base devem ser pequenas, diretas e estaveis. O papel de [`AGENTS.md`](AGENTS.md) e alinhar linguagem, guardrails e fontes de verdade; os detalhes operacionais ficam nas skills e referencias.

### 1.1. Retomada do zero exige releitura integral de governanca

Quando a sessao voltar sem continuidade confiavel, a IA nao pode depender de
memoria residual nem de "contexto provavel".

Nessas retomadas, a regra correta passa a ser:

- reler integralmente todos os arquivos resolvidos por
  [`AI-STARTUP-GOVERNANCE-MANIFEST.md`](AI-STARTUP-GOVERNANCE-MANIFEST.md)
- tratar o manifest como fonte canonica do que precisa ser relido
- nao operar por amostragem, presuncao ou lembranca parcial de sessao antiga
- recalcular branches e worktrees abertas antes de tentar drenar uma worktree
  suja ou redistribuir alteracoes entre trilhas Jira
- consultar [`AI-CHAT-CONTRACTS-REGISTER.md`](AI-CHAT-CONTRACTS-REGISTER.md)
  para listar contratos do chat ainda nao promovidos
- gerar o relatorio operacional de retomada com `task ai:startup:session`

### 1.2. Contratos nascidos no chat precisam de registrador vivo

Nem toda definicao nasce primeiro em doc oficial. Quando isso acontecer:

- o contrato nasce no chat, mas nao pode morrer so ali
- enquanto ainda nao virar governanca oficial, ele deve entrar em
  [`AI-CHAT-CONTRACTS-REGISTER.md`](AI-CHAT-CONTRACTS-REGISTER.md)
- toda nova sessao precisa avisar o usuario se houver itens pendentes nesse
  registrador
- cada item pendente deve apontar para o **work item** dono quando ele ja
  existir

### 2. Especializacao por escopo

Cada skill cobre um dominio estreito do repo. Isso reduz ambiguidade, evita prompts gigantes e melhora a reusabilidade em tarefas futuras.

### 3. Iteracao guiada por validacao

Prompts, skills e fluxos de agentes devem ser tratados como codigo: versao, review e validacao automatica. Mudanca sem avaliacao de saida aumenta regressao silenciosa.

### 3.1. Terminar antes de comecar inclui destravar o WIP ativo

No fluxo agil deste repo, a leitura do **board** continua da direita para a
esquerda e a regra central continua sendo terminar antes de comecar.

Quando um item ja iniciado estiver bloqueado por outra issue, a IA pode puxar o
**work item** desbloqueador, mas apenas se ele for a menor unidade que destrava
diretamente esse WIP ativo.

Isso nao abre permissao para puxar demanda nova desconectada. A semantica de
`concluir_primeiro` passa a ser concluir ou destravar primeiro.

### 3.2. Priorizacao continua e timeline sao responsabilidade perene do **Product Owner**

No modelo deste repo, o backlog oficial vive no `Jira`. Isso significa que o
`AI Product Owner` nao atua apenas em intake e refinamento pontual; ele precisa
manter continuamente:

- `Backlog`, `Refinement` e `Ready` ordenados por prioridade real
- cada demanda nova posicionada no ponto correto da fila
- `Start date` e `Due date` atualizados para itens acima de `Sub-task`

Essa manutencao sustenta:

- timeline coerente
- roadmap confiavel
- planejamento de entregas
- leitura honesta da capacidade atual do fluxo

Sem essa rotina, a fila deixa de representar prioridade real e o **board**
perde valor como instrumento de gestao.

### 4. Automacao reutilizavel

A automacao deve morar em scripts, tasks e workflows reutilizaveis. Isso reduz duplicacao e facilita evoluir CI/CD sem espalhar logica em varios pontos.

### 4.1. Toda execucao local relevante precisa ter agente e issue explicitos

Quando uma rodada local estiver realmente em execucao, o repo precisa manter um
contexto ativo canonico em `.cache/ai/active-execution.json`
com:

- issue Jira ativa
- agente responsavel pela execucao atual
- status real da rodada
- branch e worktree usadas

Esse contexto local nao substitui o Jira; ele existe para impedir operacao
anonima entre o que acontece no repo, o que fica comentado no Jira e o que
chega ao chat. Em handoff, pausa ou `Done`, o contexto local deve ser limpo.

### 4.2. Assinatura Git humana e tecnica devem ser separadas

Quando a automacao local precisar gerar commits, a worktree deve usar signer
tecnico dedicado via `config.worktree`, com chave privada mantida no 1Password
SSH Agent e chave publica sincronizada por `op`/`gh`. O signer humano continua
como padrao fora da worktree tecnica e nao deve ser desativado por "bypass"
global de assinatura.

### 4.3. Referencias documentais sempre linkadas quando o formato permitir

Em Markdown e comentarios com suporte a links clicaveis, referencias internas a
arquivos, pastas, tasks, workflows e scripts do repo, bem como referencias
externas viaveis, devem apontar para o alvo explicitamente. Texto solto ou
apenas inline code abre espaco para drift, quebra de navegacao e documentacao
menos auditavel. Paths locais fora do repo podem permanecer em inline code
somente quando nao houver destino clicavel razoavel no proprio repositorio.

### 5. Auditoria exaustiva antes de reuso cross-repo

Quando a tarefa envolver importar, adaptar, comparar ou consolidar contratos de outro repo, a IA nao pode trabalhar por amostragem.

Cobertura minima obrigatoria da auditoria:

- contratos globais
- docs e catalogos
- tasks, taskfiles e aliases
- scripts e CLIs
- workflows, hooks e gates
- validadores e testes
- agentes, skills e metadata
- orquestracao, rules e evals
- relacoes entre esses elementos

Sem essa auditoria, o risco e alto de trazer governanca quebrada, testes incompletos, docs sem backend real ou duplicacao de contratos.

## Arquitetura local

### Camada 1. Contrato global

- [`AGENTS.md`](AGENTS.md)
- [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md)
- [`CONTEXT.md`](CONTEXT.md)
- [`docs/test-strategy.md`](docs/test-strategy.md)
- [`docs/ai-operating-model.md`](docs/ai-operating-model.md)
- [`AI-WIP-TRACKER.md`](AI-WIP-TRACKER.md)
- [`../ROADMAP.md`](../ROADMAP.md)
- [`ROADMAP-DECISIONS.md`](ROADMAP-DECISIONS.md)

### Camada 2. Skills do repo

As skills ficam em [`.agents/skills/`](.agents/skills/) e seguem o contrato:

- `SKILL.md` curto e acionavel
- `agents/openai.yaml` com metadata reutilizavel
- `references/` para detalhes que nao precisam poluir o prompt principal

Prompt packs versionados tambem devem viver em [`.agents/prompts/`](.agents/prompts/), inclusive
material historico, pesquisas e pacotes de contexto usados em auditorias.

### Camada 2.1. Registry declarativo do repo

Os agentes tipados ficam em [`.agents/registry/`](.agents/registry/) e definem:

- `id` estavel do papel
- `purpose` e `triggers`
- skills padrao
- contrato de saida
- handoffs e gates obrigatorios

### Camada 2.2. Orquestracao, rules e evals

Para evitar roteamento implcito e drift entre docs e execucao, o repo tambem versiona:

- [`.agents/orchestration/`](.agents/orchestration/) para capability matrix, routing policy e schemas
- [`.agents/rules/`](.agents/rules/) para guardrails declarativos de operacao e CI
- [`.agents/evals/`](.agents/evals/) para cenarios e datasets minimos de regressao

### Camada 2.3. Cerimonias versionadas

As **cerimonias** ageis do time ficam em [`.agents/cerimonias/`](.agents/cerimonias/)
com:

- schema declarativo da **cerimonia**
- definicoes por ritual, como a **Retrospectiva**
- templates e contratos dos logs de execucao

### Camada 3. Cartoes de agentes

Os papeis operacionais ficam em [`.agents/cards/`](.agents/cards/). Cada cartao define:

- objetivo
- quando usar
- entradas
- saidas
- fluxo
- guardrails
- criterio de conclusao

Esses cartoes funcionam como prompt-base para subagentes humanos ou de IA.

### Fronteira entre [`.agents/`](.agents/) e adaptadores de assistente

Para evitar ambiguidades e drift:

- [`.agents/`](.agents/) e a fonte canonica de contratos, skills, registry, orchestration, rules e evals
- [`.codex/`](.codex/) no repo guarda apenas um [`README.md`](README.md) de compatibilidade apontando para [`.agents/`](.agents/)
- adaptadores especificos de assistente devem ser gerados a partir de [`.agents/`](.agents/), nunca mantidos manualmente em paralelo
- runtime local de IA continua fora do Git

### Camada 4. Validacao

[`scripts/validate-ai-assets.ps1`](scripts/validate-ai-assets.ps1) valida:

- frontmatter das skills
- metadata dos agentes
- estrutura minima de [`.agents/cards/`](.agents/cards/)
- estrutura minima de [`.agents/registry/`](.agents/registry/)
- presenca de [`.agents/config.toml`](.agents/config.toml)
- presenca de [`.agents/README.md`](.agents/README.md)
- presenca de [`.codex/README.md`](.codex/README.md)
- presenca de orchestration, rules e evals
- estrutura minima dos cartoes
- presenca dos docs estruturais de WIP
- presenca do contrato de licoes aprendidas
- presenca do ledger vivo de revisao especializada
- presenca do inventario versionado de auditoria cross-repo
- coerencia minima do contrato de auditoria exaustiva
- ausencia de placeholders e `TODO`

[`scripts/validate_docs.py`](scripts/validate_docs.py) valida:

- links locais quebrados
- referencias internas do repo sem link explicito nos Markdown governados
- referencias externas viaveis sem link explicito nos Markdown governados
- cobertura da camada documental ativa do repo, incluindo `README`, [`docs/`](docs/),
  [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md) e [`.agents/`](.agents/) ativos

### Camada 5. Automacao

- `task ai:validate`
- `task ai:chat:intake`
- `task ai:route`
- `task ai:delegate`
- `task ai:review:required`
- `task ai:review:record`
- `task ai:review:check`
- `task ai:eval:smoke`
- `task ai:lessons:check`
- `task ai:rules:check`
- `task ai:install:codex`
- `task ai:worklog:check`
- `task ai:worklog:close:gate`
- `task ci:workflow:sync:check`
- workflow `AI Governance`

`task ai:worklog:check` tambem atua como guardrail de commit checkpoint entre
rodadas: se a worktree estiver suja e nao houver item ativo em `Doing`, a
proxima rodada deve ser bloqueada ate existir commit do contexto anterior.

Quando houver WIP ativo, o mesmo preflight precisa tratar `concluir_primeiro`
como concluir ou puxar somente o **work item** minimo que destrava o que ja
esta em curso.

### Camada 6. Catalogos e fluxo

Os catalogos humanos versionados ficam em:

- [`docs/AI-AGENTS-CATALOG.md`](docs/AI-AGENTS-CATALOG.md)
- [`docs/AI-SKILLS-CATALOG.md`](docs/AI-SKILLS-CATALOG.md)
- [`docs/AI-DELEGATION-FLOW.md`](docs/AI-DELEGATION-FLOW.md)
- [`docs/AI-GOVERNANCE-AND-REGRESSION.md`](docs/AI-GOVERNANCE-AND-REGRESSION.md)
- [`docs/atlassian-ia/README.md`](docs/atlassian-ia/README.md) para contexto,
  pareceres, planos e rastreabilidade da trilha Atlassian + IA

Esses documentos nao sao "marketing" do sistema; eles sao contratos de operacao e precisam refletir o estado real da camada declarativa.

O gate global de **Scrum Master** faz parte dessa camada: ele precisa existir na
orquestracao, nos catalogos, nas evals e nos contratos para fiscalizar
continuamente **board**, **WIP**, ownership, comunicacao e **cerimonias**.
Sua efetividade minima fica rastreada no
[`docs/AI-SCRUM-MASTER-LEDGER.md`](AI-SCRUM-MASTER-LEDGER.md).

## Politica de leitura do board

O **board** canonico e lido da direita para a esquerda:
**Done** <- **Review** <- **Testing** <- **Doing** <- **Ready** <-
**Refinement** <- **Backlog**.

A regra operacional e **comecar a terminar**: antes de puxar algo novo de
**Ready** ou **Backlog**, o time precisa tentar mover o item mais a direita com
avanco real possivel.

Quando houver agentes ociosos:

- o **Scrum Master** identifica o item mais a direita destravavel
- o **Engenheiro** coordena capacidade, ownership e redistribuicao
- so sem possibilidade real de avancar para a direita e permitido puxar novo
  trabalho

## Camada de identidade humana dos agentes

A identidade humana oficial de um agente nasce em
[`.agents/registry/`](.agents/registry/), no campo `display_name`.

O titulo `# ...` do card funciona como espelho humano obrigatorio desse nome de
exibicao quando ele existir.

Sem `display_name`, o fallback de exibicao continua sendo o id tecnico do
agente.

Toda rotina de startup e restart precisa carregar essa camada antes de iniciar
comunicacao com o usuario, espelhar marcos no chat ou decidir como exibir um
papel em logs e artefatos.

Quando a superficie do `Jira` permitir exibicao humana sem perder
rastreabilidade tecnica, o fluxo deve preferir `display_name`; quando nao
permitir, o id tecnico permanece como chave interna e o nome humano fica na
camada visivel correspondente.

## Politica de versionamento

### Versionar

- [`AGENTS.md`](AGENTS.md)
- [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md)
- [`.agents/`](.agents/) e sua arvore declarativa
- [`docs/AI-SOURCE-AUDIT.md`](docs/AI-SOURCE-AUDIT.md)
- [`docs/AI-REVIEW-LEDGER.md`](docs/AI-REVIEW-LEDGER.md)
- [`docs/AI-SCRUM-MASTER-LEDGER.md`](docs/AI-SCRUM-MASTER-LEDGER.md)
- [`docs/atlassian-ia/README.md`](docs/atlassian-ia/README.md) e os arquivos
  desta trilha quando houver estudos, contextos ou planos da camada Atlassian + IA
- [`AI-WIP-TRACKER.md`](AI-WIP-TRACKER.md)
- [`../ROADMAP.md`](../ROADMAP.md)
- [`ROADMAP-DECISIONS.md`](ROADMAP-DECISIONS.md)
- prompts e docs declarativos do repo
- templates estaveis que precisem ser materializados pelo bootstrap

### Nao versionar

- `.gemini/`
- sessoes, historico, caches, bancos sqlite e memoria local
- perfis de navegador
- tokens, auth, cookies, state files e configuracoes geradas por login
- artefatos locais de ferramentas fora da arvore canonica [`.agents/`](.agents/)

## Decisao sobre `~/.gemini`

Com base na estrutura local inspecionada, `~/.gemini` mistura:

- browser profile
- historico de conversas
- estado interno do agente
- arquivos gerados por execucao

Isso torna a pasta inadequada como fonte de verdade do repo. O que faz sentido versionar e somente a camada declarativa e portavel, por exemplo um `GEMINI.md` mantido no repo e depois materializado no `HOME` por bootstrap. A pasta inteira nao deve entrar no Git.

## Estrutura no repo

Como [`df/`](df/) guarda apenas o que sera utilizado na maquina apos o bootstrap, os artefatos de governanca do projeto ficam fora dele. Neste repo:

- [`AGENTS.md`](AGENTS.md) define o contrato global do projeto
- [`.agents/cards/`](.agents/cards/) guarda cartoes versionados de agentes
- [`.agents/skills/`](.agents/skills/) guarda skills versionadas do projeto
- [`.agents/prompts/`](.agents/prompts/) guarda prompt packs versionados e historico de contexto
- [`.agents/registry/`](.agents/registry/), [`.agents/orchestration/`](.agents/orchestration/), [`.agents/rules/`](.agents/rules/) e [`.agents/evals/`](.agents/evals/) guardam a camada declarativa
- [`.agents/cerimonias/`](.agents/cerimonias/) guarda as definicoes e templates das **cerimonias** ageis
- [`.codex/README.md`](.codex/README.md) deixa explicito que adaptadores de assistente nao sao fonte de verdade
- [`AI-WIP-TRACKER.md`](AI-WIP-TRACKER.md) guarda o estado incremental do trabalho de IA
- [`docs/AI-REVIEW-LEDGER.md`](docs/AI-REVIEW-LEDGER.md) guarda os pareceres vivos de revisao especializada por worklog
- [`config/ai/`](config/ai/) guarda a control plane dev-time de plataformas,
  contratos e optionalidade dos agentes, desacoplada de [`bootstrap/`](bootstrap/)
  e de [`df/`](df/)
- [`df/`](df/) continua reservado aos dotfiles e assets materializados no ambiente

## Estrategia de evolucao

1. Manter [`AGENTS.md`](AGENTS.md) curto.
2. Criar skills pequenas e especializadas.
3. Acionar gates paralelos de arquitetura/modernizacao e integracoes criticas nas analises substantivas.
4. Empurrar detalhes para `references/`.
5. Validar mudancas em CI.
6. Tratar [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md) como contrato revisado a cada fechamento de worklog.
7. Reusar workflows e tasks sempre que possivel.
8. Auditar exaustivamente antes de importar governanca de outro repo.

## Fontes

- [OpenAI Prompting](https://platform.openai.com/docs/guides/prompting)
- [OpenAI Evals](https://platform.openai.com/docs/guides/evals)
- [OpenAI Evaluation Best Practices](https://platform.openai.com/docs/guides/evaluation-best-practices)
- [GitHub Actions reusable workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/reusing-workflow-configurations)
- [GitHub Actions avoiding duplication](https://docs.github.com/actions/concepts/workflows-and-actions/avoiding-duplication)
