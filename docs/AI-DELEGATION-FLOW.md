# AI Delegation Flow

## Pipeline canonico

1. Ler [`../AGENTS.md`](../AGENTS.md), [`../LICOES-APRENDIDAS.md`](../LICOES-APRENDIDAS.md) e contexto minimo do repo.
2. Rodar preflight de pendencias em [`AI-WIP-TRACKER.md`](AI-WIP-TRACKER.md).
3. Se houver importacao cross-repo, concluir auditoria estrutural e registrar o delta em [`AI-SOURCE-AUDIT.md`](AI-SOURCE-AUDIT.md).
4. Acionar `repo-governance-authority`.
5. Acionar `execution-worklog-governance-owner`.
6. Acionar `architecture-modernization-authority` em paralelo, sempre lendo e monitorando [`AI-WIP-TRACKER.md`](AI-WIP-TRACKER.md), [`../ROADMAP.md`](../ROADMAP.md), [`ROADMAP-DECISIONS.md`](ROADMAP-DECISIONS.md) e demais registradores vivos de backlog/pendencias.
7. Se a tarefa pedir triagem, decomposicao ou plano de delegacao, acionar `orchestrator` com `$task-routing-and-decomposition`.
8. Se o escopo tocar bootstrap, auth, secrets, CI, sync, CLI ou ambiente, acionar `critical-integrations-guardian`.
9. Se o escopo tocar rotacao, backup, expiracao, revogacao ou inventario de credenciais, chaves SSH, `sops+age` ou notificacao de segredos, acionar `secrets-rotation-governor`.
10. Se houver texto, comentario, documentacao, config textual ou identificadores legiveis alterados, acionar `pascoalete` em modo consultivo com `task spell:review`.
11. Se houver mudanca em Python, PowerShell ou automacao, acionar o revisor especialista aplicavel antes do fechamento tecnico.
12. Se o escopo tocar [`../LICOES-APRENDIDAS.md`](../LICOES-APRENDIDAS.md), fechamento de rodada ou retroativo, acionar `lessons-governance-curator`.
13. Implementar e validar.
14. Registrar pareceres especializados em [`AI-REVIEW-LEDGER.md`](AI-REVIEW-LEDGER.md) quando houver mudanca de codigo ou automacao e parecer ortografico em [`AI-ORTHOGRAPHY-LEDGER.md`](AI-ORTHOGRAPHY-LEDGER.md) quando houver review consultivo textual.
15. Revisar licoes, fechar worklog e validar gates finais.

## Roteamento por escopo

- [`../bootstrap/`](../bootstrap/) e [`../df/`](../df/) -> `bootstrap-operator`
- [`../AGENTS.md`](../AGENTS.md), [`../.agents/`](../.agents/), [`../.codex/README.md`](../.codex/README.md) e [`./`](./) -> `repo-governance-authority`
- [`AI-WIP-TRACKER.md`](AI-WIP-TRACKER.md), [`../ROADMAP.md`](../ROADMAP.md), [`ROADMAP-DECISIONS.md`](ROADMAP-DECISIONS.md) e [`../scripts/ai-worklog.py`](../scripts/ai-worklog.py) -> `execution-worklog-governance-owner`
- triagem, intake, decomposicao, delegacao -> `orchestrator`
- qualquer analise substantiva -> `architecture-modernization-authority`
- auth, secrets, `gh`, `op`, `sops`, `age`, `ssh-agent`, CI, sync, signing -> `critical-integrations-guardian`
- rotacao, revogacao, expiracao, backup, inventario e notificacao de secrets -> `secrets-rotation-governor`
- docs, comentarios, configs textuais, dicionario `cspell` e revisao ortografica consultiva -> `pascoalete`
- Python -> `python-reviewer`
- PowerShell -> `powershell-reviewer`
- shell, workflows, Taskfile, Docker e CI/CD -> `automation-reviewer`
- [`../LICOES-APRENDIDAS.md`](../LICOES-APRENDIDAS.md), [`../scripts/ai-lessons.py`](../scripts/ai-lessons.py), retroativos -> `lessons-governance-curator`

## Gatilhos obrigatorios

- `architecture-modernization-authority` e sempre obrigatorio como gate paralelo.
- `architecture-modernization-authority` deve observar continuamente WIP, backlog, roadmap, decisions e outros artefatos vivos para nao sugerir trabalho fora de contexto.
- `critical-integrations-guardian` e obrigatorio em mudancas de plataforma e integracoes criticas.
- `secrets-rotation-governor` e obrigatorio em mudancas de lifecycle de credenciais.
- `pascoalete` e obrigatorio em modo consultivo para alteracoes textuais e deve abrir pendencia no backlog se reprovar algo que permanecer sem correcao.
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
