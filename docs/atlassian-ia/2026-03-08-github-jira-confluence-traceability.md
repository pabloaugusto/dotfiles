# Integracao GitHub + Jira + Confluence

- Status: `research-backed-planning`
- Data-base: `2026-03-08`
- Relacionados:
  - [`2026-03-08-github-for-atlassian-runbook.md`](2026-03-08-github-for-atlassian-runbook.md)
  - [`../../docs/ai-operating-model.md`](../../docs/ai-operating-model.md)
  - [`../../Taskfile.yml`](../../Taskfile.yml)
  - [`../../docs/git-conventions.md`](../../docs/git-conventions.md)

## Objetivo

Definir a integracao canonica entre `GitHub`, `Jira` e `Confluence` para que:

- branches, commits, PRs, releases, workflows e deployments fiquem rastreaveis
  no `Jira`
- a documentacao oficial em `Confluence` aponte para as mudancas reais do
  `GitHub`
- o fluxo de trabalho do repo mantenha rastreabilidade ponta a ponta sem
  depender de comentario manual solto

## Decisao recomendada

Adotar como baseline:

1. `GitHub for Atlassian` como integracao oficial entre `GitHub` e `Jira`
2. chave Jira obrigatoria em branch, commit e PR
3. workflows e deployments do `GitHub Actions` ligados ao `Jira`
4. referencias do repo no `Jira` e no `Confluence` sempre em URL do `GitHub`
5. `Smart Commits` como capacidade opcional e governada, nao como baseline
6. reparo retroativo obrigatorio sempre que a automacao gerar descricao,
   comentario ou pagina com path local sem URL oficial do `GitHub`

## O que as fontes oficiais confirmam

Segundo a documentacao oficial da Atlassian:

- quando as chaves do work item entram em branches, commits e pull requests, o
  `Jira` passa a mostrar branches, PRs, commits, builds e deployments no painel
  de desenvolvimento, no board, na Development page, no Code tab, no Releases
  hub e na timeline de deployments
- para branches, basta incluir a chave no nome da branch
- para commits, basta incluir a chave na mensagem do commit
- para PRs, a chave pode estar no titulo do PR ou no nome da branch de origem
- workflows e deployments do `GitHub Actions` podem ser ligados ao `Jira` via
  `GitHub for Atlassian`, desde que os eventos corretos sejam emitidos
- `Smart Commits` permitem comentar, registrar tempo e transicionar issues a
  partir do commit, mas a propria Atlassian registra um aviso de seguranca sobre
  acesso elevado

Isso sustenta uma separacao boa de camadas:

- baseline obrigatoria: issue key + development panel + workflows/deployments
- capacidade opcional: `Smart Commits`

## Padrao operacional recomendado

### Branches

- padrao canonico: `<type>/<jira-key>-<slug>`
- exemplo: `feat/DOT-78-github-traceability`

Motivo:

- respeita o contrato do repo para branch
- satisfaz a regra do `Jira` para link automatico da branch

Transicao recomendada:

- branches legadas ja abertas no piloto podem continuar temporariamente no
  formato antigo `<type>/<slug>` ate serem encerradas
- toda branch nova da fase GitHub + Jira + Confluence deve nascer no formato
  canonico com chave Jira

### Commits

- padrao recomendado: `emoji + conventional commit + jira key`
- exemplo: `🔧 feat(jira): DOT-78 integrar rastreabilidade GitHub`

Motivo:

- preserva a convencao do repo
- satisfaz a regra da Atlassian para link automatico do commit

### Pull requests

- titulo deve repetir a chave Jira
- exemplo: `🔧 feat(jira): DOT-78 integrar rastreabilidade GitHub`

Motivo:

- o `Jira` liga PR por titulo e/ou branch
- manter a chave no titulo reduz falsos negativos

### Releases, tags e deployments

- releases e tags devem manter a referencia da issue ou do epic no corpo da
  release note quando fizer sentido
- o baseline tecnico deve ligar `GitHub Actions` ao `Jira`
- deployments precisam emitir os eventos aceitos pela integracao oficial

## Smart Commits: decisao de baseline

Recomendacao:

- `nao` habilitar `Smart Commits` como baseline obrigatoria na v1
- `sim` analisar habilitacao controlada em demanda propria

Motivo:

- a Atlassian confirma que `Smart Commits` podem comentar, registrar tempo e
  transicionar issues
- a mesma documentacao traz um aviso de seguranca sobre elevacao de privilegio
  via autoria de commit

Entao a leitura mais segura para este piloto e:

- v1: rastreabilidade por issue key + app oficial + automacao explicita
- v2: avaliar `Smart Commits` sob politica de seguranca

## Confluence no fluxo

