#!/usr/bin/env bats
# BOOT-AGEFILE: a chave age vive apenas em arquivo 600; o ambiente recebe
# somente SOPS_AGE_KEY_FILE. Usa HOME temporario e chave gerada na hora.

setup() {
	REPO_ROOT="$(cd "$BATS_TEST_DIRNAME/../.." && pwd)"
	BOOTSTRAP="$REPO_ROOT/app/bootstrap/bootstrap-ubuntu-wsl.sh"

	TMP_HOME="$(mktemp -d)"
	export HOME="$TMP_HOME"
	export XDG_CONFIG_HOME="$TMP_HOME/.config"
	unset SOPS_AGE_KEY SOPS_AGE_KEY_FILE SOPS_AGE_KEY_REF DOTFILES_AGE_KEY_FILE

	age-keygen -o "$TMP_HOME/k" >/dev/null 2>&1
	[ -f "$TMP_HOME/k" ] || skip "age-keygen indisponivel"
	TEST_KEY="$(tr -d '\r' < "$TMP_HOME/k")"
	TEST_RECIPIENT="$(age-keygen -y "$TMP_HOME/k" 2>/dev/null | tr -d '\r\n')"

	# Fixture do arquivo de config do sops (contem apenas o recipient publico).
	echo "sops:" > "$TMP_HOME/dotfiles.sops.yaml"
	echo "  age: $TEST_RECIPIENT" >> "$TMP_HOME/dotfiles.sops.yaml"

	load_age_functions
}

teardown() {
	[ -n "$TMP_HOME" ] && rm -rf "$TMP_HOME"
}

# Extrai apenas as funcoes de chave age do bootstrap, sem executar o script.
load_age_functions() {
	eval "$(sed -n \
		-e '/^chmodSupportsPosix()/,/^}/p' \
		-e '/^ageKeyFilePath()/,/^}/p' \
		-e '/^ageKeyFileExpectedRecipient()/,/^}/p' \
		-e '/^materializeAgeKeyFile()/,/^}/p' \
		-e '/^validateAgeKeyFile()/,/^}/p' \
		-e '/^persistSopsAgeEnv()/,/^}/p' \
		"$BOOTSTRAP")"
	AGE_KEY_RECIPIENT_SOURCE="$TMP_HOME/dotfiles.sops.yaml"
	export AGE_KEY_RECIPIENT_SOURCE

	# chmod e no-op em MSYS/DrvFs; as assercoes de permissao so valem onde o
	# filesystem honra perms POSIX (Linux/WSL).
	PERM_SUPPORTED=0
	chmodSupportsPosix && PERM_SUPPORTED=1
	export PERM_SUPPORTED
}

@test "materializa a chave em arquivo 600 e exporta apenas SOPS_AGE_KEY_FILE" {
	export SOPS_AGE_KEY="$TEST_KEY"
	run materializeAgeKeyFile
	[ "$status" -eq 0 ]

	key_file="$XDG_CONFIG_HOME/sops/age/keys.txt"
	[ -f "$key_file" ]
	[ "$SOPS_AGE_KEY_FILE" = "$key_file" ]
	[ -z "${SOPS_AGE_KEY:-}" ]
	if [ "$PERM_SUPPORTED" = "1" ]; then
		[ "$(stat -c '%a' "$key_file")" = "600" ]
	fi
}

@test "validateAgeKeyFile aceita o arquivo cuja chave casa com o recipient de referencia" {
	export SOPS_AGE_KEY="$TEST_KEY"
	materializeAgeKeyFile
	run validateAgeKeyFile
	[ "$status" -eq 0 ]
}

@test "validateAgeKeyFile falha quando o recipient diverge, sem imprimir a chave" {
	export SOPS_AGE_KEY="$TEST_KEY"
	materializeAgeKeyFile

	# Referencia aponta para outro recipient (chave gerada na hora, distinta).
	age-keygen -o "$TMP_HOME/outra" >/dev/null 2>&1
	OUTRO_RECIPIENT="$(age-keygen -y "$TMP_HOME/outra" 2>/dev/null | tr -d '\r\n')"
	echo "sops:" > "$TMP_HOME/dotfiles.sops.yaml"
	echo "  age: $OUTRO_RECIPIENT" >> "$TMP_HOME/dotfiles.sops.yaml"

	run validateAgeKeyFile
	[ "$status" -ne 0 ]
	[[ "$output" != *"$TEST_KEY"* ]]
}

@test "persistSopsAgeEnv grava apenas o caminho no runtime.env" {
	export SOPS_AGE_KEY="$TEST_KEY"
	run persistSopsAgeEnv
	[ "$status" -eq 0 ]

	runtime_file="$HOME/.config/dotfiles/runtime.env"
	[ -f "$runtime_file" ]
	grep -q '^export SOPS_AGE_KEY_FILE=' "$runtime_file"
	# Nenhuma linha grava o conteudo da chave.
	! grep -q '^export SOPS_AGE_KEY=' "$runtime_file"
	! grep -q 'AGE-SECRET-KEY' "$runtime_file"
	if [ "$PERM_SUPPORTED" = "1" ]; then
		[ "$(stat -c '%a' "$runtime_file")" = "600" ]
	fi
}

@test "persistSopsAgeEnv remove residuo de SOPS_AGE_KEY de arquivos de startup" {
	export SOPS_AGE_KEY="$TEST_KEY"
	printf 'export SOPS_AGE_KEY="AGE-SECRET-KEY-1RESIDUO"\n' > "$HOME/.bashrc"
	printf 'export SOPS_AGE_KEY="AGE-SECRET-KEY-1RESIDUO"\n' > "$HOME/.profile"

	persistSopsAgeEnv
	! grep -q '^export SOPS_AGE_KEY=' "$HOME/.bashrc"
	! grep -q '^export SOPS_AGE_KEY=' "$HOME/.profile"
}
