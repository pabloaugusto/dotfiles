#!/usr/bin/env bash
set -euo pipefail

# Smart sync workflow for dotfiles in Linux/WSL:
# - inspect local pending changes and ahead/behind status
# - optionally create grouped commits by context
# - optionally push local commits
# - keep sync through Git only (no direct file copy across environments)

_sync_repo_path() {
  if [[ -n "${DOTFILES:-}" ]]; then
    printf '%s\n' "$DOTFILES"
    return
  fi
  printf '%s/dotfiles\n' "$HOME"
}

_sync_prompt_yes_no() {
  local prompt="$1"
  local answer=""

  if [[ ! -t 0 ]]; then
    echo "${prompt} [y/N]: sessao nao interativa detectada -> padrao N"
    return 1
  fi

  read -r -p "${prompt} [y/N]: " answer
  answer="$(printf '%s' "$answer" | tr '[:upper:]' '[:lower:]')"
  case "$answer" in
    y|yes|s|sim) return 0 ;;
    *) return 1 ;;
  esac
}

_sync_context_for_path() {
  local path="$1"
  local normalized="${path//\\//}"

  case "$normalized" in
    .github/workflows/*) echo "ci" ;;
    .github/*) echo "automation" ;;
    bootstrap/*) echo "bootstrap" ;;
    df/powershell/*) echo "powershell" ;;
    df/bash/*) echo "bash" ;;
    df/zsh/*) echo "zsh" ;;
    df/git/*) echo "git" ;;
    df/ssh/*) echo "ssh" ;;
    docs/*|README.md|CONTEXT.md|SECURITY.md) echo "docs" ;;
    Taskfile.yml) echo "automation" ;;
    Dockerfile|docker/*) echo "docker" ;;
    *)
      if [[ "$normalized" == */* ]]; then
        echo "${normalized%%/*}"
      else
        echo "misc"
      fi
      ;;
  esac
}

_sync_collect_changed_files() {
  local repo="$1"
  local line=""
  local path=""

  while IFS= read -r line; do
    [[ -n "$line" ]] || continue
    path="${line:3}"
    if [[ "$path" == *" -> "* ]]; then
      path="${path##* -> }"
    fi
    [[ -n "$path" ]] && printf '%s\n' "$path"
  done < <(git -C "$repo" status --porcelain=v1)
}

SYNC_BRANCH=""
SYNC_UPSTREAM=""
SYNC_DIRTY=0
SYNC_AHEAD=0
SYNC_BEHIND=0

_sync_refresh_state() {
  local repo="$1"
  SYNC_BRANCH="$(git -C "$repo" rev-parse --abbrev-ref HEAD)"
  SYNC_UPSTREAM="$(git -C "$repo" rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null || true)"

  if [[ -n "$(git -C "$repo" status --porcelain=v1)" ]]; then
    SYNC_DIRTY=1
  else
    SYNC_DIRTY=0
  fi

  SYNC_AHEAD=0
  SYNC_BEHIND=0
  if [[ -n "$SYNC_UPSTREAM" ]]; then
    SYNC_AHEAD="$(git -C "$repo" rev-list --count "${SYNC_UPSTREAM}..HEAD")"
    SYNC_BEHIND="$(git -C "$repo" rev-list --count "HEAD..${SYNC_UPSTREAM}")"
  fi
}

_sync_commit_by_context() {
  local repo="$1"
  local -a changed_files=()
  local -a contexts=()
  local -a ordered=(
    automation ci bootstrap powershell bash zsh git ssh docs docker misc
  )
  local -a files_for_ctx=()
  local file=""
  local ctx=""
  local commit_msg=""
  local commits=0
  declare -A groups=()

  mapfile -t changed_files < <(_sync_collect_changed_files "$repo" | sort -u)
  if [[ "${#changed_files[@]}" -eq 0 ]]; then
    echo "Nenhuma alteracao local detectada para commits agrupados."
    return 0
  fi

  for file in "${changed_files[@]}"; do
    [[ -n "$file" ]] || continue
    ctx="$(_sync_context_for_path "$file")"
    if [[ -n "${groups[$ctx]:-}" ]]; then
      groups[$ctx]+=$'\n'"$file"
    else
      groups[$ctx]="$file"
    fi
  done

  for ctx in "${ordered[@]}"; do
    [[ -n "${groups[$ctx]:-}" ]] && contexts+=("$ctx")
  done
  for ctx in "${!groups[@]}"; do
    if [[ " ${contexts[*]} " != *" ${ctx} "* ]]; then
      contexts+=("$ctx")
    fi
  done

  for ctx in "${contexts[@]}"; do
    mapfile -t files_for_ctx < <(printf '%s\n' "${groups[$ctx]}" | awk 'NF' | sort -u)
    [[ "${#files_for_ctx[@]}" -gt 0 ]] || continue

    git -C "$repo" add -- "${files_for_ctx[@]}"
    if git -C "$repo" diff --cached --quiet; then
      continue
    fi

    commit_msg="chore(sync): ${ctx} updates"
    git -C "$repo" commit -m "$commit_msg"
    echo "- ${commit_msg}"
    commits=$((commits + 1))
  done

  echo "Grouped commits created: ${commits}"
}

