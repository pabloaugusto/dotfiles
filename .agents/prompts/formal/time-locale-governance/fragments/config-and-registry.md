# Config E Registry

Este pack trabalha com duas camadas complementares:

- um arquivo TOML global como fonte canonica de configuracoes do projeto
- um registry YAML temporal por superficie

```text
Arquivos alvo planejados:
- config/config.toml
- config/time-surfaces.yaml
```

## Regra de separacao

- o arquivo TOML global guarda defaults globais, formatos e policy base
- o registry YAML temporal guarda classificacao, ownership, justificativas e
  comportamento por superficie temporal

## Classes obrigatorias de superficie

- `default_regionalized`
- `explicit_utc`
- `stable_machine_token`

## Matriz de precedencia

1. contrato explicito da superficie
2. policy temporal canonica do projeto
3. runtime efetivo permitido pela policy
4. override explicito e rastreavel da execucao atual
5. fallback seguro com drift explicito, nunca `UTC` implicito
