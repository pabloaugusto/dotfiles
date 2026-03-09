# Catalogo normativo dos reviewers especializados

Artefato canonico da base normativa que orienta cada reviewer especializado da
control plane. A fonte declarativa correspondente fica em
[`../../../config/ai/reviewer-standards.yaml`](../../../config/ai/reviewer-standards.yaml).

## Objetivo

- explicitar as normas, especificacoes, RFCs e referencias primarias usadas por
  cada reviewer
- separar tres camadas de governanca tecnica:
  - padrao de linguagem ou formato
  - guia de estilo ou convencao
  - enforcement automatizado
- evitar aprovacoes vagas, sem fundamento tecnico ou sem criterio audivel

## Regra operacional

- reviewer especializado deve citar, quando aplicavel, pelo menos uma fonte
  primaria do seu perfil ao justificar achado, risco, excecao ou aprovacao
- quando nao existir norma formal numerada, vale a documentacao primaria do
  fornecedor ou mantenedor oficial
- guias de estilo de mercado entram como camada secundaria; nao substituem a
  especificacao oficial

## Perfis ativos

### Python

Papel: `ai-reviewer-python`

Camada normativa:

- linguagem: [Python Language Reference](https://docs.python.org/3/reference/)
- estilo e higiene:
  - [PEP 8](https://peps.python.org/pep-0008/)
  - [PEP 20](https://peps.python.org/pep-0020/)
  - [PEP 257](https://peps.python.org/pep-0257/)
- contratos de tipagem:
  - [PEP 484](https://peps.python.org/pep-0484/)
- enforcement automatizado:
  - [Ruff](https://docs.astral.sh/ruff/)
  - [mypy](https://mypy.readthedocs.io/)

Escopo minimo de review:

- corretude sintatica e semantica
- tipagem e contratos publicos
- manutencao, legibilidade e acoplamento
- performance e I/O quando relevantes
- portabilidade Windows e WSL quando aplicavel

### PowerShell

Papel: `ai-reviewer-powershell`

Camada normativa:

- design de comandos:
  - [Approved Verbs for PowerShell Commands](https://learn.microsoft.com/powershell/scripting/developer/cmdlet/approved-verbs-for-windows-powershell-commands?view=powershell-7.5)
- linguagem e construcao de funcoes:
  - [about_Functions_Advanced](https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_functions_advanced?view=powershell-7.5)
  - [about_Language_Modes](https://learn.microsoft.com/powershell/module/microsoft.powershell.core/about/about_language_modes?view=powershell-7.5)
- enforcement automatizado:
  - [PSScriptAnalyzer rules](https://learn.microsoft.com/powershell/utility-modules/psscriptanalyzer/rules/readme?view=ps-modules)

Escopo minimo de review:

- compatibilidade entre `Windows PowerShell` e `pwsh` quando aplicavel
- idempotencia, quoting e seguranca operacional
- approved verbs, ergonomia e semantica de funcoes
- integracao com host Windows e WSL

### Automacao

Papel: `ai-reviewer-automation`

Camada normativa:

- shell:
  - [POSIX Shell Command Language](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html)
- containers:
  - [Dockerfile reference](https://docs.docker.com/reference/dockerfile/)
- CI/CD:
  - [Workflow syntax for GitHub Actions](https://docs.github.com/actions/using-workflows/workflow-syntax-for-github-actions)
- enforcement automatizado:
  - [ShellCheck](https://www.shellcheck.net/)
  - [actionlint](https://github.com/rhysd/actionlint)
  - [Hadolint](https://github.com/hadolint/hadolint)

Escopo minimo de review:

- determinismo de task, shell e workflow
- portabilidade e quoting defensivo
- seguranca de pipeline, secrets e artefatos
- rollback, retry e idempotencia operacional

### Config policy

Papel: `ai-reviewer-config-policy`

Camada normativa:

- formatos declarativos:
  - [YAML 1.2.2 Specification](https://yaml.org/spec/1.2.2/)
  - [RFC 8259 - JSON](https://www.rfc-editor.org/rfc/rfc8259)
  - [JSON Schema](https://json-schema.org/)
  - [JSON5 specification](https://spec.json5.org/)
  - [TOML v1.0.0](https://toml.io/en/v1.0.0)
  - [CommonMark Spec](https://spec.commonmark.org/)
- enforcement automatizado:
  - [yamllint](https://yamllint.readthedocs.io/)
  - [Spectral](https://docs.stoplight.io/docs/spectral/674b27b261c3c-overview)
  - [markdownlint](https://github.com/DavidAnson/markdownlint)

Escopo minimo de review:

- aderencia ao formato e ao schema
- compatibilidade contratual e semantica
- legibilidade humana dos artefatos versionados
- linkagem e rastreabilidade documental

## Perfil futuro recomendado

### JavaScript

Papel futuro sugerido: `ai-reviewer-javascript`

Base normativa recomendada:

- [ECMA-262](https://ecma-international.org/publications-and-standards/standards/ecma-262/)
- [ECMA-402](https://ecma-international.org/publications-and-standards/standards/ecma-402/)
- [HTML Living Standard](https://html.spec.whatwg.org/)
- [TC39 Process](https://tc39.es/process-document/)

Camada secundaria de estilo:

- [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- [Google JavaScript Style Guide](https://google.github.io/styleguide/jsguide.html)

Enforcement automatizado recomendado:

- [ESLint](https://eslint.org/docs/latest/)
- [Prettier](https://prettier.io/docs/)

## Relacionados

- [`agent-operations.md`](agent-operations.md)
- [`../2026-03-07-operacao-agentes-jira-confluence.md`](../2026-03-07-operacao-agentes-jira-confluence.md)
- [`../2026-03-07-parecer-e-plano-inicial.md`](../2026-03-07-parecer-e-plano-inicial.md)
