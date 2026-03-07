# Checklist

## Arquivos mais sensiveis

- [`bootstrap/bootstrap-config.ps1`](bootstrap/bootstrap-config.ps1)
- [`bootstrap/bootstrap-windows.ps1`](bootstrap/bootstrap-windows.ps1)
- [`bootstrap/bootstrap-ubuntu-wsl.sh`](bootstrap/bootstrap-ubuntu-wsl.sh)
- [`bootstrap/user-config.yaml.tpl`](bootstrap/user-config.yaml.tpl)
- [`Taskfile.yml`](Taskfile.yml)

## Invariantes

- template, parser e docs devem refletir o mesmo contrato
- caminhos canonicos absolutos sao preferiveis
- links finais precisam apontar para o destino real, nao para outro atalho
- `refresh` e `relink` devem suportar rerun sem dano

## Sinais de regressao

- task presume `%USERPROFILE%/dotfiles` ou `~/dotfiles`
- config local ganha comentario ou secao que o template nao conhece
- parser aceita um formato que o writer nao sabe reemitir
- validacao depende do ambiente pessoal do operador
