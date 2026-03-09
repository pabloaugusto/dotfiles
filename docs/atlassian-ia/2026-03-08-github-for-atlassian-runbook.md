# GitHub for Atlassian Runbook

- Status: `operational-baseline`
- Data-base: `2026-03-08`
- Relacionados:
  - [`2026-03-08-github-jira-confluence-traceability.md`](2026-03-08-github-jira-confluence-traceability.md)
  - [`artifacts/jira-writing-standards.md`](artifacts/jira-writing-standards.md)
  - [`artifacts/agent-operations.md`](artifacts/agent-operations.md)
  - [`../../docs/git-conventions.md`](../../docs/git-conventions.md)
  - [`../../Taskfile.yml`](../../Taskfile.yml)

## Objetivo

Padronizar o setup e a operacao da integracao oficial entre `GitHub`, `Jira` e
`Confluence` neste piloto, garantindo rastreabilidade ponta a ponta para:

- branches
- commits
- pull requests
- workflows
- deployments
- releases
- documentacao oficial

## Quando usar este runbook

Use este runbook quando for necessario:

- conectar ou revisar o app `GitHub for Atlassian`
- validar o painel `Development` do `Jira`
- confirmar que branch, commit e PR aparecem nas issues
- ligar workflows e deployments do `GitHub Actions` ao `Jira`
- revisar a trilha documental entre `Jira`, `Confluence` e `GitHub`

## Resultado esperado

Ao final do fluxo:

- a issue do `Jira` mostra evidencias de desenvolvimento no painel `Development`
- a pagina oficial do `Confluence` referencia a mudanca real no `GitHub`
- a automacao local do repo valida branch, commit e PR com chave Jira
- a equipe humana consegue auditar a entrega sem depender do historico do chat

## Pre-requisitos

- tenant `Jira Cloud` operacional
- `Confluence` ativo no mesmo tenant
- app `GitHub for Atlassian` instalado e conectado
- repositorio e organizacao corretos autorizados no app
- permissao administrativa suficiente no `Jira` e no `GitHub`
- chave Jira obrigatoria em branch, commit e PR
- `gh` autenticado para os probes locais de suporte

## Passo a passo de acesso e autenticacao

### 0. Validar a credencial efetiva do `gh`

Rodar primeiro:

```bash
task github:auth:probe
```

Objetivo:

- confirmar se o shell esta usando `GH_TOKEN` ou `GITHUB_TOKEN`
- confirmar se a credencial salva do `gh` no keyring assume o controle quando os
  env vars saem da frente
- validar se `gh api user/ssh_signing_keys` esta acessivel
- evitar falso negativo ao testar administracao do GitHub com o token errado

Observacao importante:

