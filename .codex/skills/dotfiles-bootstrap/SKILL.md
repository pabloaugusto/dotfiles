---
name: dotfiles-bootstrap
description: Diagnosticar, ajustar e validar bootstrap, user-config, links canonicos, refresh/relink e derivados deste repo de dotfiles. Use quando a tarefa tocar `bootstrap/`, `Taskfile.yml`, `bootstrap/user-config.yaml(.tpl)`, symlinks, junctions, canonicalizacao de paths ou paridade Windows/WSL.
---

# Dotfiles Bootstrap

## Objetivo

Guiar mudancas no bootstrap sem perder previsibilidade, idempotencia e paridade entre Windows host e Ubuntu WSL.

## Fluxo

1. Ler `CONTEXT.md`, `docs/bootstrap-flow.md` e `docs/config-reference.md`.
2. Ler `references/checklist.md` desta skill quando a tarefa tocar layout, config ou links.
3. Identificar se a mudanca afeta Windows, WSL ou ambos.
4. Preservar caminhos absolutos canonicos como fonte de verdade.
5. Quando mudar contrato de config, manter em paridade:
   - `bootstrap/user-config.yaml.tpl`
   - `bootstrap/bootstrap-config.ps1`
   - documentacao relevante
6. Validar com tasks, lints e testes aderentes ao escopo.

## Regras

- Tratar `_path` como destino absoluto explicito.
- Aceitar `_dir` por compatibilidade, mas preferir absoluto e canonico.
- Nao usar symlink ou alias como fonte primaria de configuracao.
- Manter `refresh` e `relink` idempotentes.
- Evitar acoplar bootstrap ao `HOME` real quando for possivel injetar contexto.

## Validacao minima

- `task ci:lint:windows` quando houver mudanca em `.ps1`
- `task ci:lint:linux` quando houver mudanca em `.sh`
- `task test:unit:powershell` quando tocar parser e resolucao de config
- tasks de bootstrap afetadas pelo escopo

## Referencias

- `references/checklist.md`
