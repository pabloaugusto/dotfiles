# AI Governance And Regression

## Principios

- governanca declarativa, nao so narrativa
- rastreabilidade entre worklog, roadmap e licoes
- gates pequenos, objetivos e automatizados
- zero importacao cross-repo por amostragem

## Gate minimo desta camada

```powershell
task ai:validate
task ai:review:check WORKLOG_ID="WIP-..."
task spell:review WORKLOG_ID="WIP-..." PATHS="README.md,AGENTS.md"
task ai:lessons:check
task ai:worklog:close:gate
task ai:eval:smoke
task ci:workflow:sync:check
task test:unit:python:windows
```

## Regresses que devem falhar

- worklog concluido sem revisao em [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md)
- ausencia de catalogos, orchestration, rules ou evals declarativos
- drift entre [`.agents/`](.agents/), [`docs/`](docs/) e a ponte legada em [`.codex/README.md`](.codex/README.md)
- falta dos gates obrigatorios de arquitetura e integracoes criticas
- datasets de roteamento ou governanca sem cobertura executavel
- drift entre workflows, Taskfile e catalogos [`docs/TASKS.md`](docs/TASKS.md) e [`docs/WORKFLOWS.md`](docs/WORKFLOWS.md)

## Regras perenes

- `architecture-modernization-authority` revisa toda analise substantiva.
- `critical-integrations-guardian` protege toda mudanca sensivel a bootstrap, auth, secrets, CI, sync ou CLI critica.
- `secrets-rotation-governor` protege toda mudanca de lifecycle de credenciais e exige ordem segura de substituicao.
- `pascoalete` revisa ortografia tecnica e higiene do dicionario `cspell` em modo consultivo; quando reprova e a rodada nao corrige, a falha deve gerar pendencia rastreavel no backlog vigente.
- `python-reviewer`, `powershell-reviewer` e `automation-reviewer` revisam toda mudanca de codigo ou automacao da sua familia e podem reprovar o fechamento tecnico.
- parecer especializado aprovado ou reprovado precisa ficar rastreado em [`docs/AI-REVIEW-LEDGER.md`](AI-REVIEW-LEDGER.md).
- parecer ortografico consultivo precisa ficar rastreado em [`docs/AI-ORTHOGRAPHY-LEDGER.md`](AI-ORTHOGRAPHY-LEDGER.md).
- `lessons-governance-curator` revisa toda rodada antes do `done`.
- `orchestrator` governa intake, route e delegate quando a tarefa exigir triagem ou decomposicao.
- CI nao pode validar apenas presenca de arquivos; precisa validar tambem coerencia minima, smoke eval, sincronismo workflow-task-doc e revisao de licoes.
