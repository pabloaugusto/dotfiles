# Bootstrap de Autenticacao Atlassian via Playwright

- Status: `planejado-para-bootstrap-humano`
- Data-base: `2026-03-08`
- Relacionados:
  - [`2026-03-07-diagnostico-auth-e-acesso-atlassian.md`](2026-03-07-diagnostico-auth-e-acesso-atlassian.md)
  - [`artifacts/agent-operations.md`](artifacts/agent-operations.md)
  - [`../../config/ai/contracts.yaml`](../../config/ai/contracts.yaml)
  - [`../../config/ai/agents.yaml`](../../config/ai/agents.yaml)

## Decisao

Para validacao visual de `Jira` e `Confluence`, o fluxo canonico de autenticacao
deve usar `Playwright` com:

1. bootstrap humano inicial do login Atlassian
2. persistencia local de `storageState`
3. reuso desse estado nas execucoes seguintes do browser validator

Nao devemos tentar automatizar `MFA`, `2FA` ou `SSO` no bootstrap. Essa etapa e
humana por definicao.

## Motivo

- o login web da Atlassian pode envolver `SSO`, `MFA` e redirecionamentos
- `service account token` resolve o plano `REST`, nao o login interativo de UI
- `storageState` e o padrao mais estavel para reuso de sessao no `Playwright`
- a validacao visual precisa de evidencia navegavel e screenshots, nao apenas
  probes de API

## Fluxo canonico

### Fase 1. Bootstrap humano

- abrir `Chromium` em modo visivel
- navegar por padrao para a home do `Confluence` do tenant (`/wiki/home`)
  - o bootstrap de sessao nao deve depender de uma pagina ou `space` especifico
    antes do login
- salvar screenshot inicial
- aguardar o humano concluir:
  - email
  - senha
  - `SSO`, se existir
  - `MFA`, se existir
- confirmar que a UI autenticada carregou e que o navegador saiu de
  `id.atlassian.com`
- salvar screenshot de sessao autenticada
- persistir `storageState` local

### Fase 2. Execucao automatica recorrente

- abrir `browser context` com `storageState`
- validar que a sessao nao caiu em login
- navegar por URL direta ou por busca na UI
- validar titulo, trechos obrigatorios e metadados
- salvar screenshots por checkpoint
- registrar `PASS` ou `FAIL` estruturado

## Evidencias minimas

- `01-home-logado.png`
- `02-busca-preenchida.png` ou `02-pagina-direta.png`
- `03-resultado-encontrado.png` quando houver busca
- `04-pagina-aberta.png`
- `05-titulo-validado.png`
- `06-body-validado.png`
- `07-full-page.png`
- `resultado.json`

## Status de falha canonicos

- `REAUTENTICACAO_NECESSARIA`
- `LOGIN_REQUIRED`
- `PAGE_NOT_FOUND`
- `PERMISSION_DENIED`
- `TITLE_MISMATCH`
- `BODY_TEXT_NOT_FOUND`
- `SEARCH_RESULT_NOT_FOUND`
- `UI_TIMEOUT`

## Armazenamento local

O `storageState` deve ficar fora do versionamento, em caminho local ignorado,
por exemplo:

- `.cache/playwright/atlassian/storage-state.json`

As evidencias tambem devem ficar fora do versionamento por padrao, salvo quando
forem promovidas a bundle auditavel de uma issue especifica.

## Tasks canonicas

- `task ai:atlassian:browser:install`
- `task ai:atlassian:browser:auth:bootstrap`
- `task ai:atlassian:browser:auth:status`

## Regra operacional

- sem `storageState` valido, o browser validator deve falhar cedo com
  `REAUTENTICACAO_NECESSARIA`
- o operador humano so deve pressionar `Enter` depois de ver a UI final de
  `Jira` ou `Confluence`, nao ainda na tela de login
- sem screenshot, nao existe validacao visual completa
- sempre que possivel, a validacao visual deve ser refletida em comentario
  estruturado no `Jira` e, quando fizer sentido, em pagina ou anexo no
  `Confluence`
