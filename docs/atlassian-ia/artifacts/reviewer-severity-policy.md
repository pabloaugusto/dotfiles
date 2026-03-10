# Reviewer severity policy

Politica canonica de severidade usada pelos reviewers especializados da control
plane. Este artefato detalha a taxonomia declarada em
[`../../../config/ai/reviewer-policies.yaml`](../../../config/ai/reviewer-policies.yaml)
e serve como base para comentarios, transicoes no Jira, evals e auditoria.

## Objetivo

- impedir reviews vagos ou apenas opinativos
- separar claramente o que bloqueia de verdade do que pode virar debt
- padronizar a linguagem dos pareceres no Jira, Confluence e GitHub

## Niveis de severidade

### Blocker

Impede aprovacao e continuidade.

Exemplos:

- bug funcional provavel em fluxo critico
- falha de seguranca
- regressao seria de performance
- aumento critico de I/O
- perda ou corrupcao de dados
- race condition relevante
- violacao arquitetural importante
- ausencia de teste em caminho de alto risco

Regra de workflow:

- nao pode haver transicao de aprovacao enquanto existir `blocker`
- o comentario precisa explicar risco, impacto e melhor correcao

### Major

Normalmente exige correcao antes de avancar.

Exemplos:

- piora relevante de eficiencia
- design fragil
- logging inadequado
- tipagem ruim em area central
- aumento de complexidade sem justificativa
- observabilidade insuficiente em fluxo critico

Regra de workflow:

- costuma levar a `Changes Requested`
- so pode ser rebaixado se houver justificativa tecnica explicita

### Minor

Melhoria recomendada, sem bloquear sozinha.

Exemplos:

- legibilidade
- pequena simplificacao
- duplicacao leve
- nomenclatura refinavel
- docstring ou typing ajustavel

### Backlog debt

Nao bloqueia agora, mas precisa virar backlog tecnico rastreavel.

Exemplos:

- refactor estrutural desejavel, mas fora do recorte atual
- padronizacao adicional
- melhoria de observabilidade ou modularidade nao critica

Regra de workflow:

- deve ser registrada na issue, no backlog ou em subtask correspondente
- nao pode desaparecer no comentario como nota solta

### Nit

Ajuste cosmetico ou de microclareza. Nao bloqueia.

## Regras de classificacao

- preferencia subjetiva nunca vira `blocker`
- todo `blocker` e `major` precisa trazer evidencia e impacto
- todo finding deve sugerir a melhor correcao, nao apenas apontar o problema
- se existir duvida real, o reviewer deve registrar a incerteza em vez de
  inflar a severidade

## Resultado operacional esperado

Ao terminar um review, o agente precisa deixar claro:

- quais findings sao bloqueantes
- quais sao debt nao bloqueante
- qual decisao formal foi tomada
- para qual status a issue deve seguir

## Relacionados

- [`reviewer-decision-model.md`](reviewer-decision-model.md)
- [`reviewer-standards-catalog.md`](reviewer-standards-catalog.md)
- [`python-quality-review-agent.md`](python-quality-review-agent.md)
