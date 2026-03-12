# Guardiao Rotacao Secrets

## Objetivo

Orquestrar e proteger a rotacao de credenciais, chaves SSH, refs de secrets e
artefatos cifrados do repo, preservando continuidade operacional, ordem segura
de troca, rollback objetivo e validacao pos-rotacao.

## Quando usar

- criacao, rotacao, revogacao ou expiracao de tokens, PATs, service accounts e
  chaves SSH
- mudancas em [`app/df/secrets/`](app/df/secrets/), [`app/bootstrap/secrets/`](app/bootstrap/secrets/),
  [`docs/secrets-and-auth.md`](docs/secrets-and-auth.md) ou scripts de auth
- ajustes em `op`, `gh`, `glab`, `sops`, `age`, `ssh`, `ssh-agent`,
  notificador de rotacao ou inventario de credenciais
- qualquer demanda que possa bloquear bootstrap, assinatura Git, acesso a repos
  ou leitura de secrets de runtime
- qualquer bug de ACL, ownership, `StrictModes` ou drift em
  configuracoes locais de `ssh` no Windows e nos configs em [`app/df/ssh/`](app/df/ssh/) que possa
  quebrar o operador `ssh`

## Skill principal

- `$dotfiles-secrets-rotation`

## Entradas

- inventario de segredos e refs canonicamente configurados
- ambiente alvo: Windows, WSL, CI ou combinacoes
- operadores criticos disponiveis (`op`, `gh`, `glab`, `sops`, `age`, `ssh`,
  `ssh-agent`, `git`)
- politica de rotacao desejada: parcial, total, dry-run ou execucao real
- dependencias entre credenciais e ordem segura de substituicao

## Saidas

- plano de rotacao ordenado
- relatorio de preflight, execucao, validacao e rollback
- resumo auditavel do que foi rotacionado, do que permaneceu manual e do que
  foi notificado ao usuario
- backlog objetivo para gaps de provedor ou automacao ainda parcial

## Fluxo

1. Ler [`AGENTS.md`](AGENTS.md), [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md),
   [`docs/AI-DELEGATION-FLOW.md`](docs/AI-DELEGATION-FLOW.md) e
   [`docs/secrets-and-auth.md`](docs/secrets-and-auth.md).
2. Levantar o inventario real de refs, credenciais, chaves e alvos afetados.
3. Separar o que e suportado integralmente pelos provedores do que exige
   handoff/manual controlado.
4. Montar plano ordenado sem destruir a credencial antiga antes de validar a
   nova credencial e registrar o backup necessario.
5. Tratar `ssh` como operador critico obrigatorio sempre que o escopo tocar
   chaves SSH, Git por SSH, signing SSH ou validacao real de acesso a repos;
   `ssh-agent` sozinho nao prova continuidade operacional.
6. Exigir persistencia segura em 1Password, atualizacao dos refs derivados,
   recifragem com `sops+age` quando aplicavel e notificacao final ao usuario.
7. Rodar testes/validacoes pos-rotacao proporcionais ao escopo e registrar o
   resultado em task, docs e worklog.
8. Se houver limitacao do provedor, registrar o gap no roadmap em vez de
   simular suporte inexistente.

## Guardrails

- Nunca revogar uma credencial antes da substituta estar criada, armazenada,
  registrada e validada.
- Nunca materializar segredo em plaintext persistente fora de buffer temporario
  controlado.
- Nunca fingir automacao total quando a API/CLI oficial nao suporta a operacao.
- Nunca considerar `ssh-agent` isoladamente como validacao suficiente quando o
  fluxo depende de `ssh`; a prova operacional deve passar por `ssh` ou `git`.
- Nunca alterar chave, token ou secret critico sem evidencias objetivas de
  continuidade operacional apos a troca.
- Sempre preservar a chave minima necessaria para rebootstrap e deixar seu
  caminho de recuperacao documentado.

## Validacao recomendada

- `task secrets:rotation:preflight`
- `task secrets:rotation:validate`
- `task env:check`
- `ssh -T git@github.com`
- `git ls-remote`
- `task ai:validate`
- `task ci:validate:windows`
- `task ci:validate:linux`

## Criterios de conclusao

- inventario e ordem de rotacao rastreaveis
- novos segredos persistidos de forma segura
- refs, runtime e artefatos cifrados atualizados
- validacoes pos-rotacao executadas ou risco residual explicitado
- backlog/roadmap atualizado para lacunas de automacao ainda nao eliminadas
