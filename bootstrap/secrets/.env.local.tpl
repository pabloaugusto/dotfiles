# Runtime secrets template injected by 1Password (`op inject`).
# Output file target: ~/.env.local
# Keep only references (`op://...`) here. Do not place plaintext secrets.
export OP_SERVICE_ACCOUNT_TOKEN="op://secrets/dotfiles/1password/service-account" # 1password service account
# Dedicated PAT for dotfiles/bootstrap (least privilege, preferred).
# Bootstrap auth logic still supports fallback to the full-access token ref if needed.
export GITHUB_TOKEN="op://secrets/dotfiles/github/token"
export SOPS_AGE_KEY="op://secrets/dotfiles/age/age.key"
