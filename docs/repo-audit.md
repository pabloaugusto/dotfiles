# Auditoria do Repositorio (2026-03-07)

Snapshot tecnico do estado atual do repositorio, com foco em:

- riscos abertos
- problemas ja resolvidos
- backlog tecnico que ainda faz sentido perseguir

## Escopo e metodo

- escopo: arquivos rastreados por Git
- leitura estatica de configuracoes, docs, bootstrap, shell, workflows e tests
- validacao contra o estado real atual da worktree `feat/test-harness-hybrid`

## Melhorias ja consolidadas

- CI ativo com workflows reais para IA, PR, qualidade e integracao do bootstrap
- camada canonica de IA consolidada em [`.agents/`](.agents/)
- paridade entre workflows, tasks e catalogos documentais
- stack Python formalizada com [`pyproject.toml`](pyproject.toml), `uv`, `ruff`, `ty`, `pytest`,
  `pymarkdownlnt`, `yamllint`, `actionlint` e `gitleaks`
- `.venv` segregada por plataforma para worktree compartilhada entre Windows e
  WSL
- aliases centralizados por ambiente:
  - [`df/.aliases`](df/.aliases)
  - [`df/powershell/aliases.ps1`](df/powershell/aliases.ps1)
  - [`df/git/.gitconfig-base`](df/git/.gitconfig-base)
- harnesses reais de integracao para `relink` em Linux e Windows
- historico, backups e snapshots deslocados para [`archive/`](archive/) quando nao sao
  fonte canonica

## Achados abertos

### Critico

1. **Politica Git global insegura (`safe.directory = *`)**
   - Evidencia: [`df/git/.gitconfig`](df/git/.gitconfig)
   - Impacto: desativa protecao de ownership suspeito para qualquer diretorio.
   - Recomendacao: restringir `safe.directory` a paths necessarios.
   - Esforco: **Baixo**

### Alto

1. **Menu do `_start.ps1` ainda expoe Linux/Mac sem dispatch real**
   - Evidencia: [`docs/bootstrap-flow.md`](docs/bootstrap-flow.md) e [`bootstrap/_start.ps1`](bootstrap/_start.ps1)
   - Impacto: UX ambigua e expectativa incorreta no entrypoint Windows.
   - Recomendacao: ocultar opcoes nao suportadas ou implementar dispatch real.
   - Esforco: **Baixo**

2. **Scripts legados de suporte ainda usam comandos quebrados**
   - Evidencia: [`bootstrap/scripts/post-win-install-script.ps1`](bootstrap/scripts/post-win-install-script.ps1)
   - Impacto: reutilizacao manual pode falhar silenciosamente.
   - Recomendacao: corrigir ou marcar explicitamente como legado.
   - Esforco: **Baixo**

3. **Catalogo de software Windows ainda tem ruido e fragilidade**
   - Evidencia: [`bootstrap/software-list.ps1`](bootstrap/software-list.ps1)
   - Exemplos:
     - duplicacao de instalacao de pacotes de auth
     - ID `Microsoft.OpenSSH.Preview ` com espaco final
   - Impacto: tempo extra, logs ruidosos e falha pontual de instalacao.
   - Recomendacao: modularizar catalogo e validar IDs automaticamente.
   - Esforco: **Medio**

### Medio

1. **Plugin do `op` no Bash pode alterar comandos esperados**
   - Evidencia: [`df/bash/.bashrc`](df/bash/.bashrc)
   - Impacto: wrappers podem interferir em `gh`, `ssh` e `checkEnv`.
   - Recomendacao: condicionar por flag ou normalizar chamadas com `command`.
   - Esforco: **Baixo**

2. **Instalacao apt ainda usa heuristica fragil**
   - Evidencia: [`df/bash/.inc/_functions.sh`](df/bash/.inc/_functions.sh)
   - Impacto: falso positivo ou falso negativo ao decidir install vs upgrade.
   - Recomendacao: usar `dpkg -s` ou `apt-cache policy`.
   - Esforco: **Medio**

3. **`checkEnv` Bash ainda usa temporarios previsiveis em partes do fluxo**
   - Evidencia: [`df/bash/.inc/check-env.sh`](df/bash/.inc/check-env.sh)
   - Impacto: risco de colisao em execucoes concorrentes.
   - Recomendacao: padronizar `mktemp` para todos os artefatos temporarios.
   - Esforco: **Baixo**

4. **Decrypt de `.env.local.sops` em toda abertura de shell**
   - Evidencia: [`df/bash/.bashrc`](df/bash/.bashrc), [`df/bash/.profile`](df/bash/.profile)
   - Impacto: overhead de startup e criacao recorrente de temporarios.
   - Recomendacao: cache de sessao com TTL ou execucao sob demanda.
   - Esforco: **Medio**

5. **Scripts legados ainda precisam de marcacao mais explicita**
   - Evidencia: [`bootstrap/symlinks.ps1`](bootstrap/symlinks.ps1) e `bootstrap/scripts/*`
   - Impacto: arquivos antigos podem parecer caminhos ativos para quem entra no
     repo pela primeira vez.
   - Recomendacao: reforcar a fronteira entre caminho canonico e legado.
   - Esforco: **Baixo**

### Baixo

1. **Idioma e ortografia ainda oscilam em mensagens e comentarios**
   - Evidencia: scripts e docs antigos em ingles parcial ou com typos.
   - Impacto: onboarding e UX piores que o necessario.
   - Recomendacao: continuar a padronizacao gradual em PT-BR tecnico.
   - Esforco: **Baixo**

2. **Algumas referencias externas ainda carecem de traducao operacional local**
   - Evidencia: docs de referencia e notas.
   - Impacto: onboarding mais lento.
   - Recomendacao: manter a secao "como aplicar aqui" quando a referencia ficar
     realmente central para o repo.
   - Esforco: **Baixo**

3. **Spellcheck versionado ainda nao entrou no gate canonico**
   - Evidencia: [`.cspell.json`](.cspell.json), [`scripts/run-cspell.py`](scripts/run-cspell.py), [`Taskfile.yml`](Taskfile.yml)
   - Impacto: existe task dedicada, mas a camada PT-BR/EN ainda gera ruido alto
     demais para entrar em `ci:quality`.
   - Recomendacao: curar o dicionario tecnico e reduzir falsos positivos antes
     de promover `spell:check` ao baseline oficial.
   - Esforco: **Baixo**

## Achados recentemente resolvidos

- CI desabilitado por workflows `.ignore`: resolvido
- duplicacao dos aliases Git entre `.gitconfig` e `.gitconfig-base`: resolvida
- backups e snapshots ativos fora de [`archive/`](archive/): resolvido em grande parte
- fixtures dentro de [`df/`](df/): resolvido
- stack Python sem contrato e sem lockfile: resolvido
- validacao de docs, YAML, workflows e segredos sem baseline canonico: resolvido

## Proximos passos sugeridos

1. Endurecer seguranca Git restringindo `safe.directory`.
2. Corrigir ou aposentar scripts legados de bootstrap Windows.
3. Modularizar [`bootstrap/software-list.ps1`](bootstrap/software-list.ps1).
4. Reduzir ambiguidade do `_start.ps1` e do menu parcial Windows/Linux/Mac.
5. Curar o dicionario do `cspell` para promover spellcheck ao gate canonico.
6. Otimizar shell startup em torno de `.env.local.sops` e plugins do `op`.
