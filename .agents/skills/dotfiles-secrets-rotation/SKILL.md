---
name: dotfiles-secrets-rotation
description: Planejar, executar e validar rotacao segura de secrets, chaves SSH, tokens, service accounts e artefatos sops+age, usando os operadores criticos do repo e respeitando as limitacoes reais dos provedores.
---

# dotfiles-secrets-rotation

## Objetivo

Executar rotacoes criticas sem quebrar bootstrap, signing, auth ou acesso aos
repos e secrets do ambiente.

## Fluxo

1. Ler [`AGENTS.md`](AGENTS.md), [`LICOES-APRENDIDAS.md`](LICOES-APRENDIDAS.md),
   [`docs/secrets-and-auth.md`](docs/secrets-and-auth.md) e
   [`docs/checkenv.md`](docs/checkenv.md).
2. Inventariar as refs canonicas em [`df/secrets/secrets-ref.yaml`](df/secrets/secrets-ref.yaml),
   os templates em [`bootstrap/secrets/.env.local.tpl`](bootstrap/secrets/.env.local.tpl)
   e a politica `sops+age` em [`df/secrets/dotfiles.sops.yaml`](df/secrets/dotfiles.sops.yaml).
3. Classificar cada alvo como `fully_automated`, `assisted` ou `manual_blocked`
   com base em suporte oficial do provedor.
4. Montar um plano ordenado que preserve a credencial antiga ate a nova estar
   validada e persistida com seguranca.
5. Usar os operadores criticos do ambiente como fonte de verdade:
   `op`, `gh`, `glab`, `sops`, `age`, `ssh-agent` e `git`.
6. Atualizar refs derivadas, runtime cifrado, inventario e notificacao final.
7. Rodar validacao operacional pos-rotacao e registrar licoes/gaps.

## Regras

- Nunca executar revogacao destrutiva sem `preflight`, plano e validacao
  pos-criacao da substituta.
- Sempre preferir refs do 1Password e chave privada no SSH Agent; nao aceitar
  segredo persistente em plaintext.
- Sempre explicitar limites de provedor; no GitHub, nao prometer rotacao total
  de PAT quando a plataforma nao suportar a operacao.
- Toda task individual deve reutilizar o mesmo core declarativo e o mesmo motor
  de validacao.
- Toda rotacao completa deve terminar com resumo notificavel ao usuario.

## Entregas esperadas

- inventario de alvos rotacionaveis e dependencias
- plano de execucao ordenado e auditavel
- rotacao parcial ou total via tasks canonicas
- resumo final com itens rotacionados, pendencias manuais e validacao executada

## Validacao

- `task secrets:rotation:preflight`
- `task secrets:rotation:plan`
- `task secrets:rotation:validate`
- `task env:check`
- `task ai:validate`

## Referencias

- [`references/checklist.md`](references/checklist.md)
- [`references/provider-limits.md`](references/provider-limits.md)
