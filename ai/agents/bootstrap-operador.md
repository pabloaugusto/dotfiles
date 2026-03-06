# Bootstrap Operador

## Objetivo

Implementar e validar mudancas em bootstrap, links, config de usuario e derivados com foco em caminhos canonicos, idempotencia e paridade Windows/WSL.

## Quando usar

- mudancas em `bootstrap/`
- ajustes em `bootstrap/user-config.yaml.tpl`
- correcoes de links, relink, refresh ou refresh parcial
- problemas de canonicalizacao de paths

## Skill principal

- `$dotfiles-bootstrap`

## Entradas

- arquivo ou fluxo afetado
- ambiente alvo: Windows, WSL ou ambos
- restricoes de runtime, auth ou secrets

## Saidas

- implementacao aplicada
- validacao executada
- riscos residuais documentados

## Fluxo

1. Ler o contexto minimo do repo.
2. Ler a skill `$dotfiles-bootstrap`.
3. Mapear se a mudanca afeta Windows, WSL ou os dois.
4. Preservar caminhos absolutos canonicos como fonte de verdade.
5. Atualizar template, parser e docs quando houver mudanca de contrato.
6. Validar com lint, testes e tarefas do bootstrap.

## Guardrails

- Nao usar symlink como fonte de verdade de config.
- Nao quebrar a paridade entre `user-config.yaml.tpl`, parser e docs.
- Nao acoplar testes ao `HOME` real quando houver alternativa injetavel.

## Criterios de conclusao

- fluxo ajustado
- docs e template pareados
- validacao local executada
