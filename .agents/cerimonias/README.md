# Cerimonias do Time de IA

Camada canonica das **cerimonias** ageis versionadas do time.

## Estrutura

- [`ceremony.schema.json`](ceremony.schema.json): schema base das definicoes de
  **cerimonia**.
- [`retrospectiva.yaml`](retrospectiva.yaml): definicao ativa da
  **Retrospectiva**.
- [`logs/retrospectiva-template.md`](logs/retrospectiva-template.md): template
  Markdown para execucao de retrospectivas.
- [`logs/retrospectiva/README.md`](logs/retrospectiva/README.md): contrato de
  naming e localizacao dos logs reais.

## Regras operacionais

- Toda **cerimonia** precisa nascer versionada nesta arvore antes de virar
  rotina do time.
- Toda execucao real de **cerimonia** deve gerar log Markdown proprio.
- Toda branch finalizada que exigir **Retrospectiva** precisa gerar log
  Markdown, entrada indice no
  [`docs/AI-SCRUM-MASTER-LEDGER.md`](../../docs/AI-SCRUM-MASTER-LEDGER.md) e
  pagina no `Confluence` quando o contrato da **cerimonia** assim determinar.
- Problema novo encontrado em **cerimonia** deve abrir ou apontar para issue no
  `Jira`.
- Problema nao resolvido na hora durante a **cerimonia** deve abrir ou linkar
  `Bug` ou `Task` no `Jira` antes de o fechamento da branch ser considerado
  aderente.
- Issues abertas a partir de **cerimonia** devem carregar as labels
  `cerimonia` e o nome da **cerimonia**.
- A sincronizacao com `Confluence` deve respeitar o contrato definido na propria
  definicao da **cerimonia**.
