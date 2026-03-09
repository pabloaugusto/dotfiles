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
- Problema novo encontrado em **cerimonia** deve abrir ou apontar para issue no
  `Jira`.
- Issues abertas a partir de **cerimonia** devem carregar as labels
  `cerimonia` e o nome da **cerimonia**.
- A sincronizacao com `Confluence` deve respeitar o contrato definido na propria
  definicao da **cerimonia**.
