# Retrospectiva - 2026-03-10 17:56 UTC - feat/DOT-119-kanban-right-to-left

## Metadados

| Campo | Valor |
| --- | --- |
| Cerimonia | Retrospectiva |
| Data/Hora UTC | 2026-03-10 17:56 UTC |
| Repo | dotfiles |
| Branch | feat/DOT-119-kanban-right-to-left |
| Work items | DOT-119, DOT-135 |
| Facilitador | Scrum Master |
| Participantes | Scrum Master, Testador (QA), Revisor, Escrivao, ai-reviewer-config-policy, ai-reviewer-python, Pascoalete |
| Contexto | Backfill fiel da **Retrospectiva** da fatia de incremento testavel que tornou perene a leitura do board da direita para a esquerda, com foco em terminar antes de comecar e cobertura automatica no validador do repo. |
| Confluence | [Retrospectiva - 2026-03-10 17:56](https://pabloaugusto.atlassian.net/spaces/DOT/pages/256901121/Retrospectiva+-+2026-03-10+17+56) |

## Finalidade

Analisar os problemas enfrentados no ciclo da branch e deixar o plano de acao
rastreavel para o que ainda nao foi concluido.

## Pauta inicial

1. Revisar objetivo da branch e resultado entregue.
2. Catalogar problemas que atrapalharam o fluxo.
3. Classificar o que foi resolvido, o que segue pendente e o que exige nova
   issue.
4. Definir plano de acao, responsavel e proximo passo.

## Problemas catalogados

| ID | Problema | Impacto | Status atual | Jira | Plano de acao |
| --- | --- | --- | --- | --- | --- |
| P1 | A operacao do board ainda nao explicitava de forma perene a leitura da direita para a esquerda e a regra de terminar antes de comecar. | Agentes ociosos podiam puxar trabalho novo sem priorizar o item mais proximo de `Done`, desperdicando capacidade do fluxo. | Resolvido nesta branch. | [DOT-119](https://pabloaugusto.atlassian.net/browse/DOT-119) | Manter contracts, cards, `jira-model` e operating model sincronizados sempre que a politica do board evoluir. |
| P2 | A regra ainda nao tinha cobertura automatica suficiente na validacao declarativa do repo. | O contrato podia voltar a drifar entre documento e execucao real sem falha objetiva de governanca. | Resolvido nesta branch. | [DOT-119](https://pabloaugusto.atlassian.net/browse/DOT-119) | Preservar a cobertura em `validate-ai-assets` e repetir a verificacao em toda mudanca de board policy. |

## Artefatos gerados

- log Markdown desta **cerimonia**: [`.agents/cerimonias/logs/retrospectiva/2026-03-10-1756-feat-DOT-119-kanban-right-to-left.md`](./2026-03-10-1756-feat-DOT-119-kanban-right-to-left.md)
- entrada correspondente no [`docs/AI-SCRUM-MASTER-LEDGER.md`](../../../../docs/AI-SCRUM-MASTER-LEDGER.md)
- issue(s) do `Jira` abertas ou vinculadas: [DOT-119](https://pabloaugusto.atlassian.net/browse/DOT-119), [DOT-135](https://pabloaugusto.atlassian.net/browse/DOT-135), [DOT-127](https://pabloaugusto.atlassian.net/browse/DOT-127)
- pagina no `Confluence` conforme contrato da **cerimonia**: [Retrospectiva - 2026-03-10 17:56](https://pabloaugusto.atlassian.net/spaces/DOT/pages/256901121/Retrospectiva+-+2026-03-10+17+56)

## Encaminhamento

- Plano de acao: seguir tratando a politica do board como contrato perene e auditar toda excecao pelo criterio do menor desbloqueador possivel.
- Proximo passo: manter a continuidade da trilha do board em [DOT-127](https://pabloaugusto.atlassian.net/browse/DOT-127) e usar esta baseline para puxar o proximo work item minimo que destrave o fluxo.
- Responsavel: Scrum Master
