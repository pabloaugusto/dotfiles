# Security Guide

Guia de seguranca para operar e publicar este repositorio.

## Nunca versionar

- chaves privadas (`*.pem`, `*.p12`, `*.pfx`, `*.key`)
- arquivos `.env` plaintext (`.env`, `.env.local`, `.env.*`)
- tokens exportados em texto
- arquivos locais nao versionados:
  - `bootstrap/user-config.yaml`
  - `df/git/.gitconfig.local`
- runtime local de IA:
  - `.gemini/`
  - sessoes, caches, bancos SQLite e historico
  - perfis de navegador
  - auth, cookies, state files e configuracoes geradas por login

## Modelo atual do projeto

- refs de segredo em `op://...`
- runtime env local cifrado em `~/.env.local.sops`
- `SOPS_AGE_KEY` persistido no ambiente de usuario
- SSH e assinatura Git via 1Password SSH Agent e `op-ssh-sign`
- `.agents/` como camada declarativa versionavel; runtime local de assistentes
  fica fora do Git

## Checklist antes de push

1. procurar segredos:
   - `git grep -n "ghp_|github_pat_|AKIA|BEGIN .*PRIVATE KEY|xoxb-|AIza"`
2. revisar ignorados e sensiveis:
   - `git status --ignored`
3. revisar diff staged:
   - `git diff --staged`
4. quando a mudanca tocar auth ou bootstrap:
   - `task env:check`

## Se uma credencial for exposta

1. revogar ou rotacionar imediatamente
2. remover do codigo e do historico (`git filter-repo` ou BFG)
3. force-push do historico limpo quando aplicavel
4. invalidar credenciais derivadas
5. avisar colaboradores para re-clone ou reset conforme necessario

## Hardening recomendado

- branch protection no GitHub
- token dedicado por projeto com menor privilegio possivel
- auditoria periodica com `checkEnv`
- revisao de configuracoes SSH e Git signer
- scanner de segredos em pre-commit ou CI (`gitleaks`, `detect-secrets`)

## Regra operacional

- segredo portavel e declarativo pode virar template ou ref versionado
- segredo materializado, token de sessao e estado de ferramenta nao entram no
  repositorio
