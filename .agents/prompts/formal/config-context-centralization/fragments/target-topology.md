# Topologia Alvo Por Contexto

## Raizes canonicas

- [config/](../../../../../config/) para dev, integracoes de dev e defaults globais
- a futura pasta `config` sob [app/](../../../../../app/) para runtime do
  produto dotfiles
- a futura pasta `config` sob [`.agents/`](../../../../) para configuracao
  declarativa da IA
- [pyproject.toml](../../../../../pyproject.toml) para toolchain Python

## Estrutura inicial recomendada

```text
config/
  config.toml
  dev.toml
  integrations.toml
  quality.toml
  time-surfaces.yaml

app/config/
  config.toml
  runtime.toml
  bootstrap.toml
  links.toml

.agents/config/
  config.toml
  agents.toml
  communication.toml
  startup.toml
  orchestration.toml
  reviews.toml
  prompts.toml
```

## Fronteira da toolchain Python

[pyproject.toml](../../../../../pyproject.toml) permanece apenas com:

- dependencias Python
- lint
- type checking
- testes
- configuracao da toolchain Python

Ele nao deve receber configuracao de runtime, IA ou regionalizacao global.
