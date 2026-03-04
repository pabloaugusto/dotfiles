# Config Reference (arquivos estritos)

Guia de referência para arquivos de configuração que **não** suportam comentários
inline seguros (JSON/TOML/etc.) ou que devem permanecer enxutos.

## Objetivo

- documentar significado de chaves sem quebrar sintaxe de consumidores
- reduzir custo de manutenção para humanos e agentes de IA

## `bootstrap/user-config.yaml`

Uso:

- fonte única local de configuração do bootstrap (wizard + sincronização de derivados)

Pontos críticos (OneDrive Windows):

- `paths.windows.onedrive_enabled`: liga/desliga dependência de OneDrive
- `paths.windows.onedrive_root`: root desejada (auto-detect quando vazio)
- `paths.windows.onedrive_auto_migrate`: tentativa best-effort de migração automática
- `paths.windows.links_profile_*`: origens de symlinks no perfil
- `paths.windows.links_drive_enabled` + `links_drive_*`: atalhos opcionais em drive raiz
- `paths.windows.profile_links_migrate_content`: migra conteúdo antes de criar links das pastas padrão
- `paths.windows.profile_links_*`: ativa e define destino de pastas padrão (`Documents`, `Desktop`, `Downloads`, `Pictures`, `Videos`, `Music`, `Contacts`, `Favorites`, `Links`)

Observação:

- mudanças nesses campos impactam diretamente `bootstrap/bootstrap-windows.ps1`,
  incluindo os gates de validação pós-bootstrap.

## `df/windows-terminal/settings.json`

Uso:

- configura perfis, aparência, fontes e atalhos do Windows Terminal
- é linkado durante bootstrap Windows

Pontos críticos:

- perfil PowerShell e perfil WSL
- fonte Nerd Font compatível com prompt
- actions/keybindings que impactam produtividade diária

## `df/vscode/settings.json`

Uso:

- define comportamento editor, terminal integrado, extensões e UX

Pontos críticos:

- integração com formatter/linter
- terminal default profile
- opções que afetam desempenho de workspace grande

## `df/vscode/keybindings.json`

Uso:

- customizações de atalhos

Pontos críticos:

- atalhos que colidem com defaults do VS Code
- atalhos críticos de navegação/build

## `df/vscode/mcp.json`

Uso:

- configuração de integração MCP do ambiente local

Pontos críticos:

- caminhos locais válidos
- políticas de segurança para ferramentas externas

## `df/oh-my-posh/pablo.omp.json`

Uso:

- layout visual do prompt

Pontos críticos:

- performance do prompt (segmentos caros)
- ícones/fonte compatível no terminal

## `df/config/atuin/config.toml`

Uso:

- histórico shell sincronizado/consultável

Pontos críticos:

- política de sync
- retenção e privacidade do histórico

## `df/secrets/dotfiles.sops.yaml`

Uso:

- regras de criptografia para `sops+age`

Pontos críticos:

- `creation_rules.path_regex` cobrindo arquivos corretos
- `age` recipient atualizado
- `encrypted_regex` coerente com seu schema de secrets

## Boas práticas gerais

- validar JSON/TOML/YAML após qualquer alteração
- manter documentação sincronizada com fluxo real de bootstrap
- não usar comentários inválidos em formatos estritos