_sync_push_current_branch() {
  local repo="$1"
  if [[ -z "$SYNC_UPSTREAM" ]]; then
    git -C "$repo" push --set-upstream origin "$SYNC_BRANCH"
  else
    git -C "$repo" push
  fi
}

_sync_print_decline_commit_suggestions() {
  echo "Nenhum commit/push automatico foi executado."
  echo "Sugestoes:"
  echo "1) Para atualizar do remoto preservando alteracoes locais: task sync:update-safe"
  echo "2) Para organizar commits manualmente: git add -p && git commit -m \"...\""
  echo "3) Para isolar trabalho em andamento: git switch -c wip/<tema>"
}

_sync_print_decline_push_suggestions() {
  echo "Nenhum push automatico foi executado."
  echo "Sugestoes:"
  echo "1) Continue localmente e rode task sync depois."
  echo "2) Valide antes de publicar: task ci:validate e task pr:validate."
  echo "3) Envie manualmente quando estiver pronto: git push"
}

_sync_ensure_git_signer_program() {
  local repo="$1"
  local effective=""
  local local_program=""
  local resolved=""
  local preferred=""

  effective="$(git -C "$repo" config --get gpg.ssh.program 2>/dev/null || true)"
  local_program="$(git -C "$repo" config --local --get gpg.ssh.program 2>/dev/null || true)"

  if [[ -n "$effective" ]]; then
    if [[ -x "$effective" ]]; then
      resolved="$effective"
    else
      resolved="$(type -P "${effective%%[[:space:]]*}" 2>/dev/null || true)"
    fi
  fi

  if [[ "$effective" =~ ^[A-Za-z]:\\ ]] || [[ "$effective" =~ ^\\\\ ]]; then
    if [[ -n "$local_program" ]]; then
      git -C "$repo" config --local --unset-all gpg.ssh.program >/dev/null 2>&1 || true
      local_program=""
    fi
    effective="$(git -C "$repo" config --get gpg.ssh.program 2>/dev/null || true)"
    resolved="$(type -P "${effective%%[[:space:]]*}" 2>/dev/null || true)"
  fi

  if [[ -z "$effective" || -z "$resolved" ]]; then
    if [[ -x "$HOME/.local/bin/op-ssh-sign" ]]; then
      preferred="$HOME/.local/bin/op-ssh-sign"
    elif command -v op-ssh-sign >/dev/null 2>&1; then
      preferred="op-ssh-sign"
    fi
    if [[ -n "$preferred" ]]; then
      git -C "$repo" config --global gpg.ssh.program "$preferred" >/dev/null 2>&1 || true
      effective="$(git -C "$repo" config --get gpg.ssh.program 2>/dev/null || true)"
      if [[ -x "$effective" ]]; then
        resolved="$effective"
      else
        resolved="$(type -P "${effective%%[[:space:]]*}" 2>/dev/null || true)"
      fi
    fi
  fi

  if [[ -z "$effective" || -z "$resolved" ]]; then
    echo "gpg.ssh.program nao resolvivel para este ambiente."
    return 1
  fi
}

_sync_ensure_repo() {
  local repo="$1"
  if [[ ! -d "$repo/.git" ]]; then
    echo "Dotfiles repository not found at: $repo"
    return 1
  fi
}

_dotfiles_update_core() {
  local repo="$1"
  local switch_main="${2:-0}"
  local safe="${3:-0}"
  local stashed=0
  local rc=0
  _sync_ensure_repo "$repo"

  if [[ "$safe" == "1" ]]; then
    if [[ -n "$(git -C "$repo" status --porcelain=v1)" ]]; then
      if ! git -C "$repo" stash push -u -m "wip-before-sync" >/dev/null; then
        echo "Falha ao criar stash para update-safe."
        return 1
      fi
      stashed=1
    fi
  fi

  if [[ "$switch_main" == "1" ]]; then
    if ! git -C "$repo" switch main >/dev/null; then
      rc=1
    fi
  fi

  if [[ "$rc" -eq 0 ]]; then
    if ! git -C "$repo" fetch --prune origin; then
      rc=1
    fi
  fi

  if [[ "$rc" -eq 0 ]]; then
    _sync_refresh_state "$repo"
    if [[ -z "$SYNC_UPSTREAM" ]]; then
      git -C "$repo" branch --set-upstream-to "origin/${SYNC_BRANCH}" "${SYNC_BRANCH}" >/dev/null 2>&1 || true
      _sync_refresh_state "$repo"
    fi

    if [[ -n "$SYNC_UPSTREAM" ]]; then
      if ! git -C "$repo" pull --rebase; then
        rc=1
      fi
    else
      echo "Aviso: branch '${SYNC_BRANCH}' sem upstream. Pull foi ignorado."
    fi
  fi

  if [[ "$safe" == "1" && "$stashed" == "1" ]]; then
    if ! git -C "$repo" stash pop >/dev/null 2>&1; then
      echo "Aviso: stash pop retornou erro. Verifique conflitos locais."
    fi
  fi

  if [[ "$rc" -ne 0 ]]; then
    return "$rc"
  fi

  git -C "$repo" status --short
  _sync_refresh_state "$repo"
}

