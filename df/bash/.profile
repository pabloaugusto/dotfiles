# personal profile
[ -n "$BASH" ] && [ -f ~/.bashrc ] && . ~/.bashrc

# uv
export PATH="$HOME/.local/bin:$PATH"

{ ble-edit/exec:gexec/.save-lastarg; } &>/dev/null
