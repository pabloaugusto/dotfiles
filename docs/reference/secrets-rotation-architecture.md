# Arquitetura de Rotacao de Secrets

Documento de referencia para a trilha canonica de rotacao de credenciais,
identidades SSH, service accounts e artefatos `sops+age` do repositorio.

## Objetivo

Materializar uma trilha unica, nao-destrutiva e auditavel para:

- inventariar alvos de rotacao
- classificar automacao real (`fully_automated`, `assisted`, `manual_blocked`)
- gerar plano ordenado sem revogar credenciais antes da validacao da substituta
- validar readiness operacional antes de qualquer corte destrutivo

## Fonte de verdade

- configuracao declarativa: [`config/secrets-rotation.yaml`](../../config/secrets-rotation.yaml)
- refs canonicas: [`app/df/secrets/secrets-ref.yaml`](../../app/df/secrets/secrets-ref.yaml)
- politica `sops+age`: [`app/df/secrets/dotfiles.sops.yaml`](../../app/df/secrets/dotfiles.sops.yaml)
- runtime cifrado: [`app/bootstrap/secrets/.env.local.tpl`](../../app/bootstrap/secrets/.env.local.tpl)
- runbook geral: [`docs/secrets-and-auth.md`](../secrets-and-auth.md)

## Interface canonica

Script:

- [`scripts/secrets-rotation.py`](../../scripts/secrets-rotation.py)

Core:

- [`scripts/secrets_rotation_lib.py`](../../scripts/secrets_rotation_lib.py)

Tasks:

- `task secrets:rotation:preflight`
- `task secrets:rotation:plan`
- `task secrets:rotation:validate`

## Operadores aceitos

Os operadores de missao critica desta trilha sao:

- `op`
- `gh`
- `glab`
- `sops`
- `age`
- `ssh`
- `ssh-keygen`
- `git`

Cada alvo so pode depender de operadores explicitamente declarados no core.

## Modelo de execucao

### 1. Preflight

Executa apenas leitura e probes seguros:

- disponibilidade de binarios
- autenticacao basica de `op`, `gh` e `glab`
- presenca de refs canonicas
- presenca de artefatos locais obrigatorios

Saida:

- status por target
- blockers
- warnings
- report JSON persistido em `audit.report_path`

### 2. Plan

Gera a ordem operacional por target, com passos e validadores sugeridos.

Nao executa rotacao nem altera estado externo.

### 3. Validate

Executa validacoes nao-destrutivas por alvo, como:

- handshake SSH com GitHub
- `git ls-remote` no remote alvo
- chamada `gh api` para PAT
- verificacao do recipient real no `sops`

## Matriz inicial de targets

### `github-ssh-auth`

- tipo: `github_ssh_identity`
- automacao: `fully_automated`
- finalidade: autenticacao GitHub via SSH

### `github-ssh-signing`

- tipo: `github_ssh_identity`
- automacao: `fully_automated`
- finalidade: assinatura Git com chave SSH dedicada

### `age-runtime`

- tipo: `age_runtime_key`
- automacao: `fully_automated`
- finalidade: recipient e artefatos cifrados do runtime local

### `onepassword-service-account`

- tipo: `onepassword_service_account`
- automacao: `assisted`
- finalidade: service account do app/bootstrap/control plane

### `github-project-pat`

- tipo: `github_pat`
- automacao: `assisted`
- finalidade: token de projeto para integracoes GitHub

## Guardrails

- nunca revogar primeiro
- nunca persistir segredo novo em plaintext
- nunca operar fora de refs canonicas quando existir ref canonica
- sempre manter um caminho de rollback explicito
- toda rotacao deve terminar com validacao operacional

## Evidencia

O report mais recente e persistido em:

- `audit.report_path` de [`config/secrets-rotation.yaml`](../../config/secrets-rotation.yaml)

Esse artefato serve como evidencia minima local antes de espelhamento em Jira e
Confluence.
