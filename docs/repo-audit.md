# Auditoria do Repositório (2026-03-03)

Auditoria técnica dos arquivos versionados (excluindo ignorados) com foco em:

- riscos de segurança
- inconsistências de fluxo
- duplicações e legado
- oportunidades de simplificação/modernização

## Escopo e método

- Escopo: arquivos rastreados por Git (texto e configuração).
- Exceção de edição: código third-party vendorizado (`df/powershell/.inc/3rd/*`).
- Baseado em leitura estática e revisão de fluxos bootstrap + shell + auth.

---

## Crítico

1. **Historico: pipelines CI estavam desabilitados no repositório**
   - Evidência original: `.github/workflows/check-scripts.yml.ignore`, `.github/workflows/linter.yaml.ignore`
   - Impacto observado na epoca: ausência de validação automática, regressões entram sem gate.
   - Status atual: resolvido com workflows ativos versionados e gates formais de qualidade, PR, IA e integração do bootstrap.
   - Esforço: **Médio**

2. **Política Git global insegura (`safe.directory = *`)**
   - Evidência: `df/git/.gitconfig:178`, `df/git/.gitconfig:179`
   - Impacto: desativa proteção de ownership suspeito para qualquer diretório.
   - Recomendação: restringir `safe.directory` a paths necessários (ex.: `~/dotfiles`, `/home/*/dotfiles`, `C:/Users/*/dotfiles`).
   - Esforço: **Baixo**

3. **Arquivo temporário/duplicado versionado (`.bw.tmp`)**
   - Evidência: `.bw.tmp`
   - Impacto: risco de divergência de lógica e ruído de manutenção; pode conter snapshot obsoleto.
   - Recomendação: remover do versionamento ou mover para pasta de scratch ignorada.
   - Esforço: **Baixo**

---

## Alto

1. **Controle de fluxo frágil no bootstrap Windows (`break` fora de loop)**
   - Evidência: `bootstrap/bootstrap-windows.ps1:46`, `bootstrap/bootstrap-windows.ps1:56`, `bootstrap/bootstrap-windows.ps1:68`
   - Impacto: comportamento inconsistente em erro (pode abortar de forma inesperada).
   - Recomendação: substituir por `return`/`throw` explícito por contexto.
   - Esforço: **Baixo**

2. **Dependência de `sudo` dentro de script PowerShell administrativo**
   - Evidência: `bootstrap/bootstrap-windows.ps1:145`
   - Impacto: pode falhar em ambiente sem alias `sudo` carregado.
   - Recomendação: usar `New-Item` direto (já há elevação) ou helper interno.
   - Esforço: **Baixo**

