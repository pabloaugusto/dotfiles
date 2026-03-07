# Matriz

## Camadas

- unit: logica pura, barata e deterministica
- integration: efeitos reais controlados por SO
- protected E2E: auth, secrets e runtime real
- local lab: reproducao manual e depuracao

## Regras por plataforma

- Linux: container-first
- Windows: runner real para integration
- Sandbox: laboratorio local no Windows

## Antipadroes

- depender de `D:` ou `%USERPROFILE%\\dotfiles` em testes
- usar auth real em PR barato
- confundir runner hospedado com ambiente E2E completo
- acoplar teste ao workstation pessoal
