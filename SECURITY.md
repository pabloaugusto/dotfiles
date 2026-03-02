# Security Guide (Public Repository)

This repository is intended to be safe for public hosting, but local runtime secrets still exist outside version control.

## What must never be committed

- Private keys (`*.pem`, `*.p12`, `*.pfx`, `*.key`)
- Runtime env files (`.env`, `.env.local`, `.env.*`)
- Local token files or exported credentials
- Real `authorized_keys` entries tied to personal accounts

## Current model

- Secrets are referenced via 1Password refs (`op://...`) in templates.
- Runtime values are materialized locally (`~/.env.local`) and are not versioned.
- Optional encrypted files should use `sops+age`.

## Before publishing / after major changes

1. Run tracked-file scan:
   - `git grep -n "ghp_|github_pat_|AKIA|BEGIN .*PRIVATE KEY|xoxb-|AIza"`
2. Verify ignored files:
   - `git status --ignored`
3. Review staged diff:
   - `git diff --staged`

## If a secret was exposed

1. Revoke/rotate the secret immediately.
2. Remove it from code and history (`git filter-repo` or BFG).
3. Force push rewritten history.
4. Invalidate any downstream credentials derived from the leaked secret.

## Optional hardening for contributors

- Use a pre-commit secret scanner (e.g. `gitleaks` or `detect-secrets`).
- Keep personal identity and signing key in a local untracked Git config file.
