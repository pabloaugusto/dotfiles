<!--
Obrigatorio: use Conventional Commits + emoji semantico.

✅ PR title:
  ✨ feat(scope): descricao
  🐛 fix(scope): descricao

✅ Nome da branch:
  <type>/<slug>

Dica: commits locais podem receber emoji automaticamente via hook.
-->

## Summary

- explain the change briefly
- explain the main risk
- explain how it was validated

## Validation Checklist

- [ ] PR title segue `<emoji> <type>(scope?): descricao`
- [ ] PR title tem no maximo 72 caracteres
- [ ] branch segue `<type>/<slug>`
- [ ] commits seguem Conventional Commits com emoji semantico
- [ ] escopo da branch esta coeso
- [ ] `docs/AI-WIP-TRACKER.md` nao deixou item aberto em `Doing`
- [ ] local lint executed
- [ ] local tests executed
- [ ] docs updated when needed
- [ ] risks and follow-ups noted
