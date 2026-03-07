# Curador Licoes Aprendidas

## Objetivo

Manter [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md) como contrato vivo, auditavel e sincronizado com o tracker de worklog, o roadmap e os gates de governanca.

## Quando usar

- mudancas em [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md)
- retroativas de trabalho executado
- fechamento de worklog
- revisao de governanca de continuidade, roadmap ou backlog

## Skill principal

- `$dotfiles-lessons-governance`

## Entradas

- worklog atual ou concluido
- resultado da rodada
- licoes novas ou justificativa de ausencia de licao

## Saidas

- revisao de licoes registrada
- novas licoes catalogadas quando cabivel
- fechamento sem pendencia silenciosa entre worklog e lessons

## Fluxo

1. Ler [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md), [`docs/AI-WIP-TRACKER.md`](docs/AI-WIP-TRACKER.md) e [`docs/ROADMAP.md`](docs/ROADMAP.md).
2. Avaliar se a rodada produziu nova licao, regra, incidente ou workaround validado.
3. Se houver nova licao, registrar no catalogo com evidencias e worklog relacionado.
4. Registrar revisao explicita da rodada como `capturada` ou `sem_nova_licao`.
5. Garantir que nenhum worklog concluido fique sem revisao.

## Guardrails

- Nao fechar rodada sem revisar lessons.
- Nao registrar licao vaga, opinativa ou sem validacao.
- Nao duplicar licao equivalente quando consolidacao resolver.
- Nao deixar worklog e lessons divergirem.

## Validacao recomendada

- `task ai:lessons:check`
- `task ai:worklog:close:gate`
- `task ai:validate`

## Criterios de conclusao

- revisao da rodada registrada
- novas licoes consolidadas quando necessario
- `task ai:lessons:check` aprovado
