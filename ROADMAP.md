# Roadmap do Repositorio

Atualizado em: 2026-03-10 14:17 UTC
Ciclo ativo: 2026-Q1

Planejamento incremental para qualidade, testes, bootstrap e governanca do repo.

## Guardrails

- Toda sugestao aceita deve gerar rastreabilidade no mesmo ciclo.
- Pendencias mantidas devem aparecer em [`docs/AI-WIP-TRACKER.md`](docs/AI-WIP-TRACKER.md) e no roadmap.
- Priorizacao automatica ajuda a ordenar, mas a decisao final continua humana.

## Backlog Mestre

Edite apenas a tabela entre os marcadores abaixo.

<!-- roadmap:backlog:start -->
| ID | Tipo | Iniciativa | R | I | C | E | BV | TC | RR | JS | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| RM-001 | feat | Harness Linux para bootstrap e relink | 400 | 2.6 | 0.8 | 8 | 8 | 7 | 6 | 5 | in_progress |
| RM-002 | feat | Harness Windows real em CI | 380 | 2.8 | 0.7 | 13 | 9 | 8 | 7 | 8 | in_progress |
| RM-003 | governance | Governanca de worklog e roadmap com enforcement | 320 | 2.4 | 0.85 | 5 | 9 | 7 | 8 | 4 | done |
<!-- roadmap:backlog:end -->

## Priorizacao Automatica

Atualizada por `task ai:roadmap:refresh`.

<!-- roadmap:priority:start -->
Atualizado em: 2026-03-10 14:17 UTC

### Ranking RICE

| Rank | ID | Status | RICE |
| --- | --- | --- | --- |
| 1 | RM-001 | in_progress | 104.00 |
| 2 | RM-002 | in_progress | 57.29 |

### Ranking WSJF

| Rank | ID | Status | WSJF |
| --- | --- | --- | --- |
| 1 | RM-001 | in_progress | 4.20 |
| 2 | RM-002 | in_progress | 3.00 |

### Referencia de IDs

- `RM-001` [feat]: Harness Linux para bootstrap e relink
- `RM-002` [feat]: Harness Windows real em CI

### Sequencia Recomendada

1. `RM-001` - Harness Linux para bootstrap e relink
2. `RM-002` - Harness Windows real em CI

### Governanca de Sugestoes

Sem sugestoes pendentes neste ciclo; itens aceitos ja estao rastreaveis.
<!-- roadmap:priority:end -->

## Horizonte de Entrega

### Now

<!-- roadmap:now:start -->
- [fix] Corrigir ACL e ownership indevidos de C:\Users\pablo\.ssh\config, removendo principals orfaos ou nao permitidos que hoje quebram ssh no Windows e no WSL via /mnt/c. | notas=P0 imediato: bug operacional confirmado localmente. Impacta acesso SSH real, validacao de Git/SSH, signer tecnico, rotacao de secrets e q...
- [ops] Resolver o bloqueio operacional de assinatura Git/1Password para permitir checkpoint commit sem interrupcao, preferindo signer tecnico de automacao por worktree/repo e preservando signer humano fora da worktree tecnica. | notas=Prioridade 0 operacional: destravar commit checkpoint em modo automacao, sem intervencao humana, antes de encerrar a rodada atual.
- [fix] Corrigir pendencias ortograficas remanescentes do worklog WIP-20260307-SECRETS-ROTATION com o Pascoalete, incluindo higiene do dicionario cspell, ledger consultivo e backlog automatico quando nao houver correcao automatica. | notas=Prioridade 0 operacional: fechar os ajustes remanescentes do Pascoalete antes de avancar para a proxima fase tecnica da rotacao de secrets.
- [security] Implementar o modulo de rotacionamento automatizado de secrets, chaves SSH, tokens e artefatos sops+age, com tarefas isoladas e task unificada, blue/green, validacao pos-rotacao, auditoria cifrada, notificacao e orquestracao segura por op, gh, glab, ssh-agent e demais CLIs criticos. | notas=Demanda explicita do usuario; deve manter 1Password como source of truth, evitar plaintext e garantir continuidade operacional apos a troca.
- Expandir datasets e cenarios de eval para bootstrap cross-platform, seguranca e risco operacional. | notas=Fase adicional apos o fechamento do core de rotacao; a base smoke ja existe, mas faltam cenarios mais pesados e regressao especifica de secrets/bootstrap.
- RM-001 - expandir o harness Linux de relink para bootstrap full com stubs de auth e secrets
- RM-002 - estabilizar o harness Windows no runner hospedado e ampliar cobertura alem de relink
<!-- roadmap:now:end -->

