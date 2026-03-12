# Auth Secrets And Critical Integrations Rules

## Objetivo

Consolidar auth, secrets e tooling critica do workstation.

## Escopo

- `gh`, `op`, `sops`, `age`, `ssh-agent`
- signing
- secrets e auth

## Fonte canonica e precedencia

- [`../../docs/secrets-and-auth.md`](../../docs/secrets-and-auth.md)
- [`security.rules`](security.rules)
- [`../../AGENTS.md`](../../AGENTS.md)

## Regras obrigatorias

- proteger integracoes criticas antes de alterar bootstrap, auth ou sync
- nunca introduzir secrets em plaintext
- signer tecnico dedicado em worktree de automacao
- cadeias de fallback documentadas precisam ser relembradas no startup

## Startup: o que precisa ser carregado

- auth GitHub
- probes Atlassian quando aplicavel
- contexto de signing e integrações criticas

## Delegacao: o que o subagente precisa receber

- risco operacional
- ferramenta critica afetada
- regras de seguranca e continuidade

## Fallback e Recuperacao

- usar fallback GitHub/PAT documentado
- preservar credencial antiga ate validar a nova em rotacao

## Enforcement e validacoes

- `task ai:atlassian:check`
- `task env:check`
- `task git:signing:mode:automation`

## Artefatos relacionados

- [`../../app/df/secrets/secrets-ref.yaml`](../../app/df/secrets/secrets-ref.yaml)
- [`../../config/ai/platforms.yaml`](../../config/ai/platforms.yaml)

## Temas vizinhos

- [`sync-foundation-rules.md`](sync-foundation-rules.md)
- [`source-audit-and-cross-repo-rules.md`](source-audit-and-cross-repo-rules.md)
