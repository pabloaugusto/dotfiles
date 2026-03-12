# Scripts Legados de Bootstrap

Esta pasta contém utilitários históricos/experimentais de bootstrap Windows.

## Status

- **Não canônico** para setup atual.
- Mantido para referência, recuperação pontual e histórico técnico.

## Fluxo recomendado hoje

Use sempre:

- `app/bootstrap/_start.ps1`
- `app/bootstrap/bootstrap-windows.ps1`

## Arquivos

- `install-windows.sh`: legado Git Bash para symlinks.
- `know-folders-change-path.ps1`: experimento para Known Folders.
- `post-win-install-script.ps1`: pós-instalação legado (PowerShell/Chocolatey).

## Diretriz de manutenção

- Não introduzir dependências novas nesses scripts legados.
- Melhorias estruturais devem ir para o fluxo canônico em `app/bootstrap/`.
