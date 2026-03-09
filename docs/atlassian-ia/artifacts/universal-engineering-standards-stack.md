# Universal Engineering Standards Stack (2026)

Mapa consolidado de standards, style guides, linters, formatters, ferramentas
de seguranca e referencias de governanca usados para orientar a engenharia
moderna desta control plane.

Este artefato complementa o catalogo especifico dos reviewers em
[`reviewer-standards-catalog.md`](reviewer-standards-catalog.md) e amplia a
visao para a governanca tecnica como um todo.

## Objetivo

- padronizar como cada especialidade escolhe suas referencias tecnicas
- separar especificacao formal de convencao e de enforcement automatizado
- reduzir reviews subjetivos e ad hoc
- fornecer uma base reutilizavel para futuros agentes e projetos

## Regra canonica

Toda especialidade deve buscar tres camadas de governanca:

1. `specification`: a linguagem, formato ou protocolo oficial
2. `conventions`: estilo, padroes de mercado e boas praticas
3. `automated enforcement`: lint, formatter, scanner, schema ou CI

Em resumo:

```text
specification -> conventions -> automated enforcement
```

## 1. Especificacoes formais de linguagem e formato

| Tecnologia | Especificacao principal | Tipo | Link |
| --- | --- | --- | --- |
| JavaScript | ECMA-262 | linguagem | [ECMA-262](https://ecma-international.org/publications-and-standards/standards/ecma-262/) |
| JavaScript i18n | ECMA-402 | linguagem | [ECMA-402](https://ecma-international.org/publications-and-standards/standards/ecma-402/) |
| Browser APIs | HTML Living Standard | plataforma | [WHATWG HTML](https://html.spec.whatwg.org/) |
| JSON | RFC 8259 | RFC | [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259) |
| YAML | YAML 1.2.2 | formato | [YAML 1.2.2](https://yaml.org/spec/1.2.2/) |
| TOML | TOML v1.0.0 | formato | [TOML](https://toml.io/en/v1.0.0) |
| Markdown | CommonMark Spec | formato | [CommonMark](https://spec.commonmark.org/) |
| Shell | POSIX Shell Command Language | linguagem | [POSIX Shell](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html) |
| Docker images | OCI Image Specification | container | [OCI Image Spec](https://github.com/opencontainers/image-spec) |
| Docker runtime | OCI Runtime Specification | container | [OCI Runtime Spec](https://github.com/opencontainers/runtime-spec) |
| JSON validation | JSON Schema | schema | [JSON Schema](https://json-schema.org/) |
| Python | Python Language Reference | linguagem | [Python Reference](https://docs.python.org/3/reference/) |
| JSON5 | JSON5 specification | formato | [JSON5](https://spec.json5.org/) |

## 2. Guias de estilo e convencoes

### JavaScript

- [Airbnb JavaScript Style Guide](https://github.com/airbnb/javascript)
- [Google JavaScript Style Guide](https://google.github.io/styleguide/jsguide.html)
- [StandardJS](https://standardjs.com/)
- [TC39 Process](https://tc39.es/process-document/)

### Python

- [PEP 8](https://peps.python.org/pep-0008/)
- [PEP 257](https://peps.python.org/pep-0257/)
- [PEP 484](https://peps.python.org/pep-0484/)
- [PEP 20](https://peps.python.org/pep-0020/)

### PowerShell

- [PowerShell Style Guide](https://learn.microsoft.com/powershell/scripting/community/contributing/powershell-style-guide)
- [Script authoring considerations](https://learn.microsoft.com/powershell/scripting/dev-cross-plat/performance/script-authoring-considerations)
- [Approved Verbs](https://learn.microsoft.com/powershell/scripting/developer/cmdlet/approved-verbs-for-windows-powershell-commands?view=powershell-7.5)

### Shell

- [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html)

### Markdown

- [Markdown Guide - basic syntax](https://www.markdownguide.org/basic-syntax/)
- [CommonMark Spec](https://spec.commonmark.org/)

### Docker

- [Dockerfile best practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

## 3. Linters e analise estatica

| Tecnologia | Ferramenta | Papel | Link |
| --- | --- | --- | --- |
| JavaScript | ESLint | lint | [ESLint](https://eslint.org/docs/latest/) |
| Python | Ruff | lint + fix | [Ruff](https://docs.astral.sh/ruff/) |
| Python | mypy | tipagem | [mypy](https://mypy.readthedocs.io/) |
| Shell | ShellCheck | lint | [ShellCheck](https://www.shellcheck.net/) |
| YAML | yamllint | lint | [yamllint](https://yamllint.readthedocs.io/) |
| Dockerfile | Hadolint | lint | [Hadolint](https://github.com/hadolint/hadolint) |
| Markdown | markdownlint | lint | [markdownlint](https://github.com/DavidAnson/markdownlint) |
| GitHub Actions | actionlint | lint | [actionlint](https://github.com/rhysd/actionlint) |
| PowerShell | PSScriptAnalyzer | lint | [PSScriptAnalyzer](https://learn.microsoft.com/powershell/utility-modules/psscriptanalyzer/rules/readme?view=ps-modules) |
| JSON / schemas | Spectral | lint de schema | [Spectral](https://docs.stoplight.io/docs/spectral/674b27b261c3c-overview) |

## 4. Formatters

| Tecnologia | Ferramenta | Link |
| --- | --- | --- |
| JS / JSON / YAML | Prettier | [Prettier](https://prettier.io/docs/) |
| Python | Black | [Black](https://black.readthedocs.io/) |
| Shell | shfmt | [shfmt](https://github.com/mvdan/sh) |
| Markdown | mdformat | [mdformat](https://github.com/executablebooks/mdformat) |

## 5. Seguranca e scanning

| Tipo | Ferramenta | Link |
| --- | --- | --- |
| dependency scanning | Dependabot | [Dependabot](https://docs.github.com/code-security/dependabot) |
| secrets detection | Gitleaks | [Gitleaks](https://github.com/gitleaks/gitleaks) |
| static security analysis | Semgrep | [Semgrep](https://semgrep.dev/) |
| container scanning | Trivy | [Trivy](https://trivy.dev/) |
| infrastructure scanning | Checkov | [Checkov](https://www.checkov.io/) |
| code scanning | CodeQL | [CodeQL](https://codeql.github.com/) |

## 6. Git e workflow

### Commits

- [Conventional Commits](https://www.conventionalcommits.org/)

### Versionamento

- [Semantic Versioning](https://semver.org/)

### Estrategias de branching

- [GitFlow](https://nvie.com/posts/a-successful-git-branching-model/)
- [GitHub Flow](https://docs.github.com/get-started/quickstart/github-flow)
- [Trunk Based Development](https://trunkbaseddevelopment.com/)

## 7. CI/CD

- [GitHub Actions](https://docs.github.com/actions)
- [GitLab CI](https://docs.gitlab.com/ee/ci/)
- [Jenkins](https://www.jenkins.io/doc/)
- [CircleCI](https://circleci.com/docs/)
- [actionlint](https://github.com/rhysd/actionlint)

## 8. Containers

- [OCI Image Specification](https://github.com/opencontainers/image-spec)
- [OCI Runtime Specification](https://github.com/opencontainers/runtime-spec)
- [Hadolint](https://github.com/hadolint/hadolint)
- [Trivy](https://trivy.dev/)
- [Dockle](https://github.com/goodwithtech/dockle)

## 9. Modelo global de qualidade

- [ISO/IEC 25010](https://iso25000.com/index.php/en/iso-25000-standards/iso-25010)
- [SonarQube](https://www.sonarsource.com/products/sonarqube/)

Atributos recorrentes do modelo:

- maintainability
- reliability
- performance efficiency
- security
- compatibility
- usability
- portability

## 10. Camada AI / agentes

### Protocolos e contratos

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [OpenAI function calling](https://platform.openai.com/docs/guides/function-calling)
- [JSON Schema](https://json-schema.org/)

### Frameworks e ecossistema

- [LangChain](https://www.langchain.com/)
- [CrewAI](https://github.com/crewAIInc/crewAI)
- [AutoGPT](https://github.com/Significant-Gravitas/AutoGPT)

## 11. Exemplo de stack aplicada

### Standards

- ECMAScript
- Python Language Reference
- POSIX Shell
- YAML
- JSON RFC
- OCI

### Style

- PEP 8
- Airbnb JS
- Google Shell

### Lint

- ESLint
- Ruff
- ShellCheck
- yamllint
- Hadolint
- markdownlint

### Formatting

- Prettier
- Black
- shfmt

### Security

- Gitleaks
- Trivy
- Semgrep

### CI/CD

- GitHub Actions
- actionlint

### Governance

- Conventional Commits
- Semantic Versioning

## 12. Estrutura recomendada para um repositorio de standards

```text
engineering-standards/
  languages/
    javascript.md
    python.md
    shell.md
    powershell.md
  formats/
    yaml.md
    json.md
    json5.md
    toml.md
    markdown.md
  containers/
    dockerfile.md
  git/
    commits.md
    branching.md
    versioning.md
  ci/
    pipelines.md
    workflows.md
  security/
    secrets.md
    scanning.md
  ai/
    agents.md
    prompts.md
    tools.md
```

## 13. Matriz simplificada arquivo -> padrao -> enforcement

| Arquivo | Standard | Linter | Formatter |
| --- | --- | --- | --- |
| `.js` | ECMA-262 | ESLint | Prettier |
| `.py` | Python Language Reference + PEPs | Ruff | Black |
| `.sh` | POSIX Shell | ShellCheck | shfmt |
| `.ps1` | PowerShell docs + Approved Verbs | PSScriptAnalyzer | formatter PowerShell |
| `.yaml` / `.yml` | YAML 1.2.2 | yamllint | Prettier |
| `.json` | RFC 8259 | Spectral / jsonlint | Prettier |
| `Dockerfile` | OCI + Dockerfile reference | Hadolint | n/a |
| `.md` | CommonMark | markdownlint | mdformat / Prettier |
| workflows | GitHub Actions syntax | actionlint | Prettier |

## 14. Como este projeto usa esse stack

- o artefato [`reviewer-standards-catalog.md`](reviewer-standards-catalog.md)
  deriva deste stack para os reviewers especializados ativos
- futuros agentes devem nascer com:
  - escopo
  - fontes primarias
  - convencoes secundarias
  - tooling de enforcement
- quando houver norma numerada oficial, ela deve vir antes de qualquer style
  guide de mercado
- quando nao houver norma formal unica, usamos documentacao primaria do
  mantenedor mais tooling automatizado e convencoes auditaveis

## 15. Recomendacao operacional

Para cada nova especialidade:

1. mapear a especificacao oficial
2. mapear o style guide ou convencao relevante
3. mapear o enforcement automatizado
4. registrar isso em artefato versionado
5. refletir o artefato em pagina oficial do Confluence
6. obrigar o reviewer a citar a base normativa quando o achado depender dela

## Relacionados

- [`reviewer-standards-catalog.md`](reviewer-standards-catalog.md)
- [`agent-operations.md`](agent-operations.md)
- [`../2026-03-07-operacao-agentes-jira-confluence.md`](../2026-03-07-operacao-agentes-jira-confluence.md)
- [`../2026-03-07-melhores-praticas-mercado.md`](../2026-03-07-melhores-praticas-mercado.md)
