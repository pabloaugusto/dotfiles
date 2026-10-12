#!/usr/bin/env bash

# Leitor YAML minimo (SSOT) para os arquivos de config do bootstrap.
# Compartilhado entre app/bootstrap/bootstrap-ubuntu-wsl.sh e check-env.sh:
# antes vivia duplicado dentro do bootstrap, e o check-env nao conseguia ler
# app/bootstrap/user-config.yaml (ex.: git.signing_key).
#
# Uso: _yaml_get <arquivo> <caminho.pontuado>
_yaml_get() {
	local file="$1"
	local target="$2"
	[ -f "$file" ] || return 0
	# POSIX awk apenas: `match(s, re, arr)` e extensao gawk; sob mawk (default do
	# Ubuntu) o parse falha e a funcao retornava vazio sem avisar.
	awk -v target="$target" '
		function trim(v) {
			sub(/^[[:space:]]+/, "", v)
			sub(/[[:space:]]+$/, "", v)
			return v
		}
		function leading_spaces(s,   n, c) {
			n = 0
			while (n < length(s)) {
				c = substr(s, n + 1, 1)
				if (c != " ") break
				n++
			}
			return n
		}
		/^[[:space:]]*#/ || /^[[:space:]]*$/ { next }
		{
			line = $0
			gsub(/\t/, "  ", line)
			indent = leading_spaces(line)
			rest = substr(line, indent + 1)
			colon = index(rest, ":")
			if (colon == 0) next
			key = substr(rest, 1, colon - 1)
			if (key !~ /^[A-Za-z0-9_-]+$/) next
			level = int(indent / 2)
			value = trim(substr(rest, colon + 1))
			path[level] = key
			for (i = level + 1; i < 20; i++) path[i] = ""
			if (value != "") {
				full = path[0]
				for (i = 1; i <= level; i++) full = full "." path[i]
				if (full == target) {
					gsub(/^"/, "", value); gsub(/"$/, "", value)
					gsub(/^'\''/, "", value); gsub(/'\''$/, "", value)
					print value
					exit
				}
			}
		}
	' "$file"
}
