# Análise do Ambiente: Dotfiles Multiambiente

Este documento compila de forma estruturada e didática tudo o que foi aprendido sobre a arquitetura, lógica e funcionamento do repositório de dotfiles.

## 1. Visão Geral e Objetivo
O repositório gerencia configurações (dotfiles) com foco em **paridade operacional multiambiente** (Windows como host principal e Ubuntu WSL), visando **repetibilidade** e **segurança avançada**. Todo o ambiente é montado de forma determinística, permitindo que o usuário tenha suas ferramentas de trabalho, preferências e autenticações configuradas de maneira idêntica e segura, independentemente do sistema operacional ou máquina que estiver usando.

## 2. Processo de Inicialização (Bootstrap)
O bootstrap é o mecanismo de setup do sistema. Ele está dividido operacionalmente e é orquestrado de maneiras diferentes dependendo do ambiente, mas com resultados semelhantes:

*   **No Windows:** O ponto de entrada é `bootstrap/_start.ps1`. Ele valida dependências (WinGet), lê a configuração, gerencia o setup do OneDrive e chama `bootstrap-windows.ps1`.
*   **No WSL (Ubuntu):** O fluxo acontece através de `bootstrap/bootstrap-ubuntu-wsl.sh`, que gerencia pacotes (apt/brew), diretórios, e cria links simbólicos relativos ao subsistema Linux.
*   **Gestão via Configuração:** Todo o processo é guiado por um arquivo central `bootstrap/user-config.yaml` (baseado no `user-config.yaml.tpl`), contendo caminhos, propriedades e toggles (como habilitar ou não o OneDrive).

## 3. Conformidade e Gate de Qualidade (`checkEnv`)
A qualidade e padronização do ambiente não são apenas aplicadas de forma passiva; elas são validadas ativamente por um script chamado **`checkEnv`** (disponível tanto em PowerShell quanto Bash).
Este controle atua como um "Compliance Gate" (Portão de Conformidade) nas execuções de bootstrap, avaliando:
*   Presença dos binários essenciais (op, gh, git, ssh, sops, age).
*   Saúde da sessão de login no 1Password.
*   Autenticação da linha de comando do GitHub (CLI) utilizando o protocolo SSH.
*   Assinatura dos commits confirmada via GPG configurada para uso da chave vinculada ao SSH Agent.
*   Integridade de layouts e caminhos (no Windows, principalmente envolvendo validações do OneDrive).
Caso qualquer ponto falhe, o fluxo é interrompido.

## 4. Gerenciamento de Segredos e Autenticação
É um dos pilares de maior destaque em segurança neste repositório:
*   **Zero Plain-Text:** Nenhuma credencial de alto risco é enviada (versionada) sem criptografia para o Git. Arquivos `.env` expostos são proibidos.
*   **1Password (SSOT):** O 1Password é usado como fonte unificada de verdade. Seus tokens validam a execução local extraindo variáveis no runtime através do CLI `op inject`, que substitui referências demarcadas com as chaves indicativas (ex: `{{op://...}}`) pelas credenciais reais durante o bootstrap.
*   **Sops e Age:** Variáveis de ambiente sensíveis que precisam existir fisicamente no disco são criptografadas (no arquivo `~/.env.local.sops`) gerenciadas através do `sops`. A injeção das variáveis e da chave criptográfica ocorre no próprio setup (utilizando chaves geradas do repositório 1Password), armazenando temporariamente a chave local necessária (`runtime.env`) apenas com as permissões corretas (0600).
*   **Assinatura de Commits (SSH):** Em vez de chaves GPG convencionais (com alto risco de vazamento das chaves privadas), os dotfiles integram nativamente o 1Password SSH Agent (`op-ssh-sign`), viabilizando a assinatura garantida em todos os commits sem que o segredo vaze no disco local. O socket local é exportado pelo `SSH_AUTH_SOCK` gerando transparência para o Git.
*   **Continuidade de Acesso (GitHub & Ferramentas):** A integração com as APIs minimiza expirações de token e quedas abruptas de acesso. A hierarquia lógica tem fallbacks de uso, e ferramentas como o CLI do GitHub são atrelados fortemente aos secrets do 1Password. Um token extraído interativamente é responsável por configurar o protocolo SSH (`git_protocol=ssh`) de forma automatizada no `gh`.

## 5. Orquestração e Sincronização via Tarefas (`Taskfile.yml`)
Todas as interfaces de execução do dia a dia, tanto de infraestrutura local quanto "Continuous Integration" do ambiente, residem num arquivo `Taskfile.yml`:
*   As *tasks* escondem a complexidade e suportam execução "inteligente" através da auto-detecção do SO.
*   **Drift nulo entre WSL e Host:** O fluxo desencoraja explicitamente a cópia bruta de arquivos do Windows para o Linux WSL. Em contrapartida, aplica-se o conceito `sync` (usando comandos git locais encriptados e isolados) para publicar atualizações do fluxo host para o WSL.
*   Pipelines locais simulam validações CI localmente (`task ci:validate`), com Docker containers verificando configurações.

## 6. Particularidade do Windows: OneDrive (Cloud Storage Syncing)
Para mitigar a perda de dados locais ou isolados das estações Windows, as pastas padrão (Documents, Desktop, etc) são re-linkadas fisicamente. A topologia foi projetada para que atalhos como arquivos `.ssh`, `bin` ou pastas de `projetos` apontem dinamicamente para o OneDrive garantindo backup implícito através de symlinks inteligentes. O repositório prevê falhas seletivas caso exista um drift de nomes em máquinas diferentes e conserta (Auto-Migrate) na inicialização.
