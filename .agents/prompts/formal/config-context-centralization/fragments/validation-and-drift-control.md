# Validacao E Controle De Drift

## Hardeners obrigatorios

- biblioteca unica de config resolution
- schemas por contexto
- tabelas documentais geradas automaticamente
- lint de `literal proibido fora da config`
- validadores anti-drift

## Regra do resolvedor unico

Nenhum script pode criar loader paralelo quando existir a biblioteca oficial de
config resolution.

## Regra dos schemas

As configs TOML internas devem validar:

- tipos
- enums
- ownership por contexto
- referencias `arquivo::chave`
- overlays permitidos

## Regra das tabelas geradas

Docs que espelham configuracao devem ser derivados da config canonica e entrar
sob enforcement de `docs:check` e `ai:validate`.

## Regra do lint

Valores classificados como `config-managed` nao podem reaparecer como literal
fora da config canonica, salvo excecao curta e explicitamente allowlisted.
