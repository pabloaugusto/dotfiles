# Escalacao de Bloqueios e Notificacoes Multicanal

- Status: `contract-approved`
- Data-base: `2026-03-08`
- Relacionados:
  - [`2026-03-07-operacao-agentes-jira-confluence.md`](2026-03-07-operacao-agentes-jira-confluence.md)
  - [`2026-03-07-parecer-e-plano-inicial.md`](2026-03-07-parecer-e-plano-inicial.md)
  - [`artifacts/agent-operations.md`](artifacts/agent-operations.md)
  - [`../../config/ai/contracts.yaml`](../../config/ai/contracts.yaml)
  - [`../../config/ai/agent-operations.yaml`](../../config/ai/agent-operations.yaml)

## Objetivo

Garantir que todo bloqueio real, quando nenhum agente de IA conseguir
transpor de forma autonoma, seja comunicado ao usuario por todos os meios de
notificacao disponiveis no sistema naquele momento.

## Regra canonica

Se uma demanda ficar bloqueada e nenhum agente conseguir destrava-la, o sistema
deve:

1. tirar a issue de `Doing` e refletir o estado real em `Paused` ou no status
   equivalente do fluxo
2. registrar comentario estruturado no `Jira`
3. registrar a atualizacao correspondente no `Confluence` quando houver pagina
   oficial relacionada
4. acionar todos os canais de comunicacao disponiveis no momento
5. registrar quais canais foram tentados, quando e com qual resultado

## Canais minimos previstos

- comentario e mencao no `Jira`
- comentario, mencao ou atualizacao de pagina no `Confluence`
- email
- Slack
- WhatsApp
- SMS
- notificacao push

Se algum canal ainda nao existir no sistema, isso precisa ficar explicito no
registro do bloqueio.

## Conteudo minimo da notificacao

Toda notificacao de bloqueio precisa informar:

- qual demanda foi bloqueada
- qual agente detectou o bloqueio
- por que o bloqueio aconteceu
- o que ja foi tentado pela automacao
- qual acao do usuario e necessaria para destravar
- onde estao as evidencias e os artefatos relacionados

## Ownership recomendado

- `ai-engineering-manager`: owner da escalacao operacional
- `ai-documentation-agent`: owner do reflexo documental
- `ai-product-owner`: owner de replanejamento e priorizacao quando o bloqueio
  muda o backlog

## Implementacao faseada

### Fase 1

- endurecer o contrato em `Jira` e `Confluence`
- exigir log formal do bloqueio e das tentativas de notificacao
- registrar explicitamente quando so existem `Jira` e `Confluence`

### Fase 2

- adicionar adapters reais para email, Slack, WhatsApp, SMS e push
- criar configuracao declarativa de canais disponiveis por ambiente
- registrar telemetria de entrega e acknowledgement

### Fase 3

- adicionar politica de repeticao e escalonamento por severidade
- medir tempo ate reconhecimento do usuario
- integrar isso aos relatorios de saude da operacao

## Criterios de aceite

- nenhum bloqueio permanente fica apenas no chat ou apenas na memoria local
- toda issue bloqueada registra o motivo e a acao esperada do usuario
- o sistema tenta todos os canais disponiveis e documenta o resultado
- `Doing` deixa de representar trabalho parado
- backlog e documentacao continuam coerentes com o bloqueio ativo
