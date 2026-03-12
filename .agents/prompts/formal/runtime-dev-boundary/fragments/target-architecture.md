# Arquitetura Alvo

```text
app/
  bootstrap/
  df/
config/
  ...
pyproject.toml
```

## Regras de ownership

- `app/bootstrap/` -> runtime e provisionamento da app/workstation
- `app/df/` -> dotfiles e assets runtime
- [`config/`](../../../../../config/) -> desenvolvimento, suporte, control plane
  e governanca
- [`pyproject.toml`](../../../../../pyproject.toml) -> toolchain Python,
  dependencias, lint, testes e configuracao de desenvolvimento nao-runtime