### Next

<!-- roadmap:next:start -->
- [fix] Corrigir pendencias ortograficas remanescentes do worklog `DOT-115` em .agents/cards/ai-engineering-manager.md, .agents/cards/ai-scrum-master.md, .agents/config.toml, .agents/ev... | notas=Pendencia automatica criada por Pascoalete apos review consultivo reprovado sem correcao automatica.
- [fix] Corrigir pendencias ortograficas remanescentes do worklog `DOT-128` em bootstrap/bootstrap-config.ps1, bootstrap/bootstrap-ubuntu-wsl.sh, bootstrap/user-config.yaml.tpl, config/... | notas=Pendencia automatica criada por Pascoalete apos review consultivo reprovado sem correcao automatica.
- [fix] Corrigir pendencias ortograficas remanescentes do worklog `DOT-127` em .agents/cards/governador-continuidade-wip.md, .agents/cards/orquestrador-delegacao.md, .agents/skills/task... | notas=Pendencia automatica criada por Pascoalete apos review consultivo reprovado sem correcao automatica.
- [fix] Corrigir pendencias ortograficas remanescentes do worklog `DOT-117` em config/ai/agent-operations.yaml, config/ai/agents.yaml, config/ai/jira-model.yaml, config/ai/reviewer-poli... | notas=Pendencia automatica criada por Pascoalete apos review consultivo reprovado sem correcao automatica.
- [fix] Corrigir pendencias ortograficas remanescentes do worklog `DOT-114` em scripts/ai-atlassian-agent-comment-audit.py, scripts/ai-atlassian-backfill.py, scripts/ai_atlassian_agent_... | notas=Pendencia automatica criada por Pascoalete apos review consultivo reprovado sem correcao automatica.
- [fix] Corrigir pendencias ortograficas remanescentes do worklog `WIP-20260307-ATLASSIAN-ADAPTERS` em docs/TASKS.md, docs/atlassian-ia/2026-03-07-diagnostico-auth-e-acesso-atlassian.md... | notas=Pendencia automatica criada por Pascoalete apos review consultivo reprovado sem correcao automatica.
- [fix] Corrigir pendencias ortograficas remanescentes do worklog `WIP-20260307-ATLASSIAN-ADAPTERS` em docs/AI-WIP-TRACKER.md, docs/atlassian-ia/2026-03-07-diagnostico-auth-e-acesso-atl... | notas=Pendencia automatica criada por Pascoalete apos review consultivo reprovado sem correcao automatica.
- [fix] Corrigir pendencias ortograficas remanescentes do worklog `WIP-20260307-ATLASSIAN-ADAPTERS` em Taskfile.yml, config/ai/confluence-model.yaml, config/ai/jira-model.yaml, docs/TAS... | notas=Pendencia automatica criada por Pascoalete apos review consultivo reprovado sem correcao automatica.
- [improvement] Redesenhar a estrategia de cache de secrets 1Password do runtime dos dotfiles para resolver secrets na borda da sessao e evitar leituras repetidas a cada abertura de terminal. | notas=Conclusao estrutural derivada do incidente de rate limit da service account do 1Password na trilha Atlassian; a camada de runtime do repo...
- [fix] Corrigir pendencias ortograficas remanescentes do worklog `WIP-20260307-ATLASSIAN-ADAPTERS` em config/ai/confluence-model.yaml, docs/atlassian-ia/2026-03-07-atlassian-auth-scope... | notas=Pendencia automatica criada por Pascoalete apos review consultivo reprovado sem correcao automatica.
- [fix] Corrigir pendencias ortograficas remanescentes do worklog `WIP-20260307-ATLASSIAN-ADAPTERS` em config/ai/confluence-model.yaml, docs/atlassian-ia/artifacts/atlassian-endpoints.m... | notas=Pendencia automatica criada por Pascoalete apos review consultivo reprovado sem correcao automatica.
- [fix] Corrigir pendencias ortograficas remanescentes do worklog `WIP-20260307-ATLASSIAN-ADAPTERS` em ROADMAP.md, docs/ROADMAP-DECISIONS.md, docs/atlassian-ia/2026-03-07-parecer-e-plan... | notas=Pendencia automatica criada por Pascoalete apos review consultivo reprovado sem correcao automatica.
- [fix] Corrigir pendencias ortograficas remanescentes do worklog `WIP-20260307-ATLASSIAN-ADAPTERS` em config/ai/agent-operations.yaml, config/ai/contracts.yaml, config/ai/jira-model.ya... | notas=Pendencia automatica criada por Pascoalete apos review consultivo reprovado sem correcao automatica.
- [governance] Endurecer a governanca perene de comentarios explicativos em arquivos de configuracao e contratos, exigindo documentacao inline ou referencia explicita para campos nao obvios; r... | notas=Gap observado pelo usuario em config/secrets-rotation.yaml; o contrato atual ainda nao esta rigido o suficiente para impedir YAMLs e conf...
- [fix] Corrigir pendencias ortograficas remanescentes do worklog `WIP-20260307-ATLASSIAN-ADAPTERS` em Taskfile.yml, config/ai/agents.yaml, config/ai/contracts.yaml, config/ai/jira-mode... | notas=Pendencia automatica criada por Pascoalete apos review consultivo reprovado sem correcao automatica.
- [fix] Corrigir pendencias ortograficas remanescentes do worklog `WIP-20260307-ATLASSIAN-ADAPTERS` em ROADMAP.md, docs/ROADMAP-DECISIONS.md, docs/atlassian-ia/2026-03-07-atlassian-prod... | notas=Pendencia automatica criada por Pascoalete apos review consultivo reprovado sem correcao automatica.
- [fix] Corrigir pendencias ortograficas remanescentes do worklog `WIP-20260307-ATLASSIAN-IA-CONTEXT` em docs/atlassian-ia/2026-03-07-modelo-operacional-completo-figma-seo.md, docs/atla... | notas=Pendencia automatica criada por Pascoalete apos review consultivo reprovado sem correcao automatica.
- [fix] Corrigir pendencias ortograficas remanescentes do worklog `WIP-20260307-ATLASSIAN-IA-CONTEXT` em .agents/cards/guardiao-rotacao-secrets.md, LICOES-APRENDIDAS.md, docs/README.md,... | notas=Pendencia automatica criada por Pascoalete apos review consultivo reprovado sem correcao automatica.
- [fix] Corrigir pendencias ortograficas remanescentes do worklog `WIP-20260307-ATLASSIAN-IA-CONTEXT` em docs/README.md, docs/ai-operating-model.md, docs/atlassian-ia/2026-03-07-bluepri... | notas=Pendencia automatica criada por Pascoalete apos review consultivo reprovado sem correcao automatica.
- [governance] Criar historico versionado de planos sugeridos, aprovados e implementados em docs/plans/, com arquivo por plano contendo data-hora, resumo do plano e status atual no nome e no c... | notas=Demanda aprovada pelo usuario. Manter por enquanto em docs/, com naming canonico orientado a historico e rastreabilidade; quando o item d...
- [feat] Integrar `Atlassian Product Discovery` como camada opcional de intake e discovery upstream do `Jira`, permitindo que ideias do `AI Product Owner` e de outros agentes nascam ali antes da promocao oficial para issue executavel. | notas=Contrato alvo: `Product Discovery` como backlog de oportunidade/hipotese; `Jira` segue fonte canonica do backlog executavel e o `AI Product Owner` continua como promotor exclusivo das issues principais.
- [fix] Padronizar datas, horas, locale e idioma de docs, scripts, agentes, workflows e logs para respeitar a configuracao canonica do repo e eliminar timestamps hardcoded em UTC quando o contrato exigir locale configurado. | notas=Proxima prioridade imediata apos concluir as prioridades 0 da rodada atual: signer tecnico em modo automacao e ajustes remanescentes do Pascoalete.
- [improvement] Executar a auditoria e o endurecimento de .vscode para parear extensoes, settings, suporte a tipos de arquivo e UX do workspace com os fluxos canonicos de qualidade, CI/CD, testes, secrets e automacao do repo. | notas=Prioridade 3 aprovada pelo usuario; manter abaixo das prioridades 0, da normalizacao de locale/timezone e da retomada tecnica do rotacionador de secrets.
- [governance] Tornar obrigatorio que todo revisor especializado use toda a stack de qualidade, lint, tipagem, testes e validacoes disponivel para sua familia de arquivo; quando faltar cobertu... | notas=Diretriz perene do usuario. Relaciona-se a expansao da malha de revisores e a auditoria de .vscode, mas merece rastreabilidade propria: c...
- [ops] Criar governanca e automacao de limpeza de artefatos efemeros do repo, garantindo remocao de worktrees, branches temporarias, pastas e arquivos de teste, outputs gerados e demai... | notas=Demanda prioritaria do usuario. Diferenciar de arquivamento de legado versionado: aqui o foco e lifecycle cleanup de residuos efemeros ge...
- [refactor] Rever toda a arvore [docs/](docs/) e reestruturá-la por semantica operacional, separando documentacao de referencia, contratos, catalogos, auditorias, notas e registradores vivo... | notas=Auditoria rapida da arvore atual confirmou mistura de categorias em docs: contratos, catalogos, ledgers operacionais, auditoria, notas e...
- [refactor] Mover o arquivo [LICOES-APRENDIDAS.md](LICOES-APRENDIDAS.md) para a pasta [docs/](docs/) e alinhar todos os contratos, scripts, tasks e validadores para a nova localizacao canon... | notas=Demanda registrada pelo usuario. Tratar como ajuste estrutural de governanca documental, com migracao assistida, links atualizados, parid...
- [feat] Expandir a malha de revisores especialistas para cobrir arquivos/configuracoes ainda sem gate dedicado, incluindo YAML/YML, JSON, Markdown, TOML, artefatos sops+age, gitconfig,... | notas=Gap confirmado na rodada atual: hoje os revisores obrigatorios cobrem Python, PowerShell e automacao, mas nao ha gate especializado dedic...
- [governance] Consolidar os revisores especialistas por familia de arquivo como capacidade entregue e, depois, ampliar a cobertura com criterios formais de aprovacao/reprovacao por linguagem quando surgirem novas familias relevantes. | notas=Prioridade 1 ja entrou na rodada atual; manter aqui apenas o follow-up estrutural apos o fechamento do primeiro corte.
- [feat] Formalizar o ambiente de desenvolvimento em [`.devcontainer/`](.devcontainer/) e reorganizar a camada Docker do repo, aposentando ou movendo o [Dockerfile](Dockerfile) legado da raiz para uma convencao coerente com [docker/](docker/). | notas=Demanda aprovada pelo usuario; deve alinhar Taskfile, docs, ambiente dev e harnesses para uma estrutura canonica unica.
- [refactor] Decidir formalmente a fronteira de [df/assets/img/](df/assets/img/) entre runtime canonico, fontes de design e conteudo a arquivar em [archive/](archive/). | notas=Aprovado como item proprio para reduzir ambiguidade entre ativos de runtime, design-fonte e legado historico.
- [refactor] Reavaliar a fronteira da pasta [scripts/](scripts/) entre camadas cli e lib, agora que a base Python com uv esta formalizada. | notas=Decisao estrutural aprovada para reduzir acoplamento, facilitar testes e deixar entrypoints mais claros.
- [governance] Expandir a cobertura de governanca de IA agora que signer tecnico, sync workflow-task-doc e intake declarativo ja foram entregues. | notas=Os itens de signer tecnico, validate_workflow_task_sync e chat-intake/route/delegate ja sairam do backlog ativo; os follow-ups futuros devem nascer como refinamentos, nao como trabalho ainda “nao feito”.
- [refactor] Consolidar ou arquivar o legado historico versionado que nao e fonte canonica, incluindo artefatos hoje ja movidos para [`archive/`](archive/) e outros scripts experimentais ou backups decl... | notas=Reduzir ruido conceitual, diminuir superficie de manutencao e deixar explicita a fronteira entre referencia historica e runtime canonico.
- [feat] Criar tasks/CLIs ai:status, ai:diff, ai:sync e ai:backup para configs de IA materializadas no HOME, com fallback copy-vs-symlink por ferramenta. | notas=Inspirado em jppferguson/dotfiles e basnijholt/dotfiles; ajuda a preservar contratos ao trocar de assistente sem drift entre repo e HOME.
- [feat] Gerar adaptadores de assistentes e arquivos MCP a partir de uma fonte canonica unica em .agents, separando escopo global do usuario e escopo do repo. | notas=Inspirado em atxtechbro/dotfiles, basnijholt/dotfiles e na documentacao oficial do Claude Code; reduz drift entre Claude, Codex, Gemini e...
- [feat] Adicionar hooks e policies de IA com presets de permissao por contexto, bloqueio de segredos e comandos destrutivos, e validacoes proporcionais ao risco. | notas=Inspirado em joshukraine/dotfiles e nos hooks/settings do Claude Code; fortalece seguranca operacional e reduz regressao silenciosa em ta...
<!-- roadmap:next:end -->

