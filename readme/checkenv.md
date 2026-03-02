# checkEnv

`checkEnv` é a rotina de health-check para validar se o ambiente está conforme o padrão esperado dos dotfiles.

## Onde está

- PowerShell: [df/powershell/_functions.ps1](../df/powershell/_functions.ps1)
- Bash: [df/bash/.inc/check-env.sh](../df/bash/.inc/check-env.sh)

## Como executar

PowerShell:
```powershell
checkEnv
```

Bash:
```bash
checkEnv
```

## Itens validados

1. Binários essenciais (`op`, `gh`, `git`, `ssh`).
2. Binários de criptografia (`sops`, `age`) como validação complementar.
3. Sessão ativa do 1Password (`op whoami`).
4. Leitura dos refs definidos em `df/secrets/secrets-ref.yaml`.
5. `gh` autenticado no `github.com` e protocolo configurado para SSH.
6. Configuração Git para assinatura SSH:
   - `gpg.format=ssh`
   - `commit.gpgsign=true`
   - `user.signingkey` em formato SSH
   - `gpg.ssh.program` válido
7. Configuração SSH:
   - `identityagent` coerente com 1Password
   - `identityfile none` para evitar fallback local
   - socket do agent no Unix/WSL (`/tmp/1password-agent.sock`)
8. Handshake `ssh -T git@github.com`.
9. Commit assinado de teste (`git commit -S`) em repositório temporário.

## Semântica de status

- `SUCCESS`: requisito atendido.
- `FAIL`: requisito obrigatório não atendido.
- `INCONCLUSIVE`: informação incompleta, opcional ou dependente de contexto externo.

## Comportamento no bootstrap

- Windows: `bootstrap/bootstrap-windows.ps1` roda `checkEnv` no final.
- WSL: `bootstrap/bootstrap-ubuntu-wsl.sh` roda `checkEnv` no final.
- Falhas (`FAIL`) interrompem bootstrap com erro explícito.

## Troubleshooting orientado por checkEnv

1. `GitHub CLI auth` falhou:
   - confirmar o ref `op://secrets/dotfiles/github/token` no 1Password
   - se necessário, validar fallback `op://secrets/github/api/token`
   - rodar `gh auth status`
2. `1Password signer program` falhou:
   - validar `gpg.ssh.program`
   - validar instalação do app 1Password
3. `SSH auth to GitHub` falhou:
   - confirmar chave pública no GitHub
   - confirmar agent 1Password habilitado
4. `Signed commit test` falhou:
   - revisar blocos Git + SSH do check