dotfiles_update() {
  local repo="${1:-$(_sync_repo_path)}"
  _dotfiles_update_core "$repo" "1" "0"
}

dotfiles_update_safe() {
  local repo="${1:-$(_sync_repo_path)}"
  _dotfiles_update_core "$repo" "1" "1"
}

dotfiles_publish() {
  local repo="${1:-$(_sync_repo_path)}"
  local message="${2:-}"
  _sync_ensure_repo "$repo"

  if [[ -z "$message" ]]; then
    echo "publish requires commit message."
    return 1
  fi

  _sync_ensure_git_signer_program "$repo"
  dotfiles_update "$repo"

  git -C "$repo" add -A
  if git -C "$repo" diff --cached --quiet; then
    echo "Nenhuma alteracao staged para commit."
    git -C "$repo" status --short
    return 0
  fi

  git -C "$repo" commit -m "$message"
  _sync_refresh_state "$repo"
  _sync_push_current_branch "$repo"
  git -C "$repo" status --short
  _sync_refresh_state "$repo"
}

dotfiles_sync() {
  local repo="${1:-$(_sync_repo_path)}"

  _sync_ensure_repo "$repo"

  git -C "$repo" fetch --prune origin
  _sync_refresh_state "$repo"
  echo "Sync state: branch=${SYNC_BRANCH} dirty=${SYNC_DIRTY} ahead=${SYNC_AHEAD} behind=${SYNC_BEHIND}"

  if [[ "$SYNC_DIRTY" -eq 1 ]]; then
    if _sync_prompt_yes_no "Foram detectadas alteracoes locais nao commitadas. Commitar por contexto e publicar agora?"; then
      _sync_ensure_git_signer_program "$repo"
      _sync_commit_by_context "$repo"
      git -C "$repo" fetch --prune origin
      _sync_refresh_state "$repo"
    else
      _sync_print_decline_commit_suggestions
      return 0
    fi
  fi

  if [[ "$SYNC_BEHIND" -gt 0 ]]; then
    echo "Remoto com ${SYNC_BEHIND} commit(s) a frente. Executando fluxo repo:update..."
    _dotfiles_update_core "$repo" "0" "0"
  fi

  if [[ -z "$SYNC_UPSTREAM" ]]; then
    if _sync_prompt_yes_no "Branch '${SYNC_BRANCH}' nao possui upstream remoto. Publicar e configurar upstream agora?"; then
      _sync_push_current_branch "$repo"
      _sync_refresh_state "$repo"
    else
      echo "Nenhum push automatico foi executado."
      echo "Sugestoes:"
      echo "1) Quando quiser publicar: git push --set-upstream origin ${SYNC_BRANCH}"
      echo "2) Continue localmente e rode task sync depois."
      return 0
    fi
  elif [[ "$SYNC_AHEAD" -gt 0 ]]; then
    if _sync_prompt_yes_no "Foram detectados ${SYNC_AHEAD} commit(s) locais nao enviados. Fazer push agora?"; then
      _sync_push_current_branch "$repo"
      _sync_refresh_state "$repo"
    else
      _sync_print_decline_push_suggestions
      return 0
    fi
  fi

  if [[ "$SYNC_DIRTY" -eq 0 && "$SYNC_AHEAD" -eq 0 && "$SYNC_BEHIND" -eq 0 ]]; then
    echo "Sync OK: branch=${SYNC_BRANCH} limpa e alinhada com o remoto."
  else
    echo "Sync state after run: branch=${SYNC_BRANCH} dirty=${SYNC_DIRTY} ahead=${SYNC_AHEAD} behind=${SYNC_BEHIND}"
  fi
}

_sync_main() {
  local action="${1:-sync}"
  shift || true

  case "$action" in
    sync)
      dotfiles_sync "${1:-$(_sync_repo_path)}"
      ;;
    update)
      dotfiles_update "${1:-$(_sync_repo_path)}"
      ;;
    update-safe)
      dotfiles_update_safe "${1:-$(_sync_repo_path)}"
      ;;
    publish)
      dotfiles_publish "${2:-$(_sync_repo_path)}" "${1:-}"
      ;;
    *)
      echo "Usage: sync-smart.sh [sync|update|update-safe] [repo_path]"
      echo "   or: sync-smart.sh publish <message> [repo_path]"
      return 1
      ;;
  esac
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  _sync_main "$@"
fi
