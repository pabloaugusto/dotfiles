# Slack - Notas rápidas

## Referências

- <https://posts.specterops.io/abusing-slack-for-offensive-operations-2343237b9282>
- <https://gist.github.com/sdurandeu/5190b8c3ac0459e291abbb2e6aa3cc55>

## Local de configuração

- Windows: `%APPDATA%\Slack`
- macOS: `~/Library/Application Support/Slack/`
- macOS (sandbox): `~/Library/Containers/com.tinyspeck.slackmacgap/Data/Library/Application Support/Slack`

## Auto join (primeiro login)

Arquivo:

```text
%APPDATA%/Slack/Signin.slacktoken
```

Conteúdo:

```json
{"default_signin_team":["YOUR_TEAM_ID"]}
```

## Backup de contas logadas

- `Slack/storage/slack-workspaces`
- `Slack/Cookies`