### Later

<!-- roadmap:later:start -->
- [improvement] Adicionar telemetria de esforco por agente e por etapa da demanda, cobrindo pesquisa, analise, arquitetura, desenvolvimento, revisao, testes e documentacao, para medir eficienci... | notas=Demanda aprovada pelo usuario para v2. Implementar como telemetria canonica do control plane, independente de dotfiles runtime, com possi...
- [refactor] Evoluir o piloto para um monolito modular em Python com pacotes importaveis por dominio, mantendo scripts como wrappers finos e deixando extracao seletiva para microservicos com... | notas=Baseado em pesquisa registrada em docs/atlassian-ia/2026-03-07-python-modular-architecture-research.md e na premissa de que este repo ser...
- [feat] Criar uma camada de conhecimento global portavel para IA, separada do contexto especifico do repo, para materializacao controlada no HOME. | notas=Inspirado em atxtechbro/dotfiles e no modelo de memory/imports do Claude Code; util para padroes cross-repo sem misturar memoria global c...
<!-- roadmap:later:end -->

## Sugestoes pendentes de decisao

<!-- roadmap:pending:start -->
- (sem itens)
<!-- roadmap:pending:end -->

## Riscos e bloqueios

- Bootstrap full ainda depende de 1Password, gh, sops e layout real de OneDrive; faltam stubs e fixtures para PR CI barato.
- Harness Windows cobre relink isolado em perfil temporario; bootstrap completo com auth real segue fora deste ciclo.