3. **Pré-requisitos Windows rígidos (acoplamento com OneDrive + `D:\`)**
   - Evidência: `bootstrap/_start.ps1:88`, `bootstrap/_start.ps1:95`
   - Impacto: reduz portabilidade e quebra em hosts válidos sem esse layout.
   - Recomendação: tornar validação configurável via YAML central e fallback saneado.
   - Esforço: **Médio**

4. **Menu expõe Linux/Mac em `_start.ps1` sem implementação real**
   - Evidência: `bootstrap/_start.ps1:183`, `bootstrap/_start.ps1:184`, `bootstrap/_start.ps1:248`
   - Impacto: UX ambígua e expectativa incorreta.
   - Recomendação: ocultar opções não suportadas ou implementar dispatch real.
   - Esforço: **Baixo**

5. **Scripts legados com comandos potencialmente quebrados**
   - Evidência: `bootstrap/scripts/post-win-install-script.ps1:23`, `bootstrap/scripts/post-win-install-script.ps1:30` (`Invoke-RestMeMethod`)
   - Impacto: scripts de suporte podem falhar silenciosamente quando reutilizados.
   - Recomendação: marcar como deprecated de forma explícita e/ou corrigir comandos.
   - Esforço: **Baixo**

6. **Duplicação de instalação de pacotes de auth no bootstrap Windows**
   - Evidência: `bootstrap/software-list.ps1:82`, `bootstrap/software-list.ps1:209`, `bootstrap/software-list.ps1:210` e `bootstrap/bootstrap-windows.ps1:229-232`
   - Impacto: logs ruidosos, repetição de tentativas, tempo extra.
   - Recomendação: separar lista em “core obrigatório” e “catálogo opcional”.
   - Esforço: **Médio**

7. **ID de pacote com espaço final (falha de instalação)**
   - Evidência: `bootstrap/software-list.ps1:208` (`Microsoft.OpenSSH.Preview `)
   - Impacto: instalação falha por ID inválido.
   - Recomendação: remover espaço final e validar lista automaticamente.
   - Esforço: **Baixo**

8. **Carga de plugin `op` no Bash pode sobrescrever comandos esperados**
   - Evidência: `df/bash/.bashrc:187`
   - Impacto: `gh`/`ssh` podem virar alias wrapper, alterando `checkEnv` e scripts.
   - Recomendação: condicionar plugin por flag (`DOTFILES_ENABLE_OP_PLUGINS=1`) ou normalizar chamadas com `command gh`.
   - Esforço: **Baixo**

---

## Médio

1. **Duas fontes de aliases Git com possível divergência**
   - Evidência: `df/git/.gitconfig:16`, `df/git/.gitconfig-base:123`
   - Impacto: manutenção duplicada e comportamento difícil de prever.
   - Recomendação: consolidar aliases em uma única camada (`.gitconfig-base`) e manter overrides mínimos por ambiente.
   - Esforço: **Médio**

2. **`push.default=matching` em config legada conflita com práticas seguras**
   - Evidência: `df/git/.gitconfig:107`
   - Impacto: risco de push involuntário de múltiplas branches.
   - Recomendação: padronizar em `simple` (já utilizado em base moderna).
   - Esforço: **Baixo**

3. **Função de instalação apt usa heurística frágil de detecção por comando**
   - Evidência: `df/bash/.inc/_functions.sh:92`, `df/bash/.inc/_functions.sh:100`
   - Impacto: falso positivo/negativo ao decidir install vs upgrade.
   - Recomendação: usar `dpkg -s`/`apt-cache policy` para pacote apt.
   - Esforço: **Médio**

4. **`checkEnv` Bash usa arquivos temporários com nomes previsíveis em `/tmp`**
   - Evidência: `df/bash/.inc/check-env.sh:297`, `df/bash/.inc/check-env.sh:301`, `df/bash/.inc/check-env.sh:316`
   - Impacto: risco de colisão em execuções concorrentes.
   - Recomendação: usar `mktemp` para todos artefatos de saída.
   - Esforço: **Baixo**

5. **Decrypt de `.env.local.sops` em toda abertura de shell**
   - Evidência: `df/bash/.bashrc:165-167`, `df/bash/.profile:18-20`
   - Impacto: overhead de startup + criação de temporários frequentes.
   - Recomendação: cache de sessão com TTL curto ou `sops exec-env` sob demanda.
   - Esforço: **Médio**

6. **Acúmulo de arquivos legados/backups no versionamento**
   - Evidência original: `bootstrap/bootstrap-ubuntu.original.sh`, `df/oh-my-posh/pablo.omp.json.bak`, `df/powertoys/settings_133470085785000868.ptb`
   - Status atual: `bootstrap-ubuntu.original.sh` e `pablo.omp.json.bak` foram movidos para `archive/`; o export do PowerToys foi canonizado para `df/powertoys/settings.ptb`.
   - Impacto: ruído de manutenção e ambiguidade sobre fonte canônica.
   - Recomendação: continuar empurrando snapshots, backups e artefatos históricos para `archive/` ou removê-los do Git quando não forem essenciais.
   - Esforço: **Baixo**

7. **Script legacy `bootstrap/symlinks.ps1` com path de include antigo**
   - Evidência: `bootstrap/symlinks.ps1:19`
   - Impacto: execução manual pode quebrar por path não canônico.
   - Recomendação: alinhar include para path atual ou marcar arquivo como somente referência.
   - Esforço: **Baixo**

---

## Baixo

1. **Inconsistências de idioma/ortografia em mensagens**
   - Evidência: textos mistos em scripts e docs (`supportted`, `comming`, `Instaling`, etc.).
   - Impacto: baixa clareza de UX.
   - Recomendação: padronizar PT-BR técnico nas mensagens.
   - Esforço: **Baixo**

2. **Catálogo de software monolítico sem perfil por contexto**
   - Evidência: `bootstrap/software-list.ps1` (lista extensa para perfis distintos).
   - Impacto: bootstrap lento e propenso a falhas em hosts diferentes.
   - Recomendação: separar em perfis (core/dev/media/workstation-full).
   - Esforço: **Médio**

3. **Alguns documentos de referência ainda dependem de fontes externas sem contexto local**
   - Evidência: `docs/*` (links externos sem mapping para comandos do repo).
   - Impacto: onboarding mais lento.
   - Recomendação: manter “Como aplicar aqui” em cada doc de referência.
   - Esforço: **Baixo**

---

## Próximos passos sugeridos (ordem)

1. Reativar CI mínimo (parse/lint/links).
2. Endurecer segurança Git (`safe.directory` restrito, `push.default` seguro).
3. Consolidar configurações legadas/duplicadas (`.bw.tmp`, `.bak`, `*.original*`).
4. Modularizar `software-list.ps1` por perfil.
5. Revisar fluxos shell para reduzir ambiguidades de alias/plugin.
