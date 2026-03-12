# checkEnv

`checkEnv` é o health-check de conformidade para autenticação, assinatura e SSH.

## Implementações

- PowerShell: [`app/df/powershell/_functions.ps1`](../app/df/powershell/_functions.ps1) (`checkEnv`)
- Bash: [`app/df/bash/.inc/check-env.sh`](../app/df/bash/.inc/check-env.sh) (`checkEnv`)

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
4. leitura de refs em [`app/df/secrets/secrets-ref.yaml`](../app/df/secrets/secrets-ref.yaml)
5. auth `gh` em `github.com` e `git_protocol=ssh`
6. política Git de assinatura:
   - `gpg.format=ssh`
   - `commit.gpgsign=true`
   - `user.signingkey` em formato SSH no modo humano ou apontando para a chave
     técnica local no modo `automation`
   - `gpg.ssh.program` resolvível para o signer efetivo do modo atual
7. política SSH:
   - `identityagent` coerente com 1Password
   - `identityfile none` (quando aplicável)
    - socket `/tmp/1password-agent.sock` no Unix/WSL
8. autenticação GitHub:
   - fluxo humano: `ssh -T git@github.com`
   - fluxo de automação: `git ls-remote origin` via `core.sshCommand` da worktree
9. commit assinado de teste em repo temporário
10. (Windows) conformidade de OneDrive/profile links quando `paths.windows.onedrive_enabled=true`

## Modos de assinatura Git

`checkEnv` entende três modos:

- `auto`: padrão. Se a worktree atual tiver `dotfiles.signing.mode=automation`,
  valida o signer técnico; caso contrário, valida o signer humano padrão.
- `human`: força a validação do signer humano.
- `automation`: força a validação do signer técnico da worktree atual.

Uso recomendado:

```powershell
task env:check SIGN_MODE=automation
task git:signing:status
```

Em modo `automation`, o `checkEnv` também valida:

- `dotfiles.signing.automationPublicKeyRef` na `config.worktree`, quando a
  worktree depende da ref pública do 1Password
- fallback local para a chave técnica quando a worktree já possui o par
  privado/público fora do versionamento
- correspondência entre a chave pública resolvida e a chave efetiva do signer
  técnico
- `core.sshCommand` da worktree quando a automação usa chave técnica local para GitHub

## Semântica de status

- `SUCCESS`: controle atendido.
- `FAIL`: controle obrigatório não atendido.
- `INCONCLUSIVE`: não foi possível afirmar com segurança.

No final, o comando imprime resumo e ações sugeridas.

## Retry automático

As implementações tentam reautenticar uma vez quando possível:

- `op` (via token já disponível no contexto)
- `gh` (via `GH_TOKEN`/`GITHUB_TOKEN` ou refs de 1Password na ordem: projeto, full-access, contingencia final)

## Comportamento no bootstrap

- Windows: [`app/bootstrap/bootstrap-windows.ps1`](../app/bootstrap/bootstrap-windows.ps1) roda `checkEnv` como gate final.
- Windows: em seguida roda validação dedicada de OneDrive/links (`Test-OneDriveLayoutHealth`).
- WSL: [`app/bootstrap/bootstrap-ubuntu-wsl.sh`](../app/bootstrap/bootstrap-ubuntu-wsl.sh) roda `checkEnv` como gate final.
- Qualquer `FAIL` interrompe o bootstrap.

## Falhas comuns e correções

- `GitHub CLI git protocol`:
  - `gh config set git_protocol ssh --host github.com`
- `1Password signer program`:
  - validar `gpg.ssh.program` e presença de `op-ssh-sign`
- `SSH auth to GitHub`:
  - validar chave no GitHub + 1Password SSH Agent ativo
  - em modo `automation`, validar também a chave técnica registrada no GitHub e o `core.sshCommand` da worktree
- `Signed commit test`:
  - revisar `user.signingkey`, signer e agent
  - em modo `automation`, confirmar que a worktree foi configurada via
    `task git:signing:mode:automation`, que a chave técnica local existe e que
    `gpg.ssh.program` foi sobrescrito para o signer técnico correto
- `OneDrive root path` / `OneDrive profile links`:
  - validar `paths.windows.*` na config local documentada em [`config-reference.md`](config-reference.md#bootstrapuser-configyaml)
  - rerodar bootstrap para recriar links e revisar root ativa do OneDrive
