# Windows Terminal Config

Arquivos deste diretório:

- `settings.json`: configuração principal do Windows Terminal.

## Observações

- `settings.json` é JSON estrito: não inserir comentários inválidos.
- Chaves e decisões de configuração estão documentadas em:
  - `docs/config-reference.md`

## Fluxo de aplicação

Durante bootstrap Windows, o arquivo é linkado para o perfil do usuário no
pacote do Windows Terminal (`...\\LocalState\\settings.json`).
