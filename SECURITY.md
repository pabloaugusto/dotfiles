# Security Guide

Guia de segurança para operar/publicar este repositório.

## Nunca versionar

- chaves privadas (`*.pem`, `*.p12`, `*.pfx`, `*.key`)
- arquivos `.env` plaintext (`.env`, `.env.local`, `.env.*`)
- tokens exportados em texto
- arquivos locais não versionados (`bootstrap/user-config.yaml`, `df/git/.gitconfig.local`)

## Modelo atual do projeto

- refs de segredo em `op://...` (1Password)
- runtime env local cifrado em `~/.env.local.sops`
- `SOPS_AGE_KEY` em env de usuário (sem `keys.txt` por padrão)
- SSH + assinatura Git via 1Password SSH Agent

## Checklist antes de push/publicação

1. scan de segredos:
   - `git grep -n "ghp_|github_pat_|AKIA|BEGIN .*PRIVATE KEY|xoxb-|AIza"`
2. verificar ignorados/sensíveis:
   - `git status --ignored`
3. revisar staged diff:
   - `git diff --staged`

## Se uma credencial for exposta

1. revogar/rotacionar imediatamente
2. remover do código e histórico (`git filter-repo`/BFG)
3. force-push do histórico limpo
4. invalidar credenciais derivadas
5. notificar colaboradores para re-clone/reset conforme necessário

## Hardening recomendado

- pre-commit secret scanner (`gitleaks`, `detect-secrets`)
- branch protection ativa no GitHub
- token dedicado por projeto com menor privilégio possível
- auditoria periódica com `checkEnv` e revisão de configs SSH/Git
