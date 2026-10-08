# Runtime secrets template resolved by 1Password (`op inject`).
# Bootstrap persists this material encrypted at ~/.env.local.sops.
# Generated from app/bootstrap/user-config.yaml
export OP_SERVICE_ACCOUNT_TOKEN="{{op://secrets/dotfiles/1password/service-account}}"
export GH_TOKEN="{{op://secrets/dotfiles/github/token}}"
export GITHUB_TOKEN="{{op://secrets/dotfiles/github/token}}"
# A ref da chave age NAO entra aqui: o op inject resolve qualquer referencia do 1Password, com ou
# sem chaves, e gravaria o CONTEUDO da chave no cache (incidente 08/10/2026).
# O bootstrap le a ref de secrets.age_key_ref (user-config.yaml) ou do default.
