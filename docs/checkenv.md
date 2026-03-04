# checkEnv

`checkEnv` é o health-check de conformidade para autenticação, assinatura e SSH.

## Implementações

- PowerShell: `df/powershell/_functions.ps1` (`checkEnv`)
- Bash: `df/bash/.inc/check-env.sh` (`checkEnv`)

## Objetivo

Garantir, antes de operar no repositório, que o ambiente está aderente ao
modelo:

- 1Password para secrets/runtime
- GitHub CLI autenticado e usando SSH
- Git commits assinados com SSH via 1Password
- SSH agent do 1Password priorizado

## Como executar

PowerShell:

```powershell
checkEnv
```

Bash:

```bash
checkEnv
```

## O que é validado

1. binários essenciais (`op`, `gh`, `git`, `ssh`)
2. binários de criptografia (`sops`, `age`)
3. sessão 1Password (`op whoami`)
4. leitura de refs em `df/secrets/secrets-ref.yaml`
5. auth `gh` em `github.com` e `git_protocol=ssh`
6. política Git de assinatura:
   - `gpg.format=ssh`
   - `commit.gpgsign=true`
   - `user.signingkey` em formato SSH
   - `gpg.ssh.program` resolvível
7. política SSH:
   - `identityagent` coerente com 1Password
   - `identityfile none` (quando aplicável)
   - socket `/tmp/1password-agent.sock` no Unix/WSL
8. `ssh -T git@github.com`
9. commit assinado de teste em repo temporário
10. (Windows) conformidade de OneDrive/profile links quando `paths.windows.onedrive_enabled=true`

## Semântica de status

- `SUCCESS`: controle atendido.
- `FAIL`: controle obrigatório não atendido.
- `INCONCLUSIVE`: não foi possível afirmar com segurança.

No final, o comando imprime resumo e ações sugeridas.

## Retry automático

As implementações tentam reautenticar uma vez quando possível:

- `op` (via token já disponível no contexto)
- `gh` (via `GH_TOKEN`/`GITHUB_TOKEN` ou refs de 1Password)

## Comportamento no bootstrap

- Windows: `bootstrap/bootstrap-windows.ps1` roda `checkEnv` como gate final.
- Windows: em seguida roda validação dedicada de OneDrive/links (`Test-OneDriveLayoutHealth`).
- WSL: `bootstrap/bootstrap-ubuntu-wsl.sh` roda `checkEnv` como gate final.
- Qualquer `FAIL` interrompe o bootstrap.

## Falhas comuns e correções

- `GitHub CLI git protocol`:
  - `gh config set git_protocol ssh --host github.com`
- `1Password signer program`:
  - validar `gpg.ssh.program` e presença de `op-ssh-sign`
- `SSH auth to GitHub`:
  - validar chave no GitHub + 1Password SSH Agent ativo
- `Signed commit test`:
  - revisar `user.signingkey`, signer e agent
- `OneDrive root path` / `OneDrive profile links`:
  - validar `paths.windows.*` no `bootstrap/user-config.yaml`
  - rerodar bootstrap para recriar links e revisar root ativa do OneDrive
