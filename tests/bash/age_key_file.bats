#!/usr/bin/env bats
# BOOT-AGEFILE: a chave age vive apenas em arquivo 600; o ambiente recebe
# somente SOPS_AGE_KEY_FILE. Usa HOME temporario e chave gerada na hora.
# A unica fonte aceita e' a ref do 1Password (op read); SOPS_AGE_KEY do env
# e' descartado sem uso.

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

	# Stub de 'op': 'op read <ref>' entrega a chave gerada acima (a mesma cujo
	# recipient esta na fixture). Nunca ecoa a ref nem o valor.
	export AGE_STUB_KEY_FILE="$TMP_HOME/k"
	mkdir -p "$TMP_HOME/bin-ok" "$TMP_HOME/bin-fail"
	cat > "$TMP_HOME/bin-ok/op" <<'STUB'
#!/usr/bin/env bash
if [ "$1" = "read" ]; then
	cat "$AGE_STUB_KEY_FILE"
	exit 0
fi
exit 1
STUB
	chmod +x "$TMP_HOME/bin-ok/op"
	# Stub que falha: escreve o erro (com o conteudo da chave!) em stderr.
	cat > "$TMP_HOME/bin-fail/op" <<'STUB'
#!/usr/bin/env bash
echo "op: falha proposital ao ler a ref" >&2
cat "$AGE_STUB_KEY_FILE" >&2
exit 1
STUB
	chmod +x "$TMP_HOME/bin-fail/op"

	use_op_ok
	load_age_functions
}

teardown() {
	[ -n "$TMP_HOME" ] && rm -rf "$TMP_HOME"
}

use_op_ok() {
	export PATH="$TMP_HOME/bin-ok:$PATH"
}

use_op_fail() {
	export PATH="$TMP_HOME/bin-fail:$PATH"
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

@test "materializa a chave vinda do op read em arquivo 600 e exporta apenas SOPS_AGE_KEY_FILE" {
	export DOTFILES_AGE_KEY_REF="op://vault/item/age-key"
	# Sem 'run': o bats executa 'run' em subshell, e as mutacoes de ambiente
	# (export SOPS_AGE_KEY_FILE / unset SOPS_AGE_KEY) nao voltariam para ca.
	rc=0
	materializeAgeKeyFile || rc=$?
	[ "$rc" -eq 0 ]

	key_file="$XDG_CONFIG_HOME/sops/age/keys.txt"
	[ -f "$key_file" ]
	[ "$SOPS_AGE_KEY_FILE" = "$key_file" ]
	[ -z "${SOPS_AGE_KEY:-}" ]
	# O arquivo contem exatamente a chave entregue pelo op read.
	[ "$(tr -d '\r' < "$key_file")" = "$TEST_KEY" ]
	if [ "$PERM_SUPPORTED" = "1" ]; then
		[ "$(stat -c '%a' "$key_file")" = "600" ]
	fi
}

@test "SOPS_AGE_KEY herdado do env nao e' gravado no arquivo de chave" {
	# Decoy: chave distinta, valida, so' para provar que nao vaza para o arquivo.
	age-keygen -o "$TMP_HOME/decoy" >/dev/null 2>&1
	DECOY_KEY="$(tr -d '\r' < "$TMP_HOME/decoy")"
	[ -n "$DECOY_KEY" ]
	[ "$DECOY_KEY" != "$TEST_KEY" ]

	export SOPS_AGE_KEY="$DECOY_KEY"
	export DOTFILES_AGE_KEY_REF="op://vault/item/age-key"
	run materializeAgeKeyFile
	[ "$status" -eq 0 ]

	key_file="$XDG_CONFIG_HOME/sops/age/keys.txt"
	[ "$(tr -d '\r' < "$key_file")" = "$TEST_KEY" ]
	[[ "$output" != *"$DECOY_KEY"* ]]
	# Nenhuma linha do arquivo carrega a chave do env (compara so' a linha
	# secreta: as linhas de comentario do age-keygen podem coincidir entre chaves).
	DECOY_SECRET="$(grep -o 'AGE-SECRET-KEY-1[A-Z0-9]*' "$TMP_HOME/decoy" | head -n1)"
	[ -n "$DECOY_SECRET" ]
	! grep -qF "$DECOY_SECRET" "$key_file"
}

@test "SOPS_AGE_KEY_REF sem op:// falha sem ecoar o valor" {
	# Valor nao-ref: pode ser o proprio segredo; nao pode aparecer na saida.
	export DOTFILES_AGE_KEY_REF="AGE-SECRET-KEY-1NAOEOUMAREF"
	run materializeAgeKeyFile
	[ "$status" -ne 0 ]
	[[ "$output" != *"AGE-SECRET-KEY-1NAOEOUMAREF"* ]]
	[ ! -f "$XDG_CONFIG_HOME/sops/age/keys.txt" ]
}

@test "op read falhando nao ecoa o stderr do op nem a chave" {
	use_op_fail
	export DOTFILES_AGE_KEY_REF="op://vault/item/age-key"
	run materializeAgeKeyFile
	[ "$status" -ne 0 ]
	[[ "$output" != *"falha proposital ao ler a ref"* ]]
	[[ "$output" != *"$TEST_KEY"* ]]
	[[ "$output" != *"AGE-SECRET-KEY-1"* ]]
	# Nenhum arquivo parcial e' deixado para tras.
	[ ! -f "$XDG_CONFIG_HOME/sops/age/keys.txt" ]
}

@test "validateAgeKeyFile aceita o arquivo cuja chave casa com o recipient de referencia" {
	export DOTFILES_AGE_KEY_REF="op://vault/item/age-key"
	materializeAgeKeyFile
	run validateAgeKeyFile
	[ "$status" -eq 0 ]
}

@test "validateAgeKeyFile falha quando o recipient diverge, sem imprimir a chave" {
	export DOTFILES_AGE_KEY_REF="op://vault/item/age-key"
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
	export DOTFILES_AGE_KEY_REF="op://vault/item/age-key"
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
	export DOTFILES_AGE_KEY_REF="op://vault/item/age-key"
	printf 'export SOPS_AGE_KEY="AGE-SECRET-KEY-1RESIDUO"\n' > "$HOME/.bashrc"
	printf 'export SOPS_AGE_KEY="AGE-SECRET-KEY-1RESIDUO"\n' > "$HOME/.profile"

	persistSopsAgeEnv
	! grep -q '^export SOPS_AGE_KEY=' "$HOME/.bashrc"
	! grep -q '^export SOPS_AGE_KEY=' "$HOME/.profile"
}
