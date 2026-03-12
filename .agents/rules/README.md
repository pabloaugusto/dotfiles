# Rules

Fonte canonica humana das regras normativas por tema em [`.agents/rules/`](./).

## Objetivo

- centralizar a governanca humana por dominio em um unico lugar
- reduzir drift entre [`AGENTS.md`](../../AGENTS.md), [`docs/`](../../docs/),
  [`config/ai/`](../../config/ai/) e enforcement executavel
- permitir que startup, delegacao, review e docs apontem para regras tematicas
  curtas e navegaveis

## Como ler

- comece por [`CATALOG.md`](CATALOG.md)
- use [`core-rules.md`](core-rules.md) para contratos transversais
- depois leia apenas o tema aplicavel ao trabalho atual

## Precedencia

1. politicas da plataforma e do sistema
2. instrucoes explicitas do operador humano na sessao atual
3. [`AGENTS.md`](../../AGENTS.md)
4. esta pasta como fonte canonica humana por tema
5. [`LICOES-APRENDIDAS.md`](../../LICOES-APRENDIDAS.md)

## Fronteira

- esta pasta define regra humana normativa
- [`config/ai/`](../../config/ai/) define contratos declarativos consumiveis
- [`Taskfile.yml`](../../Taskfile.yml), [`scripts/`](../../scripts/),
  [`tests/`](../../tests/) e [`.githooks/`](../../.githooks/) fazem o
  enforcement executavel
- [`docs/`](../../docs/) guarda guias, runbooks e explicacoes derivadas
