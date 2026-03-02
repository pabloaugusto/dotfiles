# bootstrap/user-config.yaml
# local bootstrap customization file (single source of truth)
# Copy to bootstrap/user-config.yaml or let _start.ps1 create it automatically.
# Do not commit personalized values.

version: 1
profile:
  name: "CHANGE_ME"
git:
  name: "CHANGE_ME"
  email: "you@example.com"
  username: "your-github-user"
  signing_key: "ssh-ed25519 AAAA_REPLACE_WITH_YOUR_PUBLIC_SSH_SIGNING_KEY"
paths:
  windows:
    onedrive_projects_path: ""
  wsl:
    onedrive_root: "/mnt/d/OneDrive"
    onedrive_clients_dir: ""
    onedrive_projects_dir: ""
bootstrap:
  add_user:
    enabled: false
    username: ""
    password_hash: ""
secrets:
  onepassword_service_account_ref: "op://secrets/dotfiles/1password/service-account"
  github_project_pat_ref: "op://secrets/dotfiles/github/token"
  github_full_access_ref: "op://secrets/github/api/token"
  age_key_ref: "op://secrets/dotfiles/age/age.key"
