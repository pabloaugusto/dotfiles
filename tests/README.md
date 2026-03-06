# Tests

Estrutura inicial:

- `tests/powershell`: testes Pester para logica PowerShell
- `tests/bash`: reservado para testes Bats do bootstrap Linux

Regra:

- primeiro testar funcao pura
- depois testar harness de integracao
- E2E sensivel fica fora do PR CI
