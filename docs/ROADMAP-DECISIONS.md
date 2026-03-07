# Decisoes do Roadmap

Atualizado em: 2026-03-07 14:06 UTC
Ciclo ativo: 2026-Q1

Registro das decisoes humanas por ciclo e governanca de sugestoes.

## Registro de Sugestoes

Use status: `pendente`, `aceita`, `descartada`, `aplicar_depois`.

<!-- roadmap:suggestions:start -->
| ID | Descricao | Status | RM | Captura | Atualizacao |
| --- | --- | --- | --- | --- | --- |
| SG-WIP-20260307-VSCODE-WORKSPACE | Retomar tarefa pendente WIP-20260307-VSCODE-WORKSPACE: Auditar e alinhar extensoes e configuracoes do workspace .vscode com os fluxos de qualidade, CI/CD, tipos de arquivo e con... | pendente |  | 2026-03-07 | 2026-03-07 |
| SG-20260307-ASSETS-IMG | Decidir formalmente a fronteira de [df/assets/img/](../df/assets/img/) entre runtime canonico, fontes de design e conteudo a arquivar em [archive/](../archive/). | aceita |  | 2026-03-07 | 2026-03-07 |
| SG-20260307-SCRIPTS-SPLIT | Reavaliar a fronteira da pasta [scripts/](../scripts/) entre camadas cli e lib, agora que a base Python com uv esta formalizada. | aceita |  | 2026-03-07 | 2026-03-07 |
| SG-20260307-OPSIGN | Resolver o bloqueio operacional de assinatura Git/1Password para permitir checkpoint commit sem interrupcao, preferindo signer tecnico de automacao por worktree/repo e preservan... | aceita |  | 2026-03-07 | 2026-03-07 |
| SG-20260307-095316 | Criar uma camada de conhecimento global portavel para IA, separada do contexto especifico do repo, para materializacao controlada no HOME. | aceita |  | 2026-03-07 | 2026-03-07 |
| SG-20260307-095305 | Adicionar hooks e policies de IA com presets de permissao por contexto, bloqueio de segredos e comandos destrutivos, e validacoes proporcionais ao risco. | aceita |  | 2026-03-07 | 2026-03-07 |
| SG-20260307-095254 | Gerar adaptadores de assistentes e arquivos MCP a partir de uma fonte canonica unica em .agents, separando escopo global do usuario e escopo do repo. | aceita |  | 2026-03-07 | 2026-03-07 |
| SG-20260307-095241 | Criar tasks/CLIs ai:status, ai:diff, ai:sync e ai:backup para configs de IA materializadas no HOME, com fallback copy-vs-symlink por ferramenta. | aceita |  | 2026-03-07 | 2026-03-07 |
| SG-20260307-090831 | Consolidar ou arquivar o legado historico versionado que nao e fonte canonica, incluindo artefatos hoje ja movidos para `archive/` e outros scripts experimentais ou backups decl... | aceita |  | 2026-03-07 | 2026-03-07 |
| SG-20260307-041349-01 | Expandir datasets e cenarios de eval para bootstrap cross-platform, seguranca e risco operacional. | aceita |  | 2026-03-07 | 2026-03-07 |
| SG-20260307-041349 | Adicionar validadores dedicados de sincronismo entre workflows, tasks, docs, catalogos e ativos declarativos da IA. | aceita |  | 2026-03-07 | 2026-03-07 |
| SG-20260307-041348 | Importar chat-intake, route e delegate com backend real de roteamento declarativo para a camada canonica .agents. | aceita |  | 2026-03-07 | 2026-03-07 |
<!-- roadmap:suggestions:end -->

## Historico de Ciclos

<!-- roadmap:cycles:start -->
### Ciclo 2026-Q1 @ 2026-03-07 14:06 UTC

