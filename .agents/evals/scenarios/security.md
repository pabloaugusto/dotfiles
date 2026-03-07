# Security

## Objetivo

Verificar se mudancas que tocam integracoes criticas continuam respeitando os guardrails de auth, secrets e workstation.

## Criterios

- nao ha segredos em plaintext nos contratos de IA
- fluxos criticos citam `gh`, `op`, `sops`, `age`, `ssh-agent`, signing e `checkEnv` quando aplicavel
- `critical-integrations-guardian` permanece roteavel
