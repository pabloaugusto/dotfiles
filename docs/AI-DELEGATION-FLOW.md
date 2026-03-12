# AI Delegation Flow

## Pipeline canonico

1. Ler [`../AGENTS.md`](../AGENTS.md), [`../LICOES-APRENDIDAS.md`](../LICOES-APRENDIDAS.md) e contexto minimo do repo.
2. Se a sessao veio sem continuidade confiavel, executar o startup oficial e
   usar [`AI-STARTUP-AND-RESTART.md`](AI-STARTUP-AND-RESTART.md), o relatorio
   gerado por `task ai:startup:session` e o artefato `.cache/ai/startup-ready.json`
   como base obrigatoria da rodada.
3. Enquanto a sessao nao atingir `ready_for_work`, o papel ativo no chat deve
   ser `ai-startup-governor`.
4. Rodar preflight de pendencias em [`AI-WIP-TRACKER.md`](AI-WIP-TRACKER.md).
5. Se houver importacao cross-repo, concluir auditoria estrutural e registrar o delta em [`AI-SOURCE-AUDIT.md`](AI-SOURCE-AUDIT.md).
6. Acionar `repo-governance-authority`.
7. Acionar `execution-worklog-governance-owner`.
8. Acionar `ai-scrum-master` como gate global de board, WIP, ownership, cerimonias e aderencia do fluxo.
9. Acionar `architecture-modernization-authority` em paralelo, sempre lendo e monitorando [`AI-WIP-TRACKER.md`](AI-WIP-TRACKER.md), [`../ROADMAP.md`](../ROADMAP.md), [`ROADMAP-DECISIONS.md`](ROADMAP-DECISIONS.md) e demais registradores vivos de backlog/pendencias.
10. Se a tarefa pedir triagem, decomposicao ou plano de delegacao, acionar `orchestrator` com `$task-routing-and-decomposition`.
11. Antes de qualquer subagente, preparar o pacote minimo de contexto: issue dona, branch atual, startup report, readiness artifact, classificacao do `PEA` quando aplicavel, assuncoes e ambiguidades relevantes, regras aplicaveis ao papel, arquivos normativos relevantes e proximo passo objetivo.
12. Se o escopo tocar bootstrap, auth, secrets, CI, sync, CLI ou ambiente, acionar `critical-integrations-guardian`.
13. Se o escopo tocar rotacao, backup, expiracao, revogacao ou inventario de credenciais, chaves SSH, `sops+age` ou notificacao de segredos, acionar `secrets-rotation-governor`.
14. Se houver texto, comentario, documentacao, config textual ou identificadores legiveis alterados, acionar `pascoalete` em modo consultivo com `task spell:review`, lembrando que ele funciona como alias local do `ai-linguistic-reviewer`.
15. Se houver mudanca em Python, PowerShell ou automacao, acionar o revisor especialista aplicavel antes do fechamento tecnico.
16. Se o escopo tocar [`../LICOES-APRENDIDAS.md`](../LICOES-APRENDIDAS.md), fechamento de rodada ou retroativo, acionar `lessons-governance-curator`.
17. Implementar e validar.
18. Registrar pareceres especializados em [`AI-REVIEW-LEDGER.md`](AI-REVIEW-LEDGER.md) quando houver mudanca de codigo ou automacao e parecer ortografico em [`AI-ORTHOGRAPHY-LEDGER.md`](AI-ORTHOGRAPHY-LEDGER.md) quando houver review consultivo textual.
19. Revisar licoes, fechar worklog e validar gates finais.

## Roteamento por escopo

