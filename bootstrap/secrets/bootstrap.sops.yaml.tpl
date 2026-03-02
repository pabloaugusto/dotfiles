# bootstrap/secrets/bootstrap.sops.yaml
#
# README rapido:
# - Este arquivo define regras de criptografia para segredos usados no bootstrap.
# - Chave privada local esperada: df/secrets/dotfiles.age.local.key
# - Gere a chave publica com:
#     age-keygen -y df/secrets/dotfiles.age.local.key
# - Use este arquivo com:
#     sops --config bootstrap/secrets/bootstrap.sops.yaml -e -i <arquivo>
#
# Exemplos de comando:
#   sops --config bootstrap/secrets/bootstrap.sops.yaml -e -i bootstrap/secrets/bootstrap.env
#   sops --config bootstrap/secrets/bootstrap.sops.yaml -d bootstrap/secrets/bootstrap.env
#
# IMPORTANTE:
# - Substitua "age1REPLACE_WITH_YOUR_PUBLIC_AGE_KEY" pela sua chave publica real.
# - Este arquivo pode ser versionado.
# - Nao versione segredos em texto puro.

creation_rules:
  # Segredos gerais do bootstrap (env/yaml/json/toml)
  - path_regex: ^bootstrap/secrets/.*\.(env|yaml|yml|json|toml)$
    age:
      - age1REPLACE_WITH_YOUR_PUBLIC_AGE_KEY
    encrypted_regex: '^(data|stringData|password|token|secret|private_key)$'

  # Exemplo para arquivos "sample" de secrets cifrados
  - path_regex: ^bootstrap/secrets/.*\.example\.sops\.(yaml|yml|json)$
    age:
      - age1REPLACE_WITH_YOUR_PUBLIC_AGE_KEY