- Top sequencia recomendada: `RM-001, RM-002`
- Decisao final permanece humana.
- Acao de governanca: decidir pendencias antes de novo escopo amplo.
- Sugestoes pendentes no fechamento: `SG-WIP-20260307-VSCODE-WORKSPACE`
<!-- roadmap:cycles:end -->

## Registro automatico

<!-- roadmap:autolog:start -->
- 2026-03-07 14:06 UTC | decisao=pending | horizonte=next | item=Retomar tarefa pendente WIP-20260307-VSCODE-WORKSPACE: Auditar e alinhar extensoes e configuracoes do workspace .vscode com os fluxos de qualidade, CI/CD, tipos de arquivo e con... | notas=Tarefa pausada por prioridade aprovada para assinatura Git de automacao.
- 2026-03-07 13:47 UTC | decisao=pending | horizonte=next | item=Retomar a auditoria e o endurecimento de .vscode para parear extensoes e configuracoes da IDE com os fluxos canonicos de qualidade, CI/CD e tipos de arquivo do repo. | notas=Tarefa pausada por mudanca de prioridade do usuario para automacao de assinatura Git/1Password.
- 2026-03-07 13:45 UTC | decisao=accepted | horizonte=next | item=Decidir formalmente a fronteira de [df/assets/img/](../df/assets/img/) entre runtime canonico, fontes de design e conteudo a arquivar em [archive/](../archive/). | notas=Aprovado como item proprio para reduzir ambiguidade entre ativos de runtime, design-fonte e legado historico.
- 2026-03-07 13:45 UTC | decisao=accepted | horizonte=next | item=Reavaliar a fronteira da pasta [scripts/](../scripts/) entre camadas cli e lib, agora que a base Python com uv esta formalizada. | notas=Decisao estrutural aprovada para reduzir acoplamento, facilitar testes e deixar entrypoints mais claros.
- 2026-03-07 13:45 UTC | decisao=accepted | horizonte=now | item=Resolver o bloqueio operacional de assinatura Git/1Password para permitir checkpoint commit sem interrupcao, preferindo signer tecnico de automacao por worktree/repo e preservan... | notas=Bloqueio operacional atual; priorizar perfil de assinatura de automacao sem bypass da identidade humana.
- 2026-03-07 13:24 UTC | decisao=accepted | horizonte=next | item=Consolidar ou arquivar o legado historico versionado que nao e fonte canonica, incluindo artefatos hoje ja movidos para `archive/` e outros scripts experimentais ou backups decl... | notas=Reduzir ruido conceitual, diminuir superficie de manutencao e deixar explicita a fronteira entre referencia historica e runtime canonico.
- 2026-03-07 13:11 UTC | decisao=accepted | horizonte=next | item=Criar tasks/CLIs ai:status, ai:diff, ai:sync e ai:backup para configs de IA materializadas no HOME, com fallback copy-vs-symlink por ferramenta. | notas=Inspirado em jppferguson/dotfiles e basnijholt/dotfiles; ajuda a preservar contratos ao trocar de assistente sem drift entre repo e HOME.
- 2026-03-07 13:11 UTC | decisao=accepted | horizonte=next | item=Gerar adaptadores de assistentes e arquivos MCP a partir de uma fonte canonica unica em .agents, separando escopo global do usuario e escopo do repo. | notas=Inspirado em atxtechbro/dotfiles, basnijholt/dotfiles e na documentacao oficial do Claude Code; reduz drift entre Claude, Codex, Gemini e...
- 2026-03-07 13:11 UTC | decisao=accepted | horizonte=next | item=Adicionar hooks e policies de IA com presets de permissao por contexto, bloqueio de segredos e comandos destrutivos, e validacoes proporcionais ao risco. | notas=Inspirado em joshukraine/dotfiles e nos hooks/settings do Claude Code; fortalece seguranca operacional e reduz regressao silenciosa em ta...
- 2026-03-07 13:11 UTC | decisao=accepted | horizonte=later | item=Criar uma camada de conhecimento global portavel para IA, separada do contexto especifico do repo, para materializacao controlada no HOME. | notas=Inspirado em atxtechbro/dotfiles e no modelo de memory/imports do Claude Code; util para padroes cross-repo sem misturar memoria global c...
- 2026-03-07 09:53 UTC | decisao=pending | horizonte=later | item=Criar uma camada de conhecimento global portavel para IA, separada do contexto especifico do repo, para materializacao controlada no HOME. | notas=Inspirado em atxtechbro/dotfiles e no modelo de memory/imports do Claude Code; util para padroes cross-repo sem misturar memoria global c...
- 2026-03-07 09:53 UTC | decisao=pending | horizonte=next | item=Adicionar hooks e policies de IA com presets de permissao por contexto, bloqueio de segredos e comandos destrutivos, e validacoes proporcionais ao risco. | notas=Inspirado em joshukraine/dotfiles e nos hooks/settings do Claude Code; fortalece seguranca operacional e reduz regressao silenciosa em ta...
- 2026-03-07 09:52 UTC | decisao=pending | horizonte=next | item=Gerar adaptadores de assistentes e arquivos MCP a partir de uma fonte canonica unica em .agents, separando escopo global do usuario e escopo do repo. | notas=Inspirado em atxtechbro/dotfiles, basnijholt/dotfiles e na documentacao oficial do Claude Code; reduz drift entre Claude, Codex, Gemini e...
- 2026-03-07 09:52 UTC | decisao=pending | horizonte=next | item=Criar tasks/CLIs ai:status, ai:diff, ai:sync e ai:backup para configs de IA materializadas no HOME, com fallback copy-vs-symlink por ferramenta. | notas=Inspirado em jppferguson/dotfiles e basnijholt/dotfiles; ajuda a preservar contratos ao trocar de assistente sem drift entre repo e HOME.
- 2026-03-07 09:08 UTC | decisao=pending | horizonte=next | item=Consolidar ou arquivar o legado historico versionado que nao e fonte canonica, incluindo artefatos hoje ja movidos para `archive/` e outros scripts experimentais ou backups decla... | notas=Reduzir ruido conceitual, diminuir superficie de manutencao e deixar explicita a fronteira entre referencia historica e runtime canonico.
- 2026-03-07 08:10 UTC | decisao=accepted | horizonte=now | item=Expandir datasets e cenarios de eval para bootstrap cross-platform, seguranca e risco operacional. | notas=entregue parcialmente nesta rodada com ai:eval:smoke e ampliacao inicial dos datasets; bootstrap full permanece evolucao futura
- 2026-03-07 08:10 UTC | decisao=accepted | horizonte=now | item=Adicionar validadores dedicados de sincronismo entre workflows, tasks, docs, catalogos e ativos declarativos da IA. | notas=entregue nesta rodada com validate_workflow_task_sync.py e catalogos TASKS/WORKFLOWS
- 2026-03-07 08:10 UTC | decisao=accepted | horizonte=now | item=Importar chat-intake, route e delegate com backend real de roteamento declarativo para a camada canonica .agents. | notas=entregue nesta rodada com backend Python, orchestrator e smoke eval
- 2026-03-07 04:13 UTC | decisao=pending | horizonte=later | item=Expandir datasets e cenarios de eval para bootstrap cross-platform, seguranca e risco operacional. | notas=gaps remanescentes de evals e regression suite
- 2026-03-07 04:13 UTC | decisao=pending | horizonte=next | item=Adicionar validadores dedicados de sincronismo entre workflows, tasks, docs, catalogos e ativos declarativos da IA. | notas=gaps remanescentes inspirados em iageny; workflow-task-doc sync
- 2026-03-07 04:13 UTC | decisao=pending | horizonte=next | item=Importar chat-intake, route e delegate com backend real de roteamento declarativo para a camada canonica .agents. | notas=gaps remanescentes da auditoria cross-repo; arquitetura/roteamento
- (sem itens)
<!-- roadmap:autolog:end -->
