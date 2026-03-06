---
name: dotfiles-test-harness
description: Projetar, implementar e validar testes, harnesses e CI/CD deste repo de dotfiles. Use quando a tarefa tocar `tests/`, `.github/workflows/`, `Dockerfile`, `Taskfile.yml`, Pester, Bats, containers Linux, runners Windows ou estrategia de qualidade.
---

# Dotfiles Test Harness

## Objetivo

Guiar a evolucao de testes e automacoes com foco em isolamento, custo baixo, evidencias reais de funcionamento e crescimento incremental.

## Fluxo

1. Ler `docs/test-strategy.md`.
2. Ler `references/matriz.md` desta skill.
3. Classificar a tarefa em unit, integration, protected E2E ou local lab.
4. Preferir contexto injetavel, fixture e isolamento do host.
5. Reusar scripts, tasks e workflows antes de criar duplicacao.
6. Validar localmente o que estiver disponivel e registrar o que ficou fora do escopo.

## Regras

- Pester para PowerShell e Bats para Bash.
- Linux integration e container-first.
- Windows integration em runner real; E2E real fica fora de PR barato.
- PR CI nao deve depender de auth real, OneDrive real nem estado pessoal do operador.
- Testar estado final, nao so `exit code`.

## Validacao minima

- `task test:unit:powershell`
- `task ci:lint:windows`
- `task ci:lint:linux`
- harness ou workflow tocado pela mudanca

## Referencias

- `references/matriz.md`
