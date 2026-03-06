## Sugestões de melhorias e próximos passos

Este documento consolida pontos de melhoria, riscos e ideias de evolução para o ambiente de dotfiles, agrupados por **criticidade** e sempre indicando o **tema** relacionado.

---

### 1. Crítico

- **Tema: CI / Qualidade automatizada**
  - **Problema**: Workflows de CI estão desabilitados via sufixo `.ignore` (ex.: `.github/workflows/check-scripts.yml.ignore`, `.github/workflows/linter.yaml.ignore`).
  - **Risco**: Regressões em scripts, quebra de bootstrap, problemas de segurança ou drift de estilo entram sem nenhum gate automatizado.
  - **Sugestão**:
    - Reativar um **CI mínimo** com:
      - Parse/lint de PowerShell (`pwsh` + `System.Management.Automation.Language.Parser`).
      - Parse/lint de Bash (`bash -n` para todos `*.sh`).
      - `docker build` equivalente ao `Taskfile` (paridade com `ci:docker-build`).
      - Opcionalmente, verificação simples de links/docs.
    - Garantir que `task ci:*` e `task pr:*` sejam espelhos do que roda no CI.

- **Tema: Git global / Segurança**
  - **Problema**: A config Git base coloca `safe.directory = *` em `df/git/.gitconfig`.
  - **Risco**: Isso desliga a proteção de ownership suspeito do Git para qualquer diretório.
  - **Sugestão**:
    - Restringir `safe.directory` a poucos caminhos bem definidos, por exemplo:
      - `~/dotfiles`, `/home/*/dotfiles`
      - `C:/Users/*/dotfiles`
    - Documentar explicitamente essa política em `SECURITY.md` / `docs/secrets-and-auth.md`.

- **Tema: Arquivos temporários / Legado**
  - **Problema**: Arquivo `.bw.tmp` está versionado no repositório.
  - **Risco**: Ruído de manutenção, possível divergência de lógica se for um “snapshot” obsoleto, e confusão sobre qual é a fonte canônica.
  - **Sugestão**:
    - Remover `.bw.tmp` do versionamento (e adicionar ao `.gitignore`) **ou** movê‑lo para uma pasta `archive/` claramente marcada como legado.

---

### 2. Alto

- **Tema: Robustez do bootstrap Windows**
  - **Problema**: Em versões anteriores havia controle de fluxo frágil (uso de `break` fora de loop, dependência de `sudo` num contexto já elevado etc.); parte disso já foi melhorada, mas o fluxo ainda é longo e complexo.
  - **Risco**: Erros de bootstrap podem se manifestar tardiamente, em pontos difíceis de depurar.
  - **Sugestão**:
    - Manter o padrão atual de **lançar exceções explícitas** (`throw`) com mensagens acionáveis para cada gate.
    - Para cada bloco crítico (OneDrive, symlinks, secrets, auth, `checkEnv`), garantir:
      - Uma mensagem de erro única e rastreável.
      - Um link ou referência a uma seção de troubleshooting em `docs/bootstrap-flow.md` ou `bootstrap/README.md`.

- **Tema: OneDrive como pré‑requisito rígido**
  - **Problema**: O fluxo atual assume fortemente OneDrive em muitos cenários; embora configurável via YAML, a UX ainda incentiva o caminho “OneDrive obrigatório”.
  - **Risco**: Hosts válidos sem OneDrive, ou com políticas corporativas diferentes, podem se tornar mais difíceis de suportar.
  - **Sugestão**:
    - Deixar mais claro na documentação:
      - “Modo com OneDrive” vs “Modo local” (sem OneDrive) e impactos em Windows/WSL.
    - Criar uma pequena tabela em `docs/onedrive.md` com:
      - Cenário, campos críticos no YAML, comportamento esperado.

- **Tema: Catálogo de software monolítico**
  - **Problema**: `bootstrap/software-list.ps1` concentra uma lista extensa e relativamente homogênea de pacotes.
  - **Risco**: Bootstrap mais lento, maior chance de falha por pacote específico, dificuldade de reaproveitar o bootstrap em hosts com perfis diferentes (máquina leve vs máquina full).
  - **Sugestão**:
    - Quebrar o catálogo em **perfis**:
      - `core` (mínimo para rodar dotfiles/CI).
      - `dev` (ferramentas de desenvolvimento).
      - `workstation-full` (apps de produtividade, etc.).
    - No bootstrap, permitir escolher o perfil (ou ler do YAML).

- **Tema: Plug‑ins/op wrappers no Bash**
  - **Problema**: Alguns wrappers/plugins (como integração `op`) podem alterar o comportamento de comandos como `gh` e `ssh` em shells interativos.
  - **Risco**: Scripts (incluindo `checkEnv` e automações) podem se comportar diferente quando rodados num shell com plugins carregados vs num ambiente “limpo”.
  - **Sugestão**:
    - Isolar o uso de wrappers/plugins para sessões interativas:
      - Proteger com variável de feature flag, por ex. `DOTFILES_ENABLE_OP_PLUGINS=1`.
      - Em scripts, sempre usar `command gh`, `command ssh` quando interferência de alias for indesejada.

---

### 3. Médio

- **Tema: Config Git (push e aliases)**
  - **Problema**:
    - Há aliases Git espalhados em mais de um arquivo (`.gitconfig` e `.gitconfig-base`).
    - Config antiga com `push.default=matching` ainda existe em alguma camada.
  - **Risco**:
    - Manutenção duplicada, comportamento difícil de prever dependendo da combinação de includes.
    - Risco de `git push` enviar múltiplas branches indesejadas.
  - **Sugestão**:
    - Consolidar aliases em um arquivo base único (ex.: `.gitconfig-base`).
    - Garantir que a config efetiva use `push.default=simple`.
    - Documentar a hierarquia de includes Git em `docs/config-reference.md`.

