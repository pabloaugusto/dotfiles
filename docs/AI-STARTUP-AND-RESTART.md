# AI Startup And Restart

## Objetivo

Definir o procedimento vivo de **startup** e **restart** que toda sessao de IA
deve executar ao abrir este repo do zero ou ao retomar o trabalho depois de
perder continuidade confiavel.

## Quando executar

- primeira abertura do repo em uma sessao nova
- retomada apos queda de energia, travamento, limpeza de cache ou limpeza de
  sessoes
- reabertura depois de trocar de app, modelo, branch ou worktree sem prova de
  continuidade fiel
- antes de tentar reduzir worktree suja, redistribuir alteracoes pendentes ou
  decidir o proximo **work item** so pela memoria da ultima sessao

## Startup do zero

1. Ler integralmente todos os arquivos resolvidos por
   [`AI-STARTUP-GOVERNANCE-MANIFEST.md`](AI-STARTUP-GOVERNANCE-MANIFEST.md).
2. Ler o registro vivo de contratos de chat em
   [`AI-CHAT-CONTRACTS-REGISTER.md`](AI-CHAT-CONTRACTS-REGISTER.md).
3. Recalcular inventario de branches e worktrees abertas antes de tocar em
   qualquer arvore dirty.
4. Rodar `task ai:worklog:check` e tratar o resultado como fallback local,
   nunca como substituto do quadro vivo do `Jira`.
5. Consultar o `Jira` como fonte primaria do backlog, do **WIP** e da ordem de
   prioridade.
6. Ler o **board** da direita para a esquerda, tentando primeiro destravar ou
   concluir o que estiver mais perto de terminar.
7. Cruzar cada trilha local aberta com seu **work item** dono antes de decidir
   commit, push, **PR** ou redistribuicao de alteracoes.
8. Avisar o usuario se houver contratos nascidos no chat ainda nao perenizados,
   listando quais estao pendentes e quais ja tem **work item** dono.
9. So depois desse preflight completo escolher a proxima
   **fatia de incremento testavel**.

## Restart com continuidade comprovada

Quando a propria sessao ainda preserva contexto confiavel e o estado local foi
validado na mesma rodada, o fluxo pode ser reduzido para:

1. reler o **work item** ativo, os arquivos tocados e a ultima evidencia real
2. validar `task ai:worklog:check`
3. revalidar branch, worktree e dirty tree
4. retomar a **fatia de incremento testavel** do ponto em que ela parou

Se qualquer uma dessas quatro confirmacoes falhar, o fluxo volta
automaticamente para o **startup do zero**.

## Saidas obrigatorias

- lista resolvida dos arquivos canonicos lidos
- inventario atual de worktrees e branches abertas
- quadro de contratos do chat ainda pendentes de promocao
- indicacao explicita do **work item** priorizado para a rodada seguinte

## Automacao oficial

- task manual e repetivel:
  [`ai:startup:session`](TASKS.md#aistartupsession)
- relatorio gerado localmente:
  `.cache/ai/startup-session.md`

## Regra de manutencao

- sempre que nascer novo contrato de governanca, ele deve entrar na
  documentacao oficial ou no registro vivo de contratos do chat
- sempre que nascer nova fonte normativa, o manifest deve ser atualizado
- sempre que o startup mudar, esta pagina e a task oficial precisam mudar na
  mesma rodada
