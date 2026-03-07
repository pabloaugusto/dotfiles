# Checklist

- O inventario de refs em [`df/secrets/secrets-ref.yaml`](../../../../df/secrets/secrets-ref.yaml)
  cobre todos os alvos da rotacao?
- A ordem de troca preserva a credencial antiga ate a nova ser validada?
- Existe suporte oficial real do provedor para a operacao desejada?
- A chave minima para rebootstrap continua recuperavel e documentada?
- O pos-rotacao atualiza runtime cifrado, refs derivadas, validacoes e notificacao?
