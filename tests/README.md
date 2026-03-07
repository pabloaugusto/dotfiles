# Tests

Estrutura inicial:

- `tests/powershell`: testes Pester para logica PowerShell
- `tests/python`: testes unitarios da governanca Git e do tracker de WIP de IA
- `tests/bash`: reservado para testes Bats do bootstrap Linux

Regra:

- primeiro testar funcao pura
- depois testar harness de integracao
- E2E sensivel fica fora do PR CI
