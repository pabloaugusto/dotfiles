# PowerShell - Funções e padrões avançados

Referências rápidas para padrões usados em scripts do repositório.

## Padrões recomendados

- usar funções idempotentes
- validar pré-condições cedo (`Test-Path`, `Get-Command`)
- reportar erros com mensagens acionáveis
- manter operações críticas com efeito explícito (ex.: symlink, install, auth)

## Exemplo de countdown simples

```powershell
(10..0) | ForEach-Object { Start-Sleep -Seconds 1; $_ }
```

## Referências externas úteis

- <https://github.com/andrew-s-taylor/public/tree/main/IntuneConfig/Powershell>
- <https://kolbi.cz/blog/2017/10/25/setuserfta-userchoice-hash-defeated-set-file-type-associations-per-user/>
