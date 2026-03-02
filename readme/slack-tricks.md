
# Slack tricks

### Reference

- <https://posts.specterops.io/abusing-slack-for-offensive-operations-2343237b9282>
- https://gist.github.com/sdurandeu/5190b8c3ac0459e291abbb2e6aa3cc55
- 

## Slack config storage folder

- %AppData%\Roaming\Slack (Windows)
- ~/Library/Application Support/Slack/ (macOS)
- ~/Library/Containers/com.tinyspeck.slackmacgap/Data/Library/Application Support/Slack (macOS)

## Auto joing a team (first login)

Create the file

```powershell
%APPDATA%/Slack/Signin.slacktoken
```

With the following content

```json
{"default_signin_team":["YOUR_TEAM_ID"]} //your-workspace.slack.com
```

## Backup slack logged accounts

```path
- Slack/storage/slack-workspaces
- Slack/Cookies
```


