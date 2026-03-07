# Limites de provedores

- `1Password`:
  - service account token e exibido apenas uma vez na criacao
  - service accounts nao acessam vaults built-in pessoais
  - itens e refs precisam viver em vault acessivel ao service account
- `GitHub`:
  - chaves SSH de auth e signing sao automatizaveis via `gh`
  - rotacao integral de PAT pessoal nao deve ser tratada como automatizavel sem
    um modelo de credencial suportado pelo provedor
- `GitLab`:
  - tokens e chaves SSH contam com suporte melhor via `glab`
- `sops+age`:
  - recifragem e update de recipients devem usar `sops updatekeys` e
    `sops rotate`
