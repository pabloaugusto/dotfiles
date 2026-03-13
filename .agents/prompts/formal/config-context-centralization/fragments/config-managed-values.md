# Valores Gerenciados Pela Config

## O que deve sair de docs, contracts e rules para config

- defaults globais
- mappings
- aliases
- display names
- formatos visiveis
- surfaces configuraveis
- enums internos configuraveis
- caminhos declarativos
- policies de heranca
- toggles e allowlists configuraveis

## O que permanece normativo

- obrigacoes `must`
- proibicoes
- gates de processo
- ownership normativo
- rationale
- contexto humano

## Regra pratica

Quando um texto humano citar um valor configuravel, ele deve:

1. apontar para a config canonica
2. usar a convencao `arquivo::chave`
3. deixar claro que nao e source of truth do literal
