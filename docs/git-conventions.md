# Git Conventions

Este repositorio adota convencoes obrigatorias para:

- commits
- titulos de PR
- nomes de branch

## Commits

Formato obrigatorio:

```text
<emoji> <type>(<scope opcional>): <descricao>
```

Exemplos validos:

```text
✨ feat(test-harness): scaffold pester foundation
🐛 fix(bootstrap): preserve canonical projects path
📝 docs(ci): define hybrid test strategy
♻️ refactor(bootstrap-config): extract path normalization
✅ test(powershell): cover path precedence
🔧 chore(github): add pr title validation
```

Regras:

- o emoji e obrigatorio
- o `type` segue conventional commits
- o `scope` e recomendado e deve ser curto
- a descricao deve ser objetiva e em lowercase
- nao usar ponto final

Tipos aceitos neste repo:

- `feat`
- `fix`
- `docs`
- `refactor`
- `test`
- `chore`
- `ci`
- `perf`
- `build`
- `revert`

## Pull Requests

O titulo do PR segue a mesma regra dos commits:

```text
<emoji> <type>(<scope opcional>): <descricao>
```

Exemplo:

```text
✨ feat(test-harness): add pester foundation for bootstrap config
```

## Branches

Branches NAO usam emoji.

Formato recomendado:

```text
<type>/<slug-curto>
```

Exemplos:

```text
feat/test-harness-hybrid
fix/windows-relink-regression
docs/bootstrap-config-reference
refactor/bootstrap-path-normalization
```

## Motivo

Essas convencoes tornam historico, changelog, revisao e automacao mais previsiveis.
