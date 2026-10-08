# Runtime secrets template resolved by 1Password (`op inject`).
# Bootstrap persists this material encrypted at ~/.env.local.sops.
# Generated from app/bootstrap/user-config.yaml
#
# NENHUM token entra aqui (incidente 08/10/2026): nem service account do
# 1Password (OP_SERVICE_ACCOUNT_TOKEN), nem GH_TOKEN/GITHUB_TOKEN, nem a chave
# age. O shell nao exporta segredo; o 1Password e' acessado por ref/arquivo
# (op read --out-file) e o `gh` usa a sessao propria do `gh auth`.
# A ref da chave age NAO entra aqui: o op inject resolve qualquer referencia do
# 1Password, com ou sem chaves, e gravaria o CONTEUDO da chave no cache.
# O bootstrap le a ref de secrets.age_key_ref (user-config.yaml) ou do default.