- **Tema: Funções de instalação apt/brew**
  - **Problema**: A detecção atual de “pacote já instalado” se baseia em presença de comando, o que pode gerar falsos positivos/negativos.
  - **Risco**: Pacotes apt não instalados podem ser considerados presentes, ou upgrades podem não acontecer.
  - **Sugestão**:
    - Para apt:
      - Usar `dpkg -s <pkg>` ou `apt-cache policy <pkg>` para decidir install/upgrade.
    - Para brew:
      - Usar `brew list --versions` ou `brew info --json` quando necessário.

- **Tema: Arquivos de backup/legado versionados**
  - **Problema**: Arquivos como `bootstrap/bootstrap-ubuntu.original.sh`, `df/oh-my-posh/pablo.omp.json.bak` permanecem versionados.
  - **Risco**: Ambiguidade sobre qual é a fonte “verdadeira”, dificuldade para ferramentas de IA entenderem o fluxo canônico.
  - **Sugestão**:
    - Mover esses artefatos para uma pasta `archive/` com README explicando o contexto **ou** removê‑los se não forem mais necessários.

- **Tema: Performance de shell vs decrypt frequente**
  - **Problema**: Historicamente, `.bashrc` / `.profile` já chegaram a fazer decrypt de `.env.local.sops` com mais frequência do que o ideal.
  - **Risco**: Start de shell mais lento e maior superfície para erros temporários de decrypt.
  - **Sugestão**:
    - Manter o padrão atual de:
      - **Persistir** apenas `SOPS_AGE_KEY` em `runtime.env`.
      - Decriptar `.env.local.sops` sob demanda (bootstrap, comandos específicos) em vez de toda abertura de shell.
    - Caso queira variáveis sempre carregadas:
      - Criar um helper explícito (`load-dotfiles-env`) e chamar manualmente nas sessões que precisam.

---

### 4. Baixo

- **Tema: UX de mensagens / Idioma**
  - **Problema**: Há mensagens mistas (inglês/PT‑BR) e alguns typos (`supportted`, `comming`, etc.).
  - **Risco**: Não afeta funcionalidade, mas reduz clareza e polish da experiência.
  - **Sugestão**:
    - Padronizar mensagens para **PT‑BR técnico** ou **inglês**, conforme preferência.
    - Aproveitar um sweep rápido (ou ferramenta de lint de texto) para limpar typos nos principais scripts e docs.

- **Tema: Documentação cross‑referenciada**
  - **Problema**: Alguns docs em `docs/` ainda dependem bastante de contexto externo.
  - **Risco**: Onboarding mais lento ou necessidade de ler muito código para “ligar os pontos”.
  - **Sugestão**:
    - Em cada doc de referência, adicionar uma pequena seção “Como aplicar aqui” com:
      - Comandos `task` relacionados.
      - Arquivos/funções principais no repo.

---

### 5. Ideias de novas automações e fluxos

- **Tema: Auditar/reparar estrutura pós‑bootstrap**
  - **Ideia**: Criar um comando `task env:repair` que:
    - Reusa parte da lógica de `Test-OneDriveLayoutHealth` e `user-home-estructure.md`.
    - Tenta corrigir automaticamente:
      - Symlinks quebrados em Windows/WSL.
      - Pastas `.dotfiles-prelink-*` residuais sem conteúdo ou já migradas.

- **Tema: Segurança / Secret scanning**
  - **Ideia**:
    - Adicionar um `task security:scan` que:
      - Rode `gitleaks` ou `detect-secrets`.
      - Execute o checklist de `SECURITY.md` automaticamente.
    - Integrar esse task ao CI (e opcionalmente a um hook local).

- **Tema: Onboarding guiado**
  - **Ideia**:
    - Criar um `task bootstrap:guide` (ou script dedicado) que:
      - Leia `bootstrap/user-config.yaml`.
      - Valide campos críticos.
      - Abra docs relevantes (`docs/bootstrap-flow.md`, `docs/onedrive.md`, `docs/user-home-estructure.md`) com um resumo.

- **Tema: IA / Regras e skills**
  - **Ideia**:
    - Formalizar em arquivos dedicados (por exemplo `docs/ia-agents.md` / `.cursor/rules`) os comportamentos esperados para agentes de IA que trabalham neste repo:
      - Como usar `Taskfile.yml`.
      - Regras de segurança (nunca tocar em `bootstrap/user-config.yaml`, etc.).
      - Como interpretar `docs/repo-audit.md` e `ambiente-overview.md`.

## Conclusão prática

 - Bootstrap WSL hoje está consistente em termos de fluxo, com um problema real que eu já corrigi:
    - Re‑execuções não quebram mais por causa do instalador do oh‑my‑zsh.

- Os dois pontos que ainda podem causar erro na sua máquina não são bugs, mas gates intencionais:
    - sudo pedindo senha (você resolve simplesmente rodando em um terminal interativo).

  - ensureGitHubAuth falhando quando não há token / session válidos (op + 1Password SA + refs de GitHub).

Se quiser, no próximo passo eu posso:

- Rodar apenas a parte de checkEnv (task env:check ou checkEnv direto) e te devolver um diagnóstico pontual do teu ambiente WSL, ou

- Endurecer ainda mais o bootstrap (por exemplo, adicionando um dry-run / --no-software para validar só symlinks + secrets + checkEnv).