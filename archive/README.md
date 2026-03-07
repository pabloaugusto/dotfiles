# Archive

Historico versionado de artefatos que nao sao fonte canonica do runtime atual.

Regra:

- nada em `archive/` deve ser usado como entrypoint operativo
- se um arquivo foi arquivado, o caminho canonico ativo precisa existir em outro lugar
- novos backups, `*.bak`, `*.original` e snapshots historicos devem ir para `archive/` ou sair do Git
