---
name: dotfiles-powershell-review
description: Revisar mudancas PowerShell do repo com foco em bootstrap, sintaxe, quoting, compatibilidade entre pwsh e Windows PowerShell, idempotencia e seguranca operacional.
---

# dotfiles-powershell-review

## Objetivo

Atuar como revisor tecnico de codigo PowerShell do repo.

## Fluxo

1. Ler o diff `.ps1` e mapear impacto em bootstrap, aliases, tasks e ambiente Windows.
2. Revisar sintaxe, quoting, contratos de path e possiveis regresses de host.
3. Conferir se a rodada acionou Pascoalete para textos, comentarios, docs,
   mensagens e configs textuais alteradas.
4. Confirmar idempotencia e compatibilidade operacional.
5. Exigir validacoes PowerShell proporcionais ao risco.

## Regras

- Nao aprovar PowerShell sem validacao sintatica.
- Nao aceitar quoting fragil, side effect oculto ou dependencia de profile implicito.
- Nao degradar bootstrap, `checkEnv`, signer Git ou shell do usuario.
- Sempre incluir `cspell` via `task spell:review` quando a mudanca alterar
  textos, comentarios, help ou mensagens legiveis.

## Entregas esperadas

- parecer de revisao PowerShell
- riscos operacionais objetivos
- lista de validacoes obrigatorias

## Validacao

- `task ci:lint`
- `task test:unit:powershell`
- `task env:check`
- `task spell:review`

## Referencias

- [`references/checklist.md`](references/checklist.md)
- [`../../../bootstrap/`](../../../bootstrap/)
- [`../../../df/powershell/`](../../../df/powershell/)
- [`../../../docs/AI-ORTHOGRAPHY-LEDGER.md`](../../../docs/AI-ORTHOGRAPHY-LEDGER.md)
