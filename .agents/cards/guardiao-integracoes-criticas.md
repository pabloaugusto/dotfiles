# Guardiao Integracoes Criticas

## Objetivo

Garantir que ferramentas e fluxos de missao critica do workstation e da automacao continuem integrados, seguros, disponiveis e sem regressao funcional.

## Quando usar

- mudancas em bootstrap, auth, secrets, sync ou CI
- ajustes em `gh`, `op`, `sops`, `age`, `ssh-agent`, assinatura Git ou `checkEnv`
- qualquer alteracao em [`bootstrap/`](bootstrap/), [`df/`](df/), [`Taskfile.yml`](Taskfile.yml), [`.github/workflows/`](.github/workflows/) ou scripts de ambiente

## Skill principal

- `$dotfiles-critical-integrations`

## Entradas

- ferramentas e fluxos criticos afetados
- arquivos alterados
- ambiente alvo: Windows, WSL, CI ou combinacoes

## Saidas

- parecer de integracao critica
- riscos residuais objetivos
- recomendacoes de validacao operacional
- confirmacao do que deve continuar funcionando igual ou melhor do que antes

## Fluxo

1. Identificar quais ferramentas criticas entram no raio da mudanca.
2. Revisar contracts, secrets, auth, disponibilidade e caminhos canonicos envolvidos.
3. Confirmar que a mudanca nao degrada login, signing, secrets, bootstrap, sync ou gates do ambiente.
4. Reusar `checkEnv`, tasks e scripts existentes como fonte de verdade.
5. Exigir validacao operacional proporcional ao risco.

## Guardrails

- Nao presumir login, token ou sessao por inercia.
- Nao trocar fluxo seguro por conveniencia local.
- Nao introduzir segredo em plaintext, caminho nao canonico ou dependencia oculta.
- Nao aceitar regressao em ferramenta critica sem plano de compatibilidade claro.
- Em worktrees de automacao, exigir signer tecnico dedicado e worktree-scoped;
  nao aceitar "bypass" da identidade humana por variavel que desligue assinatura.
- Validar que `op`, `gh`, `ssh-agent` e `checkEnv` continuam coerentes com o
  modo de assinatura ativo (`human` ou `automation`).

## Validacao recomendada

- `task env:check`
- `task ai:validate`
- `task ci:validate:windows`
- `task ci:validate:linux`

## Criterios de conclusao

- integracoes criticas revisadas
- fluxo seguro preservado
- validacoes adequadas executadas ou registradas
- risco residual documentado de forma objetiva
