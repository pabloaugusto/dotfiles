# Docs Index

Mapa das documentacoes versionadas do projeto e ordem recomendada de leitura.

## Comece por aqui

1. `README.md`
2. `CONTEXT.md`
3. `bootstrap/README.md`
4. `docs/test-strategy.md`
5. `docs/ai-operating-model.md`
6. `SECURITY.md`

## Operacao do ambiente e bootstrap

- `docs/bootstrap-flow.md`: fluxograma detalhado do bootstrap Windows, WSL,
  OneDrive e gates.
- `docs/checkenv.md`: contrato e checklist do `checkEnv`.
- `docs/config-reference.md`: referencia comentada do YAML de bootstrap.
- `docs/onedrive.md`: layout, migracao e troubleshooting do OneDrive.
- `docs/secrets-and-auth.md`: modelo de segredos, auth e runtime cifrado.
- `docs/user-home-structure.md`: layout esperado do `HOME` apos bootstrap.
- `bootstrap/README.md`: guia operacional textual do bootstrap.

## Qualidade, testes e CI/CD

- `docs/test-strategy.md`: arquitetura de testes do repo.
- `docs/TASKS.md`: catalogo das tasks canonicas mais importantes.
- `docs/WORKFLOWS.md`: catalogo dos workflows ativos e suas tasks.
- `tests/README.md`: suites, harnesses e comandos de teste.
- `docs/repo-audit.md`: snapshot atual de riscos, achados resolvidos e backlog
  tecnico de manutencao.

## Governanca e IA

- `docs/ai-operating-model.md`: contrato da camada de IA.
- `docs/AI-WIP-TRACKER.md`: continuidade operacional do trabalho em curso.
- `docs/ROADMAP.md`: backlog priorizado e sugestoes.
- `docs/ROADMAP-DECISIONS.md`: historico das decisoes do roadmap.
- `docs/AI-AGENTS-CATALOG.md`: catalogo dos agentes do repo.
- `docs/AI-SKILLS-CATALOG.md`: catalogo das skills.
- `docs/AI-DELEGATION-FLOW.md`: fluxo de intake, roteamento e delegacao.
- `docs/AI-GOVERNANCE-AND-REGRESSION.md`: regressao e governanca da camada de IA.
- `docs/AI-SOURCE-AUDIT.md`: auditoria estrutural das fontes cross-repo.
- `docs/git-conventions.md`: convencoes de branch, commit e PR.

## Referencias e notas

- `docs/reference/powershell/`: referencias tecnicas auxiliares.
- `docs/notes/`: notas de uso pontual que nao sao contratos principais.

## Regra de manutencao

- README raiz = catalogo funcional do projeto.
- `docs/TASKS.md` e `docs/WORKFLOWS.md` devem refletir a automacao real.
- `bootstrap/README.md` e `tests/README.md` devem refletir os fluxos correntes,
  nao estados "iniciais".