- [`../bootstrap/`](../bootstrap/) e [`../df/`](../df/) -> `bootstrap-operator`
- [`../AGENTS.md`](../AGENTS.md), [`../.agents/`](../.agents/), [`../.codex/README.md`](../.codex/README.md) e [`./`](./) -> `repo-governance-authority`
- [`AI-WIP-TRACKER.md`](AI-WIP-TRACKER.md), [`../ROADMAP.md`](../ROADMAP.md), [`ROADMAP-DECISIONS.md`](ROADMAP-DECISIONS.md) e [`../scripts/ai-worklog.py`](../scripts/ai-worklog.py) -> `execution-worklog-governance-owner`
- startup do zero, restart, `startup clearance` e first-response gate -> `ai-startup-governor`
- board, **WIP**, ownership, **cerimonias** e enforcement do processo agil -> `ai-scrum-master`
- triagem, intake, decomposicao, delegacao -> `orchestrator`
- qualquer analise substantiva -> `architecture-modernization-authority`
- auth, secrets, `gh`, `op`, `sops`, `age`, `ssh-agent`, CI, sync, signing -> `critical-integrations-guardian`
- rotacao, revogacao, expiracao, backup, inventario e notificacao de secrets -> `secrets-rotation-governor`
- docs, comentarios, configs textuais, dicionario `cspell` e revisao ortografica consultiva -> `pascoalete`
- escrita e consolidacao documental -> `ai-documentation-writer`
- revisao semantica e completude documental -> `ai-documentation-reviewer`
- source of truth, placement, lifecycle e elegibilidade de sync -> `ai-documentation-manager`
- publication, backlinks, `documentation-link` e rastreabilidade cross-surface -> `ai-documentation-sync`
- Python -> `python-reviewer`
- PowerShell -> `powershell-reviewer`
- shell, workflows, Taskfile, Docker e CI/CD -> `automation-reviewer`
- [`../LICOES-APRENDIDAS.md`](../LICOES-APRENDIDAS.md), [`../scripts/ai-lessons.py`](../scripts/ai-lessons.py), retroativos -> `lessons-governance-curator`

## Gatilhos obrigatorios

- `architecture-modernization-authority` e sempre obrigatorio como gate paralelo.
- `ai-startup-governor` e obrigatorio em toda nova sessao ou restart ate a sessao atingir `ready_for_work`.
- `ai-scrum-master` e sempre obrigatorio como gate global de **board**, **WIP**, ownership, comunicacao e **cerimonias**.
- `architecture-modernization-authority` deve observar continuamente WIP, backlog, roadmap, decisions e outros artefatos vivos para nao sugerir trabalho fora de contexto.
- nenhuma delegacao para subagente e valida sem startup carregado ou
  explicitamente linkado na rodada atual.
- nenhum agente operacional deve assumir o chat antes de `ready_for_work`; ate
  la o ownership visivel da sessao pertence ao `ai-startup-governor`.
- todo subagente deve receber contexto suficiente para operar de imediato no seu
  papel, sem depender de adivinhacao, memoria parcial ou releitura informal do
  chat.
- quando houver `PEA`, o subagente deve receber tambem o modo de execucao, as
  assuncoes relevantes e as ambiguidades ainda abertas para aquele subescopo.
- `critical-integrations-guardian` e obrigatorio em mudancas de plataforma e integracoes criticas.
- `secrets-rotation-governor` e obrigatorio em mudancas de lifecycle de credenciais.
- `pascoalete` e obrigatorio em modo consultivo para alteracoes textuais e deve abrir pendencia no backlog se reprovar algo que permanecer sem correcao.
- `ai-documentation-manager` deve entrar quando a decisao envolver source of truth, placement, lifecycle, deduplicacao ou elegibilidade de sync documental.
- `ai-documentation-sync` deve entrar quando houver publicacao cross-surface, backlinks ou `documentation-link`.
- revisores especialistas sao obrigatorios quando a mudanca tocar a familia de arquivo correspondente.
- parecer especializado precisa ser registrado em [`AI-REVIEW-LEDGER.md`](AI-REVIEW-LEDGER.md) antes do `done`.
- `orchestrator` governa `ai:chat:intake`, `ai:route` e `ai:delegate` quando a demanda exigir triagem ou decomposicao.
- nenhum worklog pode fechar sem revisao de `lessons-governance-curator`.

## Artefatos declarativos

- [`.agents/config.toml`](.agents/config.toml)
- [`.agents/registry/`](.agents/registry/) (`*.toml`)
- [`.agents/orchestration/`](.agents/orchestration/)
- [`.agents/rules/`](.agents/rules/)
- [`.agents/evals/`](.agents/evals/)
- [`AI-REVIEW-LEDGER.md`](AI-REVIEW-LEDGER.md)
- [`AI-ORTHOGRAPHY-LEDGER.md`](AI-ORTHOGRAPHY-LEDGER.md)
- [`AI-AGENTS-CATALOG.md`](AI-AGENTS-CATALOG.md)
- [`AI-SKILLS-CATALOG.md`](AI-SKILLS-CATALOG.md)
- [`AI-GOVERNANCE-AND-REGRESSION.md`](AI-GOVERNANCE-AND-REGRESSION.md)
