# Reviewer Jira workflow policy

Politica canonica de operacao do reviewer dentro do fluxo `Jira + Confluence`.
Este artefato transforma o review em decisao operacional, nao apenas em
comentario.

## Principio central

Reviewer especializado nao fecha sua atuacao com um "LGTM" generico. Ele precisa:

- publicar comentario estruturado no Jira
- anexar ou citar evidencias reais
- classificar findings por severidade
- tomar decisao formal
- mover a issue para o status correto

## Mapeamento padrao de decisao para workflow

| Decisao | Status alvo |
| --- | --- |
| `approved` | `Done` |
| `approved_with_debt` | `Done` |
| `changes_required` | `Changes Requested` |
| `blocked` | `Paused` |

## Acoes obrigatorias por decisao

### Approved

- publicar comentario com resumo do review
- listar verificacoes principais
- registrar debt nao bloqueante, se existir
- transicionar a issue

### Approved with debt

- publicar comentario com aprovacao e debt registrado
- criar ou solicitar backlog tecnico quando a politica exigir
- transicionar a issue

### Changes required

- publicar comentario com falhas, severidade, impacto e melhor correcao
- separar blockers de melhorias menores
- transicionar para `Changes Requested`

### Blocked

- publicar comentario com risco e acao obrigatoria para desbloqueio
- transicionar para `Paused`
- escalar quando houver dependencia humana, de tenant ou de ferramenta externa

## Conteudo minimo do comentario

- quem revisou
- escopo do review
- decisao
- confianca do parecer
- findings principais
- evidencias ou anexos usados
- proximo passo ou condicao de desbloqueio

## Evidencias validas

- saida de lint, testes, typecheck e benchmark
- screenshot quando houver validacao visual
- anexo gerado na propria demanda
- link GitHub canonico para arquivo versionado
- link Jira ou Confluence do mesmo tenant

## Evidencias invalidas

- caminho local `C:/...`
- URL crua de API interna que nao abre para o usuario
- comentario sem prova do trabalho feito

## Relacionados

- [`reviewer-decision-model.md`](reviewer-decision-model.md)
- [`reviewer-severity-policy.md`](reviewer-severity-policy.md)
- [`jira-writing-standards.md`](jira-writing-standards.md)
