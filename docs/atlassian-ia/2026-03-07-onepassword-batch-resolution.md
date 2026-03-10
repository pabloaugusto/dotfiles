# 1Password Batch Resolution

- Status: `implementado-no-control-plane`
- Data-base: `2026-03-07`
- Relacionados:
  - [`../../scripts/ai_control_plane_lib.py`](../../scripts/ai_control_plane_lib.py)
  - [`../../tests/python/ai_control_plane_test.py`](../../tests/python/ai_control_plane_test.py)
  - [`../../docs/secrets-and-auth.md`](../../docs/secrets-and-auth.md)
  - [`2026-03-07-atlassian-auth-scopes-and-permissions.md`](2026-03-07-atlassian-auth-scopes-and-permissions.md)

## Objetivo

Reduzir chamadas ao `1Password CLI`, evitar `Too many requests` e impedir que a
camada Atlassian espalhe `op read` repetitivo pelo dominio.

## Regra canonica

- resolver refs `op://...` em lote na borda do processo
- manter cache apenas em memoria durante a execucao
- usar fallback por item, nao por campo
- nao paralelizar probes remotos que dependam do mesmo item do `1Password`

## Estrategia implementada

1. [`resolve_atlassian_platform()`](../../scripts/ai_control_plane_lib.py)
   coleta todos os refs Atlassian do control plane.
2. [`prime_op_ref_cache()`](../../scripts/ai_control_plane_lib.py) cria um
   `.env` temporario com esses refs.
3. O processo executa `op run --env-file <tmp>` uma unica vez.
4. Os valores resolvidos entram em cache por processo.
5. Se o batch falhar, [`resolve_op_value()`](../../scripts/ai_control_plane_lib.py)
   cai para `op item get --format json` por item.
6. `op read` fica reservado a fallback pontual.

## Motivacao

- `site_url`, `email`, `token`, `service_account`, `cloud_id`, `project_key` e
  `space_key` vivem hoje no mesmo item Atlassian do `1Password`
- leituras granulares por campo aumentam latencia e risco de rate limit
- o batch com `op run` preserva o contrato `op://...` sem exigir secrets em disco

## Estado conhecido

- o control plane ja esta preparado para batch resolution
- em `2026-03-07`, o `1Password CLI` continuou respondendo `Too many requests`
  mesmo apos migracao para `op run`; portanto o bloqueio atual e externo ao
  codigo do apply
- no mesmo dia, um teste com service account de fallback confirmou que o cap
  bloqueante era `account.read_write`, nao `token.read`; portanto um segundo
  token da mesma conta nao bastou para destravar a leitura
- assim que o cofre estabilizar, o proximo passo tecnico segue sendo
  `plan -> apply` em serie no `Jira`

## Validacao local

- `uv run --locked python -m unittest tests.python.ai_control_plane_test`
- `uv run --locked ty check scripts/ai_control_plane_lib.py tests/python/ai_control_plane_test.py`
- `task ai:validate`
- `task docs:check`