O `Confluence` nao substitui o `GitHub` como fonte de mudanca tecnica. O papel
dele aqui e:

- guardar runbooks, ADRs, plano de rollout e governanca da integracao
- apontar para branches, PRs, workflows e releases quando a documentacao exigir
  prova operacional
- ser linkado nas issues do `Jira`

Regra recomendada:

- pagina de `Confluence` cita PR/branch/release por URL real do `GitHub`
- issue do `Jira` cita pagina do `Confluence` e item do `GitHub`

## Permissoes e pre-requisitos

Segundo a documentacao oficial da Atlassian, a integracao precisa de:

- permissao `Read, write, and admin access for development information` no lado
  `Jira`
- acesso `read` a conteudo, metadata e deployments no lado `GitHub`
- acesso `write` a conteudo quando se quer criar branch pelo painel do work item
- eventos de webhook para repository, push, pull request, pull request review,
  deployment status e workflow run

Camada adicional deste piloto:

- probes administrativos do `gh` precisam considerar a precedencia de
  `GH_TOKEN` e `GITHUB_TOKEN` no shell
- `gh api user/ssh_signing_keys` e um probe valido para PAT administrativo
- `gh api user/installations` nao e um probe valido com PAT; segundo a
  documentacao oficial do GitHub, esse endpoint exige `GitHub App user access
  token`
- por isso, a validacao da instalacao do `GitHub for Atlassian` deve combinar:
  - [`task github:auth:probe`](../../docs/TASKS.md)
  - checklist manual do runbook
  - evidencia direta no `Jira` e no `Confluence`

## Plano faseado recomendado

### Fase 1. Fundacao

- instalar e conectar `GitHub for Atlassian`
- validar organizacoes e repositorios necessarios
- confirmar permissao para development panel

### Fase 2. Convencoes do repo

- endurecer branch naming com issue key obrigatoria
- endurecer commit e PR title com issue key obrigatoria
- refletir isso nos validadores locais e no `GitHub Actions`

### Fase 3. Workflows e deployments

- ligar `workflow run` e `deployment_status` ao `Jira`
- mapear ambientes de deployment
- validar cards do board, Development page e Deployments page
- baseline repo-side deste piloto:
  - [`.jira/config.yml`](../../.jira/config.yml) para environment mapping
  - [`.github/workflows/jira-deployment-marker.yml`](../../.github/workflows/jira-deployment-marker.yml)
    para publicar um deployment controlado via `GitHub Actions`

### Fase 4. Documentacao e operacao

- registrar runbook oficial no `Confluence`
- registrar comentarios estruturados no `Jira` com links de PR, workflow e
  deployment
- refletir releases, tags e evidencias oficiais no fluxo

### Fase 5. Capabilidades opcionais

- avaliar `Smart Commits`
- avaliar branch creation a partir do painel de desenvolvimento do `Jira`
- avaliar automacoes adicionais com triggers DevOps do `Jira Automation`

## Criterios de aceite para a demanda de implementacao

- o repositorio fica conectado ao `Jira` pela integracao oficial
- branches, commits e PRs passam a aparecer no development panel das issues
- workflows e deployments relevantes passam a aparecer no `Jira`
- o padrao de branch, commit e PR fica documentado e validado no repo
- `Confluence`, `Jira` e `GitHub` ficam mutuamente referenciados no fluxo

## Fontes oficiais principais

- [`Atlassian Support - Integrate Jira with GitHub`](https://support.atlassian.com/jira-cloud-administration/docs/integrate-jira-software-with-github/)
- [`Atlassian Support - Link GitHub development information to Jira work items`](https://support.atlassian.com/jira-cloud-administration/docs/use-the-github-for-jira-app/)
- [`Atlassian Support - Reference work items in your development spaces`](https://support.atlassian.com/jira-software-cloud/docs/reference-issues-in-your-development-work/)
- [`Atlassian Support - Link GitHub workflows and deployments to Jira work items`](https://support.atlassian.com/jira-cloud-administration/docs/link-github-workflows-and-deployments-to-jira-issues/)
- [`Atlassian Support - Permissions required for GitHub for Atlassian`](https://support.atlassian.com/jira-cloud-administration/docs/permissions-required-for-github-for-jira/)
- [`Atlassian Support - Enable Smart Commits`](https://support.atlassian.com/jira-cloud-administration/docs/enable-smart-commits/)
- [`Atlassian Support - GitHub for Atlassian integration FAQ`](https://support.atlassian.com/jira-cloud-administration/docs/github-integration-faq/)
- [`Atlassian Marketplace - GitHub for Atlassian`](https://marketplace.atlassian.com/apps/1219592/github-for-atlassian?hosting=cloud&tab=overview)
