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
3. Carregar antes da primeira mensagem operacional ao usuario a camada de
   comunicacao no chat e a identidade humana oficial dos agentes
   (`display_name`), lembrando idioma, tom, formato de links e demais regras
   vivas da sessao.
4. Recalcular inventario de branches e worktrees abertas antes de tocar em
   qualquer arvore dirty.
5. Capturar tambem o ciclo de vida da branch atual: upstream, ahead/behind,
   absorcao em `origin/main`, `PR` aberto e candidatas objetivas a poda.
6. Detectar e registrar drift entre branch atual, `active execution`, worklog
   local e dirty tree antes de decidir commit, `PR`, merge ou redistribuicao.
7. Validar `gh auth status` antes de qualquer operacao que possa depender de
   `gh`, `GraphQL`, `PR`, merge, review ou sync com o GitHub.
8. Se a rodada puder tocar `PR`, merge ou comentario de `PR` via `gh`, executar
   tambem um probe GraphQL cedo e, em caso de falha, reaplicar a Cadeia de
   fallback GitHub/PAT `GH_TOKEN -> GITHUB_TOKEN -> op://secrets/dotfiles/github/token ->
   op://secrets/github/api/token -> op://Personal/github/token-full-access`
   documentada em [`docs/secrets-and-auth.md`](secrets-and-auth.md).
9. Rodar `task ai:worklog:check` e tratar o resultado como fallback local,
   nunca como substituto do quadro vivo do `Jira`.
10. Rodar `task ai:atlassian:check` ou conferir o resumo equivalente gerado por
   `task ai:startup:session` antes de assumir que `Jira` e `Confluence` estao
   operacionais para a rodada.
11. Se a rodada puder tocar o Atlassian, lembrar tambem `auth_mode`,
    `cloud_id`, `project_key`, `space_key` e a trilha documentada de
    recuperacao em [`docs/secrets-and-auth.md`](secrets-and-auth.md) antes de
    concluir que houve bloqueio estrutural.
12. Rodar `task ai:fallback:status` quando houver suspeita de degradacao do
   `Jira` ou quando existirem rastros locais ainda nao drenados.
13. Se o status vier como `degraded`, registrar a contingencia com
   `task ai:fallback:capture` antes de operar pelos trackers locais.
14. Se o status vier como `recovery`, drenar ou reconciliar os registros ativos
   com `task ai:fallback:resolve` antes de considerar o fallback vazio.
15. Consultar o `Jira` como fonte primaria do backlog, do **WIP** e da ordem de
   prioridade.
16. Ler o **board** da direita para a esquerda, tentando primeiro destravar ou
   concluir o que estiver mais perto de terminar, e puxando novo **work item**
   apenas quando ele for o desbloqueador direto do WIP ativo.
17. Relembrar antes de criar demanda nova as regras de dedupe de `issue` e
    reuse obrigatorio de `Epic` aberto aderente.
18. Cruzar cada trilha local aberta com seu **work item** dono antes de decidir
   commit, push, **PR** ou redistribuicao de alteracoes.
19. Verificar se a branch atual ja possui `PR` aberto e registrar esse estado
   no startup antes de decidir se a rodada vai abrir, atualizar ou mergear `PR`.
20. Avisar o usuario se houver contratos nascidos no chat ainda nao perenizados,
   listando quais estao pendentes e quais ja tem **work item** dono.
21. Antes de delegar para subagentes, preparar ou referenciar o pacote minimo
    de contexto da rodada: issue dona, branch atual, startup report, regras
    aplicaveis e caminhos normativos relevantes para o papel delegado.
22. So depois desse preflight completo escolher a proxima
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
- contrato de comunicacao com o usuario e camada de `display_name` lembrados na
  propria sessao antes da primeira mensagem operacional
- inventario atual de worktrees e branches abertas, com ciclo de vida da branch
  atual e sinais de poda
- drift objetivo entre branch atual, worklog, contexto local ativo e dirty tree
- status de `gh auth`, probe GraphQL e `PRs` abertos para a branch atual
- cadeia documentada de fallback GitHub/PAT lembrada na propria sessao
- resumo minimo da saude de `Jira` e `Confluence`, com memoria de recuperacao
  Atlassian suficiente para a rodada
- quadro de contratos do chat ainda pendentes de promocao
- pacote minimo de contexto obrigatorio para subagentes quando houver delegacao
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
- startup que esquecer contrato de comunicacao, `display_name`, auth GitHub,
  fallback PAT, ciclo da branch atual, `PR` da branch atual, saude minima do
  Atlassian ou contexto minimo de subagente deve ser tratado como drift
  operacional, nao como detalhe
- trabalho iniciado sem essa absorcao integral de contexto deve ser considerado
  **REJEITADO** ate que o startup oficial seja executado corretamente
