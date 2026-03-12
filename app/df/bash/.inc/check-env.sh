#!/usr/bin/env bash

# checkEnv
# Health check for dotfiles auth/signing stack:
# - 1Password CLI/session
# - GitHub CLI auth (SSH protocol)
# - SSH agent path and GitHub handshake
# - Git SSH signing with 1Password signer

checkEnv() {
  local requested_mode="${1:-${DOTFILES_GIT_SIGN_MODE:-auto}}"
  case "$requested_mode" in
    auto|human|automation) ;;
    *)
      echo "checkEnv: modo de assinatura invalido: $requested_mode" >&2
      return 1
      ;;
  esac

  # Result accumulator used to build a structured summary at the end.
  local _results=()
  local _fixes=()
  local _tmp_dir=""
  local _tmp_out=""
  local git_probe=""
  local git_probe_tmp=""
  local resolved_mode=""
  local automation_key_ref=""
  local git_ssh_command=""
  local gpg_format=""
  local commit_sign=""
  local signing_key=""
  local gpg_program=""

  # Adds a normalized status entry to in-memory report.
  _add_result() {
    local status="$1"
    local item="$2"
    local detail="$3"
    local solution="$4"
    _results+=("${status}|${item}|${detail}")
    if [ -n "$solution" ]; then
      _fixes+=("${item}|${solution}")
    fi
  }

  # Pretty-printer for a single check result line.
  _print_result() {
    local status="$1"
    local item="$2"
    local detail="$3"
    local tag=""
    case "$status" in
      success) tag="[SUCCESS]" ;;
      fail) tag="[FAIL]" ;;
      *) tag="[INCONCLUSIVE]" ;;
    esac
    printf '%s %s - %s\n' "$tag" "$item" "$detail"
  }

  # Verifies command existence and appends check result.
  _expect_cmd() {
    local cmd="$1"
    if command -v "$cmd" >/dev/null 2>&1; then
      _add_result "success" "Command: $cmd" "Disponivel em $(command -v "$cmd")" ""
      return 0
    fi
    _add_result "fail" "Command: $cmd" "Nao encontrado no PATH." "Instale '$cmd' no bootstrap e recarregue o shell."
    return 1
  }

  # Wraps potentially blocking commands so checkEnv does not hang forever.
  _run_with_timeout() {
    local seconds="$1"
    shift
    if command -v timeout >/dev/null 2>&1; then
      timeout "$seconds" "$@"
    else
      "$@"
    fi
  }

  echo "checkEnv: validating environment"

  # Base runtime commands expected by dotfiles bootstrap + auth flow.
  _expect_cmd op >/dev/null
  _expect_cmd gh >/dev/null
  _expect_cmd git >/dev/null
  _expect_cmd ssh >/dev/null

  if command -v sops >/dev/null 2>&1; then
    _add_result "success" "Command: sops" "Disponivel em $(command -v sops)" ""
  else
    _add_result "inconclusive" "Command: sops" "Nao encontrado no PATH." "Instale sops se pretende usar secrets versionados com age."
  fi

  if command -v age >/dev/null 2>&1; then
    _add_result "success" "Command: age" "Disponivel em $(command -v age)" ""
  else
    _add_result "inconclusive" "Command: age" "Nao encontrado no PATH." "Instale age para habilitar criptografia/decriptografia sops."
  fi

  # 1Password session + reference readability checks.
  if command -v op >/dev/null 2>&1; then
    local op_ok=0
    if _run_with_timeout 8 op whoami >/dev/null 2>&1; then
      op_ok=1
    elif [ -f "$HOME/.env.local.sops" ] && command -v sops >/dev/null 2>&1; then
      local _tmp_env token_line token_value
      _tmp_env="$(mktemp)"
      if sops -d "$HOME/.env.local.sops" >"$_tmp_env" 2>/dev/null; then
        token_line="$(grep -E '^(export[[:space:]]+)?OP_SERVICE_ACCOUNT_TOKEN=' "$_tmp_env" | tail -n1 || true)"
        token_value="${token_line#*=}"
        token_value="${token_value%\"}"
        token_value="${token_value#\"}"
        token_value="${token_value%\'}"
        token_value="${token_value#\'}"
        token_value="$(printf '%s' "$token_value" | tr -d '\r')"
        if [ -n "$token_value" ]; then
          export OP_SERVICE_ACCOUNT_TOKEN="$token_value"
          if _run_with_timeout 8 op whoami >/dev/null 2>&1; then
            op_ok=1
          fi
        fi
      fi
      rm -f "$_tmp_env"
    fi

    if [ "$op_ok" -eq 1 ]; then
      _add_result "success" "1Password CLI session" "op whoami executou com sucesso." ""
    else
      _add_result "fail" "1Password CLI session" "op whoami falhou (inclusive apos 1 retry)." "Garanta OP_SERVICE_ACCOUNT_TOKEN valido e execute 'op whoami'."
    fi

    local refs_file=""
    if [ -n "$git_probe" ] && [ -f "$git_probe/app/df/secrets/secrets-ref.yaml" ]; then
      refs_file="$git_probe/app/df/secrets/secrets-ref.yaml"
    elif [ -f "$HOME/dotfiles/app/df/secrets/secrets-ref.yaml" ]; then
      refs_file="$HOME/dotfiles/app/df/secrets/secrets-ref.yaml"
    fi
    if [ -f "$refs_file" ]; then
      while IFS= read -r ref; do
        [ -n "$ref" ] || continue
        if _run_with_timeout 8 op read "$ref" >/dev/null 2>&1; then
          _add_result "success" "1Password secret ref" "$ref acessivel." ""
        else
          _add_result "fail" "1Password secret ref" "$ref nao acessivel no contexto atual." "Ajuste permissoes do service account no vault/item."
        fi
      done < <(grep -Eo 'op://[A-Za-z0-9._/-]+' "$refs_file" | sort -u)
    fi
  fi

  # GitHub CLI login + protocol checks.
  if command -v gh >/dev/null 2>&1; then
    local gh_bin=""
    gh_bin="$(type -P gh 2>/dev/null || true)"
    if [ -z "$gh_bin" ]; then
      gh_bin="$(command -v gh 2>/dev/null || true)"
    fi
    [ -n "$gh_bin" ] || gh_bin="gh"

    _tmp_out="$(mktemp)"
    if ! _run_with_timeout 8 "$gh_bin" auth status --hostname github.com >"$_tmp_out" 2>&1; then
      local github_token="${GH_TOKEN:-${GITHUB_TOKEN:-}}"
      if [ -z "$github_token" ] && command -v op >/dev/null 2>&1; then
        for ref in "op://secrets/dotfiles/github/token" "op://secrets/github/api/token" "op://Personal/github/token-full-access"; do
          github_token="$(op read "$ref" 2>/dev/null || true)"
          [ -n "$github_token" ] && break
        done
      fi
      if [ -n "$github_token" ]; then
        printf '%s\n' "$github_token" | "$gh_bin" auth login --hostname github.com --git-protocol ssh --with-token >/dev/null 2>&1 || true
        "$gh_bin" config set git_protocol ssh --host github.com >/dev/null 2>&1 || true
      fi
      _run_with_timeout 8 "$gh_bin" auth status --hostname github.com >"$_tmp_out" 2>&1 || true
    fi

    if grep -q "Logged in to github.com" "$_tmp_out" || _run_with_timeout 8 "$gh_bin" auth status --hostname github.com >/dev/null 2>&1; then
      _add_result "success" "GitHub CLI auth" "gh autenticado no host github.com." ""
    else
      _add_result "fail" "GitHub CLI auth" "gh nao autenticado no host github.com." "Rode 'gh auth login --hostname github.com --git-protocol ssh --with-token' com token do 1Password (preferencial: op://secrets/dotfiles/github/token; contingencia final: op://Personal/github/token-full-access)."
    fi

    "$gh_bin" config set git_protocol ssh --host github.com >/dev/null 2>&1 || true
    "$gh_bin" config set git_protocol ssh >/dev/null 2>&1 || true

    local gh_protocol=""
    gh_protocol="$("$gh_bin" config get git_protocol --host github.com 2>/dev/null | tr -d '\r' | tail -n1)"
    if [ -z "$gh_protocol" ]; then
      gh_protocol="$("$gh_bin" config get git_protocol 2>/dev/null | tr -d '\r' | tail -n1)"
    fi

    if [ "$gh_protocol" = "ssh" ]; then
      _add_result "success" "GitHub CLI git protocol" "git_protocol=ssh." ""
    else
      _add_result "fail" "GitHub CLI git protocol" "git_protocol='${gh_protocol:-<empty>}'." "Execute 'gh config set git_protocol ssh --host github.com'."
    fi
    rm -f "$_tmp_out"
  fi

  # Git signature policy checks (resolved in context of dotfiles repo when present).
  if command -v git >/dev/null 2>&1; then
    git_probe="$(git rev-parse --show-toplevel 2>/dev/null || true)"
    if [ -z "$git_probe" ] || [ ! -d "$git_probe/.git" ]; then
      git_probe_tmp="$(mktemp -d "$HOME/checkenv-probe.XXXXXX")"
      git -C "$git_probe_tmp" init -q >/dev/null 2>&1 || true
      git_probe="$git_probe_tmp"
    fi

    gpg_format="$(git -C "$git_probe" config --get gpg.format 2>/dev/null)"
    commit_sign="$(git -C "$git_probe" config --get commit.gpgsign 2>/dev/null)"
    signing_key="$(git -C "$git_probe" config --get user.signingkey 2>/dev/null)"
    gpg_program="$(git -C "$git_probe" config --get gpg.ssh.program 2>/dev/null)"
    git_ssh_command="$(git -C "$git_probe" config --get core.sshCommand 2>/dev/null || true)"
    local worktree_mode
    local automation_private_key_path
    worktree_mode="$(git -C "$git_probe" config --worktree --get dotfiles.signing.mode 2>/dev/null || true)"
    automation_key_ref="$(git -C "$git_probe" config --worktree --get dotfiles.signing.automationPublicKeyRef 2>/dev/null || true)"
    automation_private_key_path="$(git -C "$git_probe" config --worktree --get dotfiles.signing.automationPrivateKeyPath 2>/dev/null || true)"
    if [ "$requested_mode" = "auto" ]; then
      if [ "$worktree_mode" = "automation" ]; then
        resolved_mode="automation"
      else
        resolved_mode="human"
      fi
    else
      resolved_mode="$requested_mode"
    fi

    _add_result "success" "Git signing mode" "mode=$resolved_mode." ""

    if [ "$gpg_format" = "ssh" ]; then
      _add_result "success" "Git signing format" "gpg.format=ssh." ""
    else
      _add_result "fail" "Git signing format" "gpg.format='$gpg_format'." "Defina 'git config --global gpg.format ssh'."
    fi

    if [ "$commit_sign" = "true" ]; then
      _add_result "success" "Git commit signing default" "commit.gpgsign=true." ""
    else
      _add_result "fail" "Git commit signing default" "commit.gpgsign='$commit_sign'." "Defina 'git config --global commit.gpgsign true'."
    fi

    local has_automation_private_key=0
    if [ "$resolved_mode" = "automation" ] && [ -n "$automation_private_key_path" ] && [ -f "$automation_private_key_path" ] && [ "$signing_key" = "$automation_private_key_path" ]; then
      has_automation_private_key=1
    fi

    if printf '%s' "$signing_key" | grep -q '^ssh-'; then
      _add_result "success" "Git signing key" "user.signingkey em formato SSH." ""
    elif [ $has_automation_private_key -eq 1 ]; then
      _add_result "success" "Git signing key" "user.signingkey aponta para a chave tecnica local: $automation_private_key_path." ""
    else
      if [ "$resolved_mode" = "automation" ]; then
        _add_result "fail" "Git signing key" "user.signingkey ausente ou invalida." "Execute task git:signing:mode:automation para sincronizar a chave tecnica local e o signer da worktree."
      else
        _add_result "fail" "Git signing key" "user.signingkey ausente ou invalida." "Defina 'git config --global user.signingkey \"ssh-ed25519 ...\"'."
      fi
    fi

    if [ "$resolved_mode" = "automation" ]; then
      local local_automation_public_key=""
      if [ $has_automation_private_key -eq 1 ] && [ -f "${automation_private_key_path}.pub" ]; then
        local_automation_public_key="$(awk 'NF {print; exit}' "${automation_private_key_path}.pub" | tr -s '[:space:]' ' ' | sed 's/^ //; s/ $//')"
      fi

      if [ -z "$automation_key_ref" ]; then
        if [ -n "$local_automation_public_key" ] && printf '%s' "$local_automation_public_key" | grep -q '^ssh-'; then
          _add_result "success" "Automation signing key ref" "A worktree esta usando o par de chaves tecnico local; a ref publica e opcional neste modo." ""
        else
          _add_result "fail" "Automation signing key ref" "Nem dotfiles.signing.automationPublicKeyRef nem a chave publica local da worktree foram encontrados." "Aplique task git:signing:mode:automation apos provisionar o par tecnico local ou configurar a ref publica."
        fi
      elif ! command -v op >/dev/null 2>&1; then
        _add_result "fail" "Automation signing key ref" "op nao esta disponivel para resolver $automation_key_ref." "Instale/autentique o 1Password CLI antes de usar o signer tecnico."
      else
        local automation_key_value automation_key_normalized signing_key_normalized
        automation_key_value="$(op read "$automation_key_ref" 2>/dev/null || true)"
        automation_key_normalized="$(printf '%s' "$automation_key_value" | awk 'NF {print; exit}' | tr -s '[:space:]' ' ' | sed 's/^ //; s/ $//')"
        signing_key_normalized="$(printf '%s' "$signing_key" | awk 'NF {print; exit}' | tr -s '[:space:]' ' ' | sed 's/^ //; s/ $//')"
        if [ -z "$automation_key_normalized" ] || ! printf '%s' "$automation_key_normalized" | grep -q '^ssh-'; then
          _add_result "fail" "Automation signing key ref" "$automation_key_ref nao retornou uma chave publica SSH valida." "Corrija a ref no 1Password ou rotacione a chave tecnica."
        elif [ "$automation_key_normalized" = "$signing_key_normalized" ] || [ "$automation_key_normalized" = "$local_automation_public_key" ]; then
          _add_result "success" "Automation signing key ref" "$automation_key_ref confere com user.signingkey da worktree." ""
        else
          _add_result "fail" "Automation signing key ref" "$automation_key_ref nao confere com user.signingkey atual." "Rode novamente task git:signing:mode:automation para sincronizar a worktree."
        fi
      fi
    fi

    local gpg_program_resolved=""
    local gpg_program_type=""
    if [ -n "$gpg_program" ]; then
      local gpg_program_cmd="$gpg_program"
      gpg_program_cmd="${gpg_program_cmd%%[[:space:]]*}"
      if [ -x "$gpg_program_cmd" ]; then
        gpg_program_resolved="$gpg_program_cmd"
      else
        gpg_program_resolved="$(type -P "$gpg_program_cmd" 2>/dev/null || true)"
        if [ -z "$gpg_program_resolved" ] && [ "$gpg_program_cmd" = "op-ssh-sign" ] && [ -x "$HOME/.local/bin/op-ssh-sign" ]; then
          gpg_program_resolved="$HOME/.local/bin/op-ssh-sign"
        fi
      fi
      gpg_program_type="$(type -t "$gpg_program_cmd" 2>/dev/null || true)"
    fi

    if [ -n "$gpg_program_resolved" ]; then
      _add_result "success" "1Password signer program" "gpg.ssh.program resolvido para: $gpg_program_resolved" ""
    elif [ -n "$gpg_program" ] && [ "$gpg_program_type" = "alias" ]; then
      _add_result "fail" "1Password signer program" "gpg.ssh.program aponta para alias ($gpg_program), e o Git exige executavel real." "Use um caminho/binario real para op-ssh-sign (ex.: ~/.local/bin/op-ssh-sign)."
    elif [ -n "$gpg_program" ]; then
      _add_result "fail" "1Password signer program" "gpg.ssh.program configurado, mas nao resolvivel: $gpg_program" "Ajuste gpg.ssh.program para op-ssh-sign/op-ssh-sign-wsl valido."
    else
      _add_result "fail" "1Password signer program" "gpg.ssh.program nao definido." "Defina gpg.ssh.program para o binario do 1Password."
    fi

  fi

  # SOPS/age readiness.
  if [ -n "${SOPS_AGE_KEY_FILE:-}" ] && [ -f "${SOPS_AGE_KEY_FILE}" ]; then
    _add_result "success" "SOPS age key file" "SOPS_AGE_KEY_FILE definido e arquivo existe." ""
  elif [ -n "${SOPS_AGE_KEY:-}" ]; then
    _add_result "success" "SOPS age key file" "SOPS_AGE_KEY existe no ambiente (modo env-only)." ""
  else
    _add_result "fail" "SOPS age key file" "Nenhuma chave age detectada no ambiente." "Defina SOPS_AGE_KEY (recomendado) ou configure SOPS_AGE_KEY_FILE."
  fi

  # SSH identity policy + github handshake checks.
  if command -v ssh >/dev/null 2>&1; then
    local ssh_graph identity_agent ssh_t_out ssh_t_rc
    ssh_graph="$(ssh -G github.com 2>/dev/null | tr -d '\r')"
    identity_agent="$(printf '%s\n' "$ssh_graph" | awk '/^identityagent /{print $2; exit}')"
    if printf '%s' "$identity_agent" | grep -Eq '1password|openssh-ssh-agent|/tmp/1password-agent\.sock'; then
      _add_result "success" "SSH identity agent" "identityagent=$identity_agent" ""
    elif [ -n "$identity_agent" ]; then
      _add_result "fail" "SSH identity agent" "identityagent inesperado: $identity_agent" "Aponte IdentityAgent para o agent do 1Password."
    else
      _add_result "fail" "SSH identity agent" "identityagent nao definido para github.com." "Configure ~/.ssh/config(.local) para usar o agent do 1Password."
    fi

    if printf '%s\n' "$ssh_graph" | grep -q '^identityfile none$'; then
      _add_result "success" "SSH identity source policy" "identityfile none ativo para evitar fallback local." ""
    else
      _add_result "fail" "SSH identity source policy" "identityfile none nao encontrado para github.com." "Use IdentityFile none para garantir chaves somente via 1Password agent."
    fi

    if [ -S /tmp/1password-agent.sock ]; then
      _add_result "success" "1Password agent socket" "/tmp/1password-agent.sock presente." ""
    elif printf '%s' "$identity_agent" | grep -q 'openssh-ssh-agent'; then
      _add_result "success" "1Password agent socket" "Agent resolvido via named pipe do Windows ($identity_agent)." ""
    else
      _add_result "fail" "1Password agent socket" "/tmp/1password-agent.sock ausente e sem fallback de agent via Windows." "Ative a integracao SSH do 1Password com WSL e reinicie o terminal."
    fi

    if [ "$resolved_mode" = "automation" ] && [ -n "$git_ssh_command" ]; then
      local git_remote_out git_remote_rc
      if command -v timeout >/dev/null 2>&1; then
        git_remote_out="$(timeout 15 git -C "$git_probe" ls-remote origin 2>&1)"
      else
        git_remote_out="$(git -C "$git_probe" ls-remote origin 2>&1)"
      fi
      git_remote_rc=$?
      if [ $git_remote_rc -eq 0 ]; then
        _add_result "success" "SSH auth to GitHub" "Acesso GitHub validado via core.sshCommand da worktree." ""
      elif [ $git_remote_rc -eq 124 ]; then
        _add_result "fail" "SSH auth to GitHub" "git ls-remote origin excedeu tempo limite com core.sshCommand ativo." "Verifique a chave tecnica registrada no GitHub e a conectividade SSH."
      else
        _add_result "fail" "SSH auth to GitHub" "git ls-remote origin falhou com core.sshCommand ativo: $git_remote_out" "Rode task git:signing:mode:automation novamente ou valide a chave tecnica de autenticacao no GitHub."
      fi
    else
      if command -v timeout >/dev/null 2>&1; then
        ssh_t_out="$(timeout 10 ssh -T git@github.com -o BatchMode=yes -o NumberOfPasswordPrompts=0 -o ConnectTimeout=5 -o StrictHostKeyChecking=accept-new 2>&1)"
      else
        ssh_t_out="$(ssh -T git@github.com -o BatchMode=yes -o NumberOfPasswordPrompts=0 -o ConnectTimeout=5 -o StrictHostKeyChecking=accept-new 2>&1)"
      fi
      ssh_t_rc=$?
      if printf '%s' "$ssh_t_out" | grep -qi "successfully authenticated"; then
        _add_result "success" "SSH auth to GitHub" "Handshake SSH com GitHub OK." ""
      elif command -v ssh.exe >/dev/null 2>&1; then
        local ssh_win_out ssh_win_rc
        if command -v timeout >/dev/null 2>&1; then
          ssh_win_out="$(timeout 12 ssh.exe -T git@github.com -o BatchMode=yes -o NumberOfPasswordPrompts=0 -o ConnectTimeout=5 -o StrictHostKeyChecking=accept-new 2>&1)"
        else
          ssh_win_out="$(ssh.exe -T git@github.com -o BatchMode=yes -o NumberOfPasswordPrompts=0 -o ConnectTimeout=5 -o StrictHostKeyChecking=accept-new 2>&1)"
        fi
        ssh_win_rc=$?
        if printf '%s' "$ssh_win_out" | grep -qi "successfully authenticated"; then
          _add_result "success" "SSH auth to GitHub" "Handshake SSH com GitHub OK via fallback ssh.exe." ""
        elif [ $ssh_t_rc -eq 124 ] || [ $ssh_win_rc -eq 124 ]; then
          _add_result "fail" "SSH auth to GitHub" "Teste SSH excedeu tempo limite." "Verifique conectividade e rode novamente."
        elif [ $ssh_t_rc -eq 255 ] || [ $ssh_win_rc -eq 255 ]; then
          _add_result "fail" "SSH auth to GitHub" "Falha de autenticacao SSH (ssh/ssh.exe): $ssh_t_out | $ssh_win_out" "Verifique chave autorizada no GitHub e agent do 1Password."
        else
          _add_result "fail" "SSH auth to GitHub" "Retorno nao deterministico (ssh/ssh.exe): $ssh_t_out | $ssh_win_out" "Rode manualmente 'ssh -T git@github.com' para confirmar."
        fi
      elif [ $ssh_t_rc -eq 124 ]; then
        _add_result "fail" "SSH auth to GitHub" "Teste SSH excedeu tempo limite." "Verifique conectividade e rode novamente."
      elif [ $ssh_t_rc -eq 255 ]; then
        _add_result "fail" "SSH auth to GitHub" "Falha de autenticacao SSH: $ssh_t_out" "Verifique chave autorizada no GitHub e agent do 1Password."
      else
        _add_result "fail" "SSH auth to GitHub" "Retorno nao deterministico: $ssh_t_out" "Rode manualmente 'ssh -T git@github.com' para confirmar."
      fi
    fi
  fi

  # End-to-end signed commit simulation in disposable temporary repo.
  if command -v git >/dev/null 2>&1; then
    _tmp_dir="$(mktemp -d "$HOME/checkenv-sign.XXXXXX" 2>/dev/null || mktemp -d 2>/dev/null || true)"
    if [ -n "$_tmp_dir" ]; then
      (
        cd "$_tmp_dir" || exit 1
        git init -q >/dev/null 2>&1 || exit 2
        uname="$(git config --global --get user.name 2>/dev/null)"
        uemail="$(git config --global --get user.email 2>/dev/null)"
        [ -n "$uname" ] || git config user.name "checkEnv"
        [ -n "$uemail" ] || git config user.email "checkenv@local"
        [ -n "$signing_key" ] && git config user.signingkey "$signing_key"
        [ -n "$gpg_format" ] && git config gpg.format "$gpg_format"
        if [ -n "$gpg_program_resolved" ]; then
          git config gpg.ssh.program "$gpg_program_resolved"
        elif [ -n "$gpg_program" ]; then
          git config gpg.ssh.program "$gpg_program"
        fi
        [ "$commit_sign" = "true" ] && git config commit.gpgsign true
        printf 'checkenv %s\n' "$(date +%s)" > .checkenv
        git add .checkenv >/dev/null 2>&1 || exit 3
        if command -v timeout >/dev/null 2>&1; then
          if ! timeout 45 git commit -S -m "checkEnv signed commit" >/tmp/checkenv_commit.$$ 2>&1; then
            rc=$?
            [ "$rc" -eq 124 ] && exit 124
            exit 4
          fi
        else
          git commit -S -m "checkEnv signed commit" >/tmp/checkenv_commit.$$ 2>&1 || exit 4
        fi
        git log --show-signature -1 >/tmp/checkenv_sig.$$ 2>&1 || exit 5
        git cat-file -p HEAD >/tmp/checkenv_cat.$$ 2>&1 || exit 6
        exit 0
      )
      local commit_probe_rc=$?
      case $commit_probe_rc in
        0)
          if grep -Eq 'Good "git" signature|Good SSH signature' /tmp/checkenv_sig.$$ 2>/dev/null; then
            _add_result "success" "Signed commit test" "git commit -S e assinatura validada." ""
          elif grep -q '^gpgsig ' /tmp/checkenv_cat.$$ 2>/dev/null; then
            _add_result "success" "Signed commit test" "git commit -S gerou commit assinado (bloco gpgsig presente)." ""
          else
            if [ "$resolved_mode" = "automation" ]; then
              _add_result "fail" "Signed commit test" "Commit criado, mas sem evidencia de assinatura (gpgsig ausente)." "Revise a worktree tecnica, a ref da chave publica e a autorizacao do 1Password para a chave de automacao."
            else
              _add_result "fail" "Signed commit test" "Commit criado, mas sem evidencia de assinatura (gpgsig ausente)." "Revise gpg.ssh.program, user.signingkey e agent do 1Password."
            fi
          fi
          ;;
        124)
          if [ "$resolved_mode" = "automation" ]; then
            _add_result "fail" "Signed commit test" "git commit -S excedeu tempo limite (possivel prompt de aprovacao da chave tecnica no 1Password)." "Autorize o signer tecnico nesta sessao do terminal e rode checkEnv novamente."
          else
            _add_result "fail" "Signed commit test" "git commit -S excedeu tempo limite (possivel prompt de aprovacao do 1Password)." "Aprove o prompt de assinatura no 1Password e rode checkEnv novamente."
          fi
          ;;
        *)
          local commit_err=""
          commit_err="$(head -n1 /tmp/checkenv_commit.$$ 2>/dev/null | tr -d '\r')"
          if [ "$resolved_mode" = "automation" ]; then
            _add_result "fail" "Signed commit test" "git commit -S falhou em repositorio temporario (${commit_err:-sem detalhe})." "Corrija a worktree tecnica, a chave privada local e o gpg.ssh.program do signer tecnico."
          else
            _add_result "fail" "Signed commit test" "git commit -S falhou em repositorio temporario (${commit_err:-sem detalhe})." "Corrija gpg.ssh.program, user.signingkey e agent do 1Password."
          fi
          ;;
      esac
      rm -f /tmp/checkenv_commit.$$ /tmp/checkenv_sig.$$ /tmp/checkenv_cat.$$
      rm -rf "$_tmp_dir"
    else
      _add_result "fail" "Signed commit test" "Nao foi possivel criar diretorio temporario." "Verifique permissao de escrita em $HOME ou /tmp."
    fi
  fi

  [ -n "$git_probe_tmp" ] && rm -rf "$git_probe_tmp"

  # Aggregate and print final summary + remediation hints.
  local _ok=0 _fail=0 _inc=0
  for entry in "${_results[@]}"; do
    IFS='|' read -r status item detail <<<"$entry"
    _print_result "$status" "$item" "$detail"
    case "$status" in
      success) _ok=$((_ok + 1)) ;;
      fail) _fail=$((_fail + 1)) ;;
      *) _inc=$((_inc + 1)) ;;
    esac
  done

  echo
  printf 'Summary: success=%s fail=%s inconclusive=%s\n' "$_ok" "$_fail" "$_inc"

  if [ "${#_fixes[@]}" -gt 0 ]; then
    echo "Possible fixes:"
    for fix in "${_fixes[@]}"; do
      IFS='|' read -r item solution <<<"$fix"
      printf -- '- %s: %s\n' "$item" "$solution"
    done
  fi

  [ "$_fail" -eq 0 ]
}