- [`List app installations accessible to the user access token`](https://docs.github.com/rest/apps/installations#list-app-installations-accessible-to-the-user-access-token)
  exige `GitHub App user access token`; esse endpoint nao serve como probe com
  PAT administrativo comum
- [`List SSH signing keys for the authenticated user`](https://docs.github.com/rest/users/ssh-signing-keys#list-ssh-signing-keys-for-the-authenticated-user)
  e um probe valido para o fluxo de signer tecnico

### 1. Entrar na administracao oficial da integracao

Abrir:

- [`Atlassian Support - Integrate Jira with GitHub`](https://support.atlassian.com/jira-cloud-administration/docs/integrate-jira-software-with-github/)
- [`Atlassian Support - Use the GitHub for Atlassian app`](https://support.atlassian.com/jira-cloud-administration/docs/use-the-github-for-jira-app/)
- [`Atlassian Marketplace - GitHub for Atlassian`](https://marketplace.atlassian.com/apps/1219592/github-for-atlassian?hosting=cloud&tab=overview)

Checkpoint visual recomendado:

- `01-atlassian-github-app-overview.png`

### 2. Autorizar organizacao e repositorio corretos

No fluxo do app:

- confirmar que a organizacao `GitHub` correta esta conectada
- confirmar que o repositorio do piloto esta incluso
- registrar qualquer excecao de permissao diretamente na issue ativa do `Jira`

Checkpoints visuais recomendados:

- `02-github-app-org-authorized.png`
- `03-github-app-repo-authorized.png`

### 3. Validar o painel Development no Jira

Depois da conexao:

- abrir uma issue alvo no `Jira`
- checar `Development`, `Code`, `Releases` e `Deployments` quando aplicavel
- se a rodada depender de browser validation, anexar screenshot real na issue

Checkpoints visuais recomendados:

- `04-jira-development-panel.png`
- `05-jira-code-tab.png`
- `06-jira-deployments.png`

### 4. Registrar evidencias

Toda rodada de login ou acesso administrativo deve deixar:

- link oficial da tela usada
- comentario estruturado na issue ativa do `Jira`
- pagina ou runbook atualizado no `Confluence` quando a regra mudar
- evidencias visuais quando o fluxo passar por UI

## Convencoes obrigatorias deste repo

- branch no formato `<type>/<jira-key>-<slug>`
  - exemplo: `feat/DOT-79-github-traceability`
- commit no formato `emoji + conventional commit + jira key`
  - exemplo: `✨ feat(git): DOT-79 integrar development traceability`
- PR com a chave Jira no titulo
- referencias a arquivos do repo em `Jira` e `Confluence` sempre por URL do
  `GitHub`

## Artefatos repo-side desta integracao

- [`.jira/config.yml`](../../.jira/config.yml)
  - mapeia os nomes de ambiente do piloto para as quatro categorias aceitas
    pelo `Jira`: `development`, `testing`, `staging` e `production`
- [`.github/workflows/jira-deployment-marker.yml`](../../.github/workflows/jira-deployment-marker.yml)
  - cria um deployment controlado via `workflow_dispatch` para emitir
    `deployment` e `deployment_status`
  - exige que o commit `HEAD` da rodada ja referencie a chave Jira informada
    para manter a associacao correta no painel de desenvolvimento

## Passo a passo operacional

### 1. Confirmar a fundacao da integracao

- abrir a administracao do `Jira`
- validar que o app `GitHub for Atlassian` esta conectado
- confirmar que a organizacao e o repositorio corretos estao autorizados
- registrar a evidencia da conexao em issue ou pagina oficial quando houver
  alteracao relevante

### 2. Validar a nomenclatura de desenvolvimento

- criar ou reutilizar uma branch com chave Jira
- executar os validadores locais do repo
- confirmar que o commit inclui a chave Jira
- confirmar que o titulo do PR inclui a chave Jira

### 3. Validar o painel Development

- abrir a issue alvo no `Jira`
- verificar se branch, commit e PR aparecem no painel `Development`
- se nao aparecerem, revisar:
  - conexao do app
  - branch name
  - commit message
  - titulo do PR
  - permissao do repositorio no app

### 4. Validar workflows e deployments

- confirmar que o `GitHub Actions` esta emitindo `workflow run`
- confirmar que deployments relevantes usam ambientes nomeados de forma estavel
- abrir a issue no `Jira` e verificar se builds e deployments aparecem na
  pagina de desenvolvimento
- quando a rodada exigir prova de deployment no piloto, disparar
  [`jira-deployment-marker.yml`](../../.github/workflows/jira-deployment-marker.yml)
  com a chave Jira da entrega e um ambiente mapeado em
  [`.jira/config.yml`](../../.jira/config.yml)

### 5. Fechar a trilha documental

- comentar na issue do `Jira` com o que foi feito
- anexar ou linkar evidencias reais
- publicar ou atualizar a pagina correspondente no `Confluence`
- garantir que `Jira`, `Confluence` e `GitHub` se apontem mutuamente

## Evidencias minimas por rodada

- URL da issue no `Jira`
- URL da pagina no `Confluence`
- URL da branch ou do PR no `GitHub`
- URL do workflow ou deployment quando aplicavel
- comentario estruturado do agente que executou a etapa

## Criterios de aceite

- a integracao oficial esta conectada ao repositorio correto
- a issue mostra branch, commit e PR no `Jira`
- workflows e deployments aparecem quando a rodada exige esse tipo de evidencia
- ambientes customizados do piloto deixam de cair como `Undefined Environment`
  no `Jira`
- a pagina do `Confluence` referencia os links reais do `GitHub`
- os comentarios em `Jira` registram agente, contexto, evidencias e proximo
  passo

## Diagnostico rapido

### Branch, commit ou PR nao aparecem no Jira

Verificar:

- se a chave Jira esta presente e correta
- se a branch foi criada depois da integracao
- se o app tem acesso ao repositorio
- se o PR herda a branch correta

### Workflow ou deployment nao aparece

Verificar:

- se o app esta habilitado para dados de desenvolvimento
- se o workflow executou no repositorio conectado
- se o deployment publicou status em um ambiente suportado

### Documentacao ficou sem utilidade pratica

Verificar:

- se o `Confluence` aponta para URLs do `GitHub`, e nao para paths locais
- se a issue do `Jira` aponta para a pagina oficial do `Confluence`
- se as evidencias estao no comentario do agente responsavel

## Decisoes operacionais adotadas

- `Smart Commits` nao fazem parte do baseline da v1
- links entre issues devem priorizar `Epic`, `Parent` e dependencias reais
- comentarios e mudancas de status precisam ficar em paridade temporal
- cada agente registra seu proprio trabalho na issue que tocou

## Referencias oficiais principais

- [`Atlassian Support - Integrate Jira with GitHub`](https://support.atlassian.com/jira-cloud-administration/docs/integrate-jira-software-with-github/)
- [`Atlassian Support - Use the GitHub for Atlassian app`](https://support.atlassian.com/jira-cloud-administration/docs/use-the-github-for-jira-app/)
- [`Atlassian Support - Link GitHub workflows and deployments to Jira work items`](https://support.atlassian.com/jira-cloud-administration/docs/link-github-workflows-and-deployments-to-jira-issues/)
- [`Atlassian Support - Reference work items in your development work`](https://support.atlassian.com/jira-software-cloud/docs/reference-issues-in-your-development-work/)
- [`Atlassian Support - Permissions required for GitHub for Atlassian`](https://support.atlassian.com/jira-cloud-administration/docs/permissions-required-for-github-for-jira/)
- [`GitHub REST - List app installations accessible to the user access token`](https://docs.github.com/rest/apps/installations#list-app-installations-accessible-to-the-user-access-token)
- [`GitHub REST - List SSH signing keys for the authenticated user`](https://docs.github.com/rest/users/ssh-signing-keys#list-ssh-signing-keys-for-the-authenticated-user)
