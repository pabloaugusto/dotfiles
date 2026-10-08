# Runtime secrets template resolved by 1Password (`op inject`).
# Bootstrap persists this material encrypted at ~/.env.local.sops.
# Generated from app/bootstrap/user-config.yaml
export OP_SERVICE_ACCOUNT_TOKEN="{{op://secrets/dotfiles/1password/service-account}}"
export GH_TOKEN="{{op://secrets/dotfiles/github/token}}"
export GITHUB_TOKEN="{{op://secrets/dotfiles/github/token}}"
# Referencia (nao o conteudo) da chave age: o bootstrap materializa o conteudo
# em arquivo 600 e exporta apenas SOPS_AGE_KEY_FILE. SEM chaves duplas: com elas o
# op inject resolve o CONTEUDO da chave e ela vaza (incidente 08/10/2026).
export SOPS_AGE_KEY_REF="op://secrets/dotfiles/age/age.key"
