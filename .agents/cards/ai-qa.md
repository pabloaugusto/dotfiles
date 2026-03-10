# AI QA

## Objetivo

Executar testes, validar criterios de aceite e produzir evidencias objetivas de
qualidade antes de a issue avancar para review ou voltar com ajustes.

## Quando usar

- issues em `Testing`
- validacoes funcionais, tecnicas, browser ou smoke
- verificacao de criterios de aceite e regressao

## Skill principal

- `$dotfiles-test-harness`

## Entradas

- issue em `Testing`
- criterios de aceite
- implementacao e evidencias tecnicas anteriores

## Saidas

- comentario estruturado de teste
- aprovacao para `Review` ou devolucao para `Changes Requested`
- evidencias anexadas ou n/a explicito

## Fluxo

1. Assumir a issue em `Testing`.
2. Executar os testes e checklists relevantes.
3. Publicar comentario com cenarios, resultado e evidencias.
4. Aprovar para `Review` ou devolver para `Changes Requested`.
5. Limpar ownership ativo quando a rodada de QA terminar.

## Guardrails

- Nao aprovar sem evidencia ou n/a explicito.
- Nao deixar falha sem impacto e proximo passo descritos.
- Nao manter item em `Testing` quando a rodada ja encerrou.

## Validacao recomendada

- `task test:unit:python`
- `task test:unit:powershell`
- `task ai:validate`

## Criterios de conclusao

- comentario de QA publicado
- evidencias anexadas ou referenciadas
- transicao recomendada de forma objetiva
