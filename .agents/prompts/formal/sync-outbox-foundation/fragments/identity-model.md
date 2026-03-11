# Fragmento - Modelo De Identidade

<!-- cspell:words implementacao estavel aplicavel -->

Toda implementacao derivada deste pack deve separar:

- `workspace_id` como identidade logica do workspace
- `runtime_environment_id` como identidade concreta da execucao

## Regras

- `workspace_id` e estavel, curto, ASCII e `kebab-case`
- `workspace_id` nao depende do path local do clone
- `runtime_environment_id` deve distinguir host, sistema, tipo de runtime e
  distro quando aplicavel
- hostname sozinho nao e identidade suficiente
