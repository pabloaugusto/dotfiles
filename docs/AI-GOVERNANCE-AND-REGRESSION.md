# AI Governance And Regression

## Principios

- governanca declarativa, nao so narrativa
- rastreabilidade entre worklog, roadmap e licoes
- gates pequenos, objetivos e automatizados
- zero importacao cross-repo por amostragem

## Gate minimo desta camada

```powershell
task ai:validate
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
- `lessons-governance-curator` revisa toda rodada antes do `done`.
- `orchestrator` governa intake, route e delegate quando a tarefa exigir triagem ou decomposicao.
- CI nao pode validar apenas presenca de arquivos; precisa validar tambem coerencia minima, smoke eval, sincronismo workflow-task-doc e revisao de licoes.
