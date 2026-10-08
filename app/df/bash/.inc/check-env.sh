#!/usr/bin/env bash

# Leitor YAML compartilhado (SSOT: app/df/bash/.inc/yaml-get.sh). Necessario para
# validar user.signingkey contra git.signing_key de app/bootstrap/user-config.yaml.
if ! command -v _yaml_get >/dev/null 2>&1; then
  _checkenv_inc_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
  # shellcheck source=yaml-get.sh
  [ -f "$_checkenv_inc_dir/yaml-get.sh" ] && source "$_checkenv_inc_dir/yaml-get.sh"
  # shellcheck source=signing-automation.sh
  [ -f "$_checkenv_inc_dir/signing-automation.sh" ] && source "$_checkenv_inc_dir/signing-automation.sh"
  unset _checkenv_inc_dir
fi

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
      success) tag="[OK]" ;;
      fail) tag="[FALHA]" ;;
      warning) tag="[AVISO]" ;;
      *) tag="[INCONCLUSIVO]" ;;
    esac
    printf '%s %s - %s\n' "$tag" "$item" "$detail"
  }

  # Prefixo de caminho que representa "binario fornecido pelo Windows": o WSL
  # monta os drives em /mnt/c, /mnt/d, ... e o PATH do Windows continua visivel
  # no Linux (appendWindowsPath padrao). Um comando exigido que so resolve para
  # /mnt/* existe apenas do lado Windows -- o bootstrap Linux nao o instalou.
  # Variavel para permitir teste com PATH simulado.
  local _windows_path_prefix="${DOTFILES_WINDOWS_PATH_PREFIX:-/mnt}"

  # Verifies command existence and appends check result.
  _expect_cmd() {
    local cmd="$1"
    local cmd_path=""
    if command -v "$cmd" >/dev/null 2>&1; then
      cmd_path="$(command -v "$cmd")"
      case "$cmd_path" in
        "$_windows_path_prefix"/*)
          _add_result "fail" "Command: $cmd" "instalado so no Windows ($cmd_path); bootstrap nao instalou no Linux." "Rode 'bash app/bootstrap/bootstrap-ubuntu-wsl.sh' (install_software) para instalar $cmd no Linux."
          return 1
          ;;
      esac
      _add_result "success" "Command: $cmd" "Disponivel em $cmd_path" ""
      return 0
    fi
    _add_result "fail" "Command: $cmd" "Nao encontrado no PATH." "Rode 'bash app/bootstrap/bootstrap-ubuntu-wsl.sh' (install_software) ou instale via brew e recarregue o shell."
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

  # Distinguishes a signer that only needs a HUMAN UNLOCK (agent without the key
  # listed / 1Password locked / agent refused the operation) from a REAL signing
  # error. Only the former may be downgraded to `warning`; everything else is
  # `fail`. $1 = captured ssh-keygen output.
  _sign_needs_unlock() {
    grep -qiE 'no private key found for public key|agent refused operation|refused operation|could not (find|open) key in agent|couldn.t (find|open) key in agent|communication with agent failed|agent_contains_key|keys? not found|no keys? (found|available)|sign_and_send_pubkey|permission denied \(publickey\)|needs? (to be )?unlock|is locked|passphrase' "$1" 2>/dev/null
  }

  echo "checkEnv: validating environment"

  # Resolve the repo root BEFORE any check that wants to read repo-relative
  # files (e.g. app/df/secrets/secrets-ref.yaml). Previously this was computed
  # further down, so every consumer above saw an empty $git_probe.
  if command -v git >/dev/null 2>&1; then
    git_probe="$(git rev-parse --show-toplevel 2>/dev/null || true)"
    if [ -z "$git_probe" ] || [ ! -d "$git_probe/.git" ]; then
      git_probe_tmp="$(mktemp -d "$HOME/checkenv-probe.XXXXXX")"
      git -C "$git_probe_tmp" init -q >/dev/null 2>&1 || true
      git_probe="$git_probe_tmp"
    fi
  fi

  # Base runtime commands expected by dotfiles bootstrap + auth flow.
  # Single source of truth per OS: mirrors the packages installed by
  # app/bootstrap/bootstrap-ubuntu-wsl.sh (install_software).
  # Sem node/npm/yarn/pnpm: o dotfiles nao usa Node e o bootstrap nao instala
  # esses gerenciadores no Linux.
  local _expected_cmds=(
    op gh git ssh sops age task uv oh-my-posh
    zsh fastfetch ansible terraform cloudflared direnv
    flux talosctl helm helmfile kubectl kustomize kubeconform
    sponge talhelper stern yq jq psql bats
    dos2unix atuin
  )
  for _cmd in "${_expected_cmds[@]}"; do
    _expect_cmd "$_cmd" >/dev/null
  done

  # 1Password session + reference readability checks.
  # Quando o shell nao tem sessao (correto: nao exportamos segredo), usamos o
  # token da service account `daneel` do arquivo 600 SO para esta sessao de
  # checagem e o removemos do ambiente antes do check de vazamento no final.
  local _op_token_from_file=0
  if command -v op >/dev/null 2>&1; then
    local op_ok=0
    if _run_with_timeout 8 op whoami >/dev/null 2>&1; then
      op_ok=1
    else
      local _token_file="" _sa_token_value=""
      if command -v dotfiles_automation_dir >/dev/null 2>&1; then
        _token_file="$(dotfiles_automation_dir)/op-sa.token"
      fi
      [ -n "$_token_file" ] || _token_file="$HOME/.config/tars/automation/op-sa.token"
      if [ -s "$_token_file" ]; then
        _sa_token_value="$(tr -d '\r\n' <"$_token_file")"
        if [ -n "$_sa_token_value" ]; then
          export OP_SERVICE_ACCOUNT_TOKEN="$_sa_token_value"
          _op_token_from_file=1
          if _run_with_timeout 8 op whoami >/dev/null 2>&1; then
            op_ok=1
          fi
        fi
        unset _sa_token_value
      fi
    fi

    if [ "$op_ok" -eq 1 ]; then
      _add_result "success" "1Password CLI session" "op whoami executou com sucesso." ""
    else
      _add_result "fail" "1Password CLI session" "op whoami falhou (inclusive apos 1 retry)." "Rode o bootstrap para materializar op-sa.token do daneel ou autentique o op com uma sessao valida."
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
        for ref in "op://secrets/dotfiles/github/token" "op://secrets/github/api/token"; do
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
      _add_result "fail" "GitHub CLI auth" "gh nao autenticado no host github.com." "Rode 'gh auth login --hostname github.com --git-protocol ssh --with-token' com token do 1Password (preferencial: op://secrets/dotfiles/github/token; fallback: op://secrets/github/api/token)."
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
    # $git_probe was already resolved above; only re-resolve if unavailable.
    if [ -z "$git_probe" ]; then
      git_probe="$(git rev-parse --show-toplevel 2>/dev/null || true)"
      if [ -z "$git_probe" ] || [ ! -d "$git_probe/.git" ]; then
        git_probe_tmp="$(mktemp -d "$HOME/checkenv-probe.XXXXXX")"
        git -C "$git_probe_tmp" init -q >/dev/null 2>&1 || true
        git_probe="$git_probe_tmp"
      fi
    fi

    gpg_format="$(git -C "$git_probe" config --get gpg.format 2>/dev/null)"
    commit_sign="$(git -C "$git_probe" config --get commit.gpgsign 2>/dev/null)"
    signing_key="$(git -C "$git_probe" config --get user.signingkey 2>/dev/null)"
    gpg_program="$(git -C "$git_probe" config --get gpg.ssh.program 2>/dev/null)"
    git_ssh_command="$(git -C "$git_probe" config --get core.sshCommand 2>/dev/null || true)"
    # Identidade de automacao: unica (`daneel`), materializada pelo bootstrap. A
    # chave efetiva vem do helper, nao de ref por worktree (desenho antigo).
    local worktree_mode
    local automation_private_key_path=""
    worktree_mode="$(git -C "$git_probe" config --worktree --get dotfiles.signing.mode 2>/dev/null || true)"
    if [ "$requested_mode" = "auto" ]; then
      if command -v dotfiles_resolve_signing_mode >/dev/null 2>&1; then
        # Ponto unico de resolucao: TARS_ACTOR=agent > env > worktree > human.
        resolved_mode="$(dotfiles_resolve_signing_mode "$git_probe")"
      elif [ "$worktree_mode" = "automation" ]; then
        resolved_mode="automation"
      else
        resolved_mode="human"
      fi
    else
      resolved_mode="$requested_mode"
    fi

    _add_result "success" "Git signing mode" "mode=$resolved_mode." ""

    # Modo automatizado: identidade UNICA `daneel`, materializada pelo bootstrap
    # a partir do 1Password. Exige chave presente, permissao 600 e assinatura de
    # um blob de teste com `ssh-keygen -Y sign`. Quando o override de env ainda
    # nao foi exportado (ex.: checkEnv fora do shell interativo), coerimos aqui
    # as variaveis usadas pelos checks abaixo para refletir a chave do daneel.
    local _auto_dir="" _auto_key="" _auto_pub=""
    if command -v dotfiles_automation_signing_key >/dev/null 2>&1; then
      _auto_key="$(dotfiles_automation_signing_key)"
    fi
    if command -v dotfiles_automation_dir >/dev/null 2>&1; then
      _auto_dir="$(dotfiles_automation_dir)"
    fi
    _auto_pub="${_auto_key}.pub"

    if [ "$resolved_mode" = "automation" ]; then
      local _auto_perms=""
      if [ -n "$_auto_key" ] && [ -f "$_auto_key" ]; then
        _auto_perms="$(stat -c '%a' "$_auto_key" 2>/dev/null || true)"
        if [ "$_auto_perms" = "600" ]; then
          _add_result "success" "Automation signing key file" "chave do daneel presente e 600." ""
        else
          _add_result "fail" "Automation signing key file" "chave do daneel com permissao '${_auto_perms:-?}' (esperado 600)." "Rode: chmod 600 $_auto_key"
        fi
      else
        _add_result "fail" "Automation signing key file" "chave do daneel ausente em ${_auto_key:-<path desconhecido>}." "Rode o bootstrap (ensureDaneelIdentity) com o item do 1Password criado."
      fi

      if [ -f "$_auto_pub" ] && command -v ssh-keygen >/dev/null 2>&1; then
        local _auto_tmp _auto_rc=0
        _auto_tmp="$(mktemp -d "$HOME/checkenv-auto.XXXXXX" 2>/dev/null || mktemp -d 2>/dev/null || true)"
        if [ -z "$_auto_tmp" ]; then
          _add_result "fail" "Automation signing probe" "sem diretorio temporario para o probe de assinatura." "Verifique permissao de escrita em $HOME ou /tmp."
        else
          printf 'checkenv automation %s\n' "$(date +%s)" >"$_auto_tmp/payload"
          SSH_ASKPASS_REQUIRE=never DISPLAY='' SSH_ASKPASS='' \
            _run_with_timeout 10 ssh-keygen -Y sign -n git -f "$_auto_pub" "$_auto_tmp/payload" \
            </dev/null >"$_auto_tmp/sign.out" 2>&1
          _auto_rc=$?
          if [ $_auto_rc -eq 0 ] && [ -f "$_auto_tmp/payload.sig" ]; then
            _add_result "success" "Automation signing probe" "ssh-keygen -Y sign assinou o blob de teste com a chave do daneel." ""
          else
            local _auto_err=""
            _auto_err="$(head -n1 "$_auto_tmp/sign.out" 2>/dev/null | tr -d '\r')"
            _add_result "fail" "Automation signing probe" "ssh-keygen -Y sign falhou (rc=$_auto_rc): ${_auto_err:-sem saida}." "Rode o bootstrap de novo para rematerializar a chave do 1Password."
          fi
          rm -rf "$_auto_tmp"
        fi
        # Mantem coerentes os checks genericos abaixo (format/signer/assinatura).
        signing_key="$_auto_pub"
        gpg_program="ssh-keygen"
      fi
    fi

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
    # Modo automation: a chave efetiva e' a publica do daneel, nao a humana da
    # config. Sem isto o check de SSOT abaixo compararia chaves diferentes.
    # user.signingkey guarda a PUBLICA (o ssh-keygen deriva a privada do mesmo
    # diretorio), entao e' ela que reportamos aqui.
    if [ "$resolved_mode" = "automation" ] && [ -n "${_auto_pub:-}" ] && [ "$signing_key" = "${_auto_pub:-}" ]; then
      has_automation_private_key=1
      automation_private_key_path="$_auto_pub"
    fi

    # SSOT da chave PUBLICA de assinatura: git.signing_key em user-config.yaml.
    # Nao vem de `op read` (chave publica nao e' segredo).
    local config_signing_key="" config_file=""
    if [ -n "$git_probe" ] && [ -f "$git_probe/app/bootstrap/user-config.yaml" ]; then
      config_file="$git_probe/app/bootstrap/user-config.yaml"
    fi
    if [ -n "$config_file" ] && command -v _yaml_get >/dev/null 2>&1; then
      config_signing_key="$(_yaml_get "$config_file" "git.signing_key")"
    fi

    if [ $has_automation_private_key -eq 1 ]; then
      _add_result "success" "Git signing key" "user.signingkey aponta para a chave PUBLICA do daneel: $automation_private_key_path (privada correspondente: ${automation_private_key_path%.pub})." ""
    elif [ -z "$config_signing_key" ]; then
      _add_result "warning" "Git signing key" "git.signing_key vazio na config: sem SSOT para validar user.signingkey." "Preencha 'git.signing_key' em app/bootstrap/user-config.yaml e rode o bootstrap/checkEnv novamente."
    elif [ -z "$signing_key" ]; then
      _add_result "fail" "Git signing key" "user.signingkey ausente (git.signing_key definido na config)." "Rode o bootstrap (configureGitSigningKey) ou 'git config --global user.signingkey \"<valor de git.signing_key>\"'."
    else
      local _cfg_key_norm _skey_norm
      _cfg_key_norm="$(printf '%s' "$config_signing_key" | awk 'NF {print; exit}' | tr -s '[:space:]' ' ' | sed 's/^ //; s/ $//')"
      _skey_norm="$(printf '%s' "$signing_key" | awk 'NF {print; exit}' | tr -s '[:space:]' ' ' | sed 's/^ //; s/ $//')"
      if [ "$_cfg_key_norm" = "$_skey_norm" ]; then
        _add_result "success" "Git signing key" "user.signingkey confere com git.signing_key da config." ""
      else
        _add_result "fail" "Git signing key" "user.signingkey difere de git.signing_key da config." "Sincronize com 'git config --global user.signingkey' usando o valor de 'git.signing_key' em app/bootstrap/user-config.yaml."
      fi
    fi

    # Identidade de automacao `daneel` (unica): token da service account em
    # arquivo 600 e allowed_signers materializado pelo bootstrap. Nada disso
    # depende de env: o valor nunca vive no ambiente.
    if [ "$resolved_mode" = "automation" ]; then
      local _sa_token="${_auto_dir:-}/op-sa.token"
      if command -v dotfiles_automation_dir >/dev/null 2>&1; then
        _sa_token="$(dotfiles_automation_dir)/op-sa.token"
      fi
      if [ -s "$_sa_token" ]; then
        local _sa_perms=""
        _sa_perms="$(stat -c '%a' "$_sa_token" 2>/dev/null || true)"
        if [ -z "$_sa_perms" ] || [ "$_sa_perms" = "600" ]; then
          _add_result "success" "Automation SA token file" "op-sa.token presente e nao vazio." ""
        else
          _add_result "fail" "Automation SA token file" "op-sa.token com permissao '${_sa_perms}' (esperado 600)." "Rode: chmod 600 $_sa_token"
        fi
      else
        _add_result "fail" "Automation SA token file" "op-sa.token ausente ou vazio em $_sa_token." "Rode o bootstrap (ensureDaneelIdentity) apos criar o item no 1Password."
      fi

      # Sempre resolvido pelo helper (SSOT do caminho): a variavel antiga
      # _auto_allowed_signers nunca era atribuida em lugar nenhum (codigo morto).
      local _allowed_signers=""
      if [ -z "$_allowed_signers" ] && command -v dotfiles_automation_allowed_signers >/dev/null 2>&1; then
        _allowed_signers="$(dotfiles_automation_allowed_signers)"
      fi
      if [ -n "$_allowed_signers" ] && [ -f "$_allowed_signers" ]; then
        _add_result "success" "allowed_signers file" "presente em $_allowed_signers." ""
      else
        _add_result "fail" "allowed_signers file" "allowed_signers ausente (${_allowed_signers:-<path desconhecido>})." "Rode o bootstrap (ensureDaneelIdentity) para materializar a ref do 1Password."
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

  # SOPS/age readiness. O conteudo da chave vive so em arquivo 600.
  if [ -n "${SOPS_AGE_KEY_FILE:-}" ] && [ -f "${SOPS_AGE_KEY_FILE}" ]; then
    _add_result "success" "SOPS age key file" "SOPS_AGE_KEY_FILE definido e arquivo existe." ""
  else
    _add_result "fail" "SOPS age key file" "Nenhum arquivo de chave age valido (SOPS_AGE_KEY_FILE)." "Configure SOPS_AGE_KEY_FILE apontando para o arquivo 600 da chave (ex.: ~/.config/sops/age/keys.txt)."
  fi

  # Encerra a sessao emprestada do token do daneel antes de medir vazamento.
  if [ "${_op_token_from_file:-0}" = "1" ]; then
    unset OP_SERVICE_ACCOUNT_TOKEN
  fi

  # Vazamento: NENHUM segredo deve viver no ambiente (so NOMES na mensagem). O
  # shell nao exporta token de service account nem token do GitHub: o 1Password e'
  # lido por arquivo/ref e o `gh` usa a sessao propria do `gh auth`.
  local _leaked_vars=""
  local _leak_var=""
  for _leak_var in OP_SERVICE_ACCOUNT_TOKEN OP_CONNECT_HOST OP_CONNECT_TOKEN GH_TOKEN GITHUB_TOKEN SOPS_AGE_KEY; do
    if [ -n "${!_leak_var:-}" ]; then
      _leaked_vars="${_leaked_vars:+$_leaked_vars, }$_leak_var"
    fi
  done
  if [ -n "$_leaked_vars" ]; then
    _add_result "fail" "Secrets leaked in env" "variaveis de segredo presentes no ambiente: $_leaked_vars." "Remova-as do shell/perfil (o shell nao deve exportar segredo) e rode checkEnv novamente."
  else
    _add_result "success" "Secrets leaked in env" "nenhum token/chave de segredo no ambiente." ""
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

  # Signature availability probe. NEVER run a real `git commit -S` here: with
  # the 1Password signer that blocks on a biometric prompt. Instead probe with
  # `ssh-keygen -Y sign`, which goes through ssh-agent and fails fast (no tty,
  # no askpass) when the key needs an unlock.
  #
  # Gate (nao rebaixar): `warning` SO quando o agente exige desbloqueio humano
  # (agente sem chaves listadas / 1Password bloqueado) ou timeout por prompt de
  # aprovacao -- sempre com o detalhe "requer desbloqueio" e o comando para
  # validar. Signer nao configurado/irresolvivel, chave publica ilegivel, erro
  # real de assinatura e ausencia de tmpdir sao `fail`.
  if [ -z "$signing_key" ]; then
    _add_result "fail" "Signature verification" "signer nao configurado: user.signingkey ausente, assinatura nao verificada." "Defina 'git config --global user.signingkey \"ssh-ed25519 ...\"' e rode checkEnv novamente."
  elif ! command -v ssh-keygen >/dev/null 2>&1; then
    _add_result "fail" "Signature verification" "signer irresolvivel: ssh-keygen nao encontrado no PATH, assinatura nao verificada." "Instale OpenSSH (ssh-keygen) e rode checkEnv novamente."
  else
    _tmp_dir="$(mktemp -d "$HOME/checkenv-sign.XXXXXX" 2>/dev/null || mktemp -d 2>/dev/null || true)"
    if [ -z "$_tmp_dir" ]; then
      _add_result "fail" "Signature verification" "sem diretorio temporario para o probe de assinatura." "Verifique permissao de escrita em $HOME ou /tmp."
    else
      local sign_pubkey="" sign_rc=0
      if [ -f "$signing_key" ]; then
        sign_pubkey="$signing_key"
      elif [ -f "$signing_key.pub" ]; then
        sign_pubkey="$signing_key.pub"
      elif printf '%s' "$signing_key" | grep -q '^ssh-'; then
        # Inline public key in user.signingkey: materialize it for the probe.
        printf '%s\n' "$signing_key" >"$_tmp_dir/signing.pub"
        sign_pubkey="$_tmp_dir/signing.pub"
      fi

      if [ -z "$sign_pubkey" ]; then
        _add_result "fail" "Signature verification" "chave publica ilegivel: user.signingkey nao aponta para chave publica legivel nem para um valor ssh-ed25519 (valor: $signing_key)." "Ajuste user.signingkey para o caminho da chave publica ou o proprio valor ssh-ed25519 ..."
      else
        local _probe_cmd="ssh-keygen -Y sign -n git -f '$signing_key' <arquivo>"
        printf 'checkenv %s\n' "$(date +%s)" >"$_tmp_dir/payload"
        # stdin fechado + SSH_ASKPASS_REQUIRE=never => nunca abre prompt de biometria.
        SSH_ASKPASS_REQUIRE=never DISPLAY='' SSH_ASKPASS='' \
          _run_with_timeout 10 ssh-keygen -Y sign -n git -f "$sign_pubkey" "$_tmp_dir/payload" \
          </dev/null >"$_tmp_dir/sign.out" 2>&1
        sign_rc=$?
        if [ $sign_rc -eq 0 ] && [ -f "$_tmp_dir/payload.sig" ]; then
          _add_result "success" "Signature verification" "ssh-keygen -Y sign concluiu sem prompt; o agent assinou com a chave configurada." ""
        else
          local _sign_err=""
          _sign_err="$(head -n1 "$_tmp_dir/sign.out" 2>/dev/null | tr -d '\r')"
          _sign_err="${_sign_err:-ssh-keygen -Y sign falhou (rc=$sign_rc)}"
          if [ $sign_rc -eq 124 ] || _sign_needs_unlock "$_tmp_dir/sign.out"; then
            _add_result "warning" "Signature verification" "assinatura nao verificada (requer desbloqueio): $_sign_err | valide com: $_probe_cmd" "Desbloqueie a chave no agent/1Password e rode checkEnv novamente."
          else
            _add_result "fail" "Signature verification" "erro real de assinatura: $_sign_err" "Corrija gpg.format/gpg.ssh.program/user.signingkey e rode checkEnv novamente."
          fi
        fi
      fi
      rm -rf "$_tmp_dir"
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
  # Final table: one row per item, OK/FALHA/AVISO.
  printf '%-14s | %-44s | %s\n' "RESULTADO" "ITEM" "DETALHE"
  printf '%s\n' "---------------+----------------------------------------------+--------------------------------"
  for entry in "${_results[@]}"; do
    IFS='|' read -r status item detail <<<"$entry"
    local _row_tag=""
    case "$status" in
      success) _row_tag="OK" ;;
      fail) _row_tag="FALHA" ;;
      *) _row_tag="AVISO" ;;
    esac
    printf '%-14s | %-44s | %s\n' "$_row_tag" "$item" "$detail"
  done
  printf '%s\n' "---------------+----------------------------------------------+--------------------------------"
  printf 'Summary: ok=%s falha=%s aviso=%s\n' "$_ok" "$_fail" "$_inc"

  if [ "${#_fixes[@]}" -gt 0 ]; then
    echo "Possible fixes:"
    for fix in "${_fixes[@]}"; do
      IFS='|' read -r item solution <<<"$fix"
      printf -- '- %s: %s\n' "$item" "$solution"
    done
  fi

  [ "$_fail" -eq 0 ]
}
