# Checklist

- `gh`, `op`, `sops`, `age`, `ssh-agent` ou assinatura Git foram impactados?
- Algum segredo pode vazar ou deixar de ser resolvido?
- O fluxo continua paritario entre Windows, WSL e CI?
- Existe task ou `checkEnv` que precisa ser atualizada?
- O patch usa caminhos canonicos e evita dependencias no host real?
