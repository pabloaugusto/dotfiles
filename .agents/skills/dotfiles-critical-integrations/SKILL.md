---
name: dotfiles-critical-integrations
description: Revisar integracoes criticas do workstation e da automacao, como gh, op, sops, age, ssh-agent, assinatura Git, checkEnv, bootstrap, sync e CI. Use quando a tarefa tocar auth, secrets, bootstrap, CLI, ambiente, workflows ou qualquer fluxo que possa degradar a operacao real do repo.
---

# dotfiles-critical-integrations

## Objetivo

Atuar como guardiao das integracoes de missao critica do repo.

## Fluxo

1. Ler `AGENTS.md`, `LICOES-APRENDIDAS.md`, `CONTEXT.md` e `docs/AI-DELEGATION-FLOW.md`.
2. Identificar quais ferramentas ou fluxos criticos entram no raio da mudanca.
3. Confirmar contratos de paths canonicos, secrets, auth, signing e tasks de validacao.
4. Proteger fluxos seguros ja existentes e evitar degradacao silenciosa.
5. Exigir validacao proporcional ao risco com `checkEnv`, bootstrap ou CI quando cabivel.

## Regras

- Nunca assumir sessao, login ou token valido sem evidencias.
- Preservar paths canonicos, secrets cifrados e fluxos de signing como fonte de verdade.
- Em mudancas sensiveis, preferir tasks canonicas de ambiente e bootstrap a validacoes improvisadas.

## Entregas esperadas

- parecer de impacto nas integracoes criticas
- riscos residuais objetivos
- validacoes operacionais recomendadas

## Validacao

- `task env:check`
- `task ai:validate`
- `task ai:eval:smoke`
- `task ci:validate:windows`

## Referencias

- `references/checklist.md`
