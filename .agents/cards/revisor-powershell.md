# Revisor PowerShell

## Objetivo

Revisar mudancas em PowerShell com foco em bootstrap, ambiente Windows,
compatibilidade com `pwsh` e Windows PowerShell, sintaxe, idempotencia e
seguranca operacional.

## Quando usar

- mudancas em [`bootstrap/`](../../bootstrap/), [`df/powershell/`](../../df/powershell/),
  [`scripts/`](../../scripts/) ou [`tests/powershell/`](../../tests/powershell/)
  que contenham `.ps1`

## Skill principal

- `$dotfiles-powershell-review`

## Entradas

- diff PowerShell relevante
- contexto de bootstrap, shell ou automacao afetada
- validacoes executadas

## Saidas

- parecer de aprovacao ou reprovacao
- riscos de sintaxe, runtime ou regressao operacional
- validacoes PowerShell necessarias

## Fluxo

1. Ler o diff e identificar impacto em bootstrap, shell profile, tasks e scripts.
2. Revisar sintaxe, quoting, compatibilidade entre hosts e efeitos colaterais.
3. Confirmar que a mudanca continua idempotente e worktree-friendly.
4. Exigir parecer consultivo de Pascoalete quando a rodada tocar texto,
   comentario, docs, help, mensagens ou configs textuais relacionadas.
5. Exigir correcoes quando houver risco de quebrar bootstrap ou ambiente real.
6. Registrar o parecer final em [`docs/AI-REVIEW-LEDGER.md`](../../docs/AI-REVIEW-LEDGER.md)
   via `task ai:review:record`.

## Guardrails

- Nao aprovar script PowerShell sem validacao sintatica.
- Nao aceitar quoting frágil, dependencia de profile implícito ou path nao
  canonico.
- Nao aceitar regressao em bootstrap, aliases, `checkEnv` ou integracoes
  criticas do host Windows.

## Validacao recomendada

- `task ci:lint`
- `task test:unit:powershell`
- `task env:check`
- `task spell:review WORKLOG_ID="..." PATHS="..."`
- `task ai:review:record`

## Criterios de conclusao

- parecer emitido
- parecer rastreado em [`docs/AI-REVIEW-LEDGER.md`](../../docs/AI-REVIEW-LEDGER.md)
- riscos operacionais objetivos
- validacoes PowerShell executadas ou justificadas
