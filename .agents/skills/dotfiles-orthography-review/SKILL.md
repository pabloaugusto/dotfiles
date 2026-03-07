---
name: dotfiles-orthography-review
description: Revisar ortografia tecnica, comentarios e textos do repo com cspell, higienizar o dicionario local e registrar parecer consultivo por arquivo. Use quando houver texto, comentarios, docs ou arquivos de configuracao versionados alterados.
---

# dotfiles-orthography-review

## Objetivo

Atuar como o fluxo consultivo de ortografia do repo via Pascoalete.

## Fluxo

1. Ler [`.cspell.json`](../../../.cspell.json),
   [`.cspell/project-words.txt`](../../../.cspell/project-words.txt) e
   [`docs/AI-ORTHOGRAPHY-LEDGER.md`](../../../docs/AI-ORTHOGRAPHY-LEDGER.md).
2. Rodar `task spell:dictionary:audit` para detectar redundancias no
   dicionario local.
3. Rodar `task spell:review` no escopo dos arquivos alterados.
4. Registrar parecer consultivo por arquivo e backlog quando houver falha
   nao corrigida.
5. Se for necessario incluir nova palavra, confirmar primeiro que ela nao esta
   coberta pelos dicionarios importados.

## Regras

- Sempre usar a stack canonica de `cspell` do repo.
- O parecer ortografico e consultivo e nao bloqueia PR/commit/deploy/release.
- Falha ortografica nao corrigida deve virar pendencia rastreavel.
- O dicionario local so recebe palavras realmente nao cobertas externamente.

## Entregas esperadas

- parecer ortografico por arquivo
- dicionario local higienizado
- pendencias rastreaveis quando houver reprovacao

## Validacao

- `task spell:check`
- `task spell:dictionary:audit`
- `task spell:review`

## Referencias

- [`references/checklist.md`](references/checklist.md)
- [`../../../.cspell.json`](../../../.cspell.json)
- [`../../../.cspell/project-words.txt`](../../../.cspell/project-words.txt)
- [`../../../docs/AI-ORTHOGRAPHY-LEDGER.md`](../../../docs/AI-ORTHOGRAPHY-LEDGER.md)
