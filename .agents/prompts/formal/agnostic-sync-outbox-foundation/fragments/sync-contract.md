# Fragmento - Contrato De Sync

<!-- cspell:words obrigatorio duravel -->

Fluxo obrigatorio:

1. gravar no outbox local duravel
2. tentar publicar no destino remoto
3. aguardar `ack` remoto explicito
4. so depois marcar como sincronizado
5. compactar ou podar conforme a retention policy

## Regra critica

- nenhum evento pode ser removido antes da confirmacao remota
