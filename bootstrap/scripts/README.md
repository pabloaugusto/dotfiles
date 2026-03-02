# Instalaçao de ambiente Windows

Utilização do chocolatey e do boxtarter para instalar tudo necessário após a instalação do windows

## Arquivos de configuração e profiles

### PowerShell

#### [PowerShell Config](<(https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_powershell_config)>)

Create / Edit the `powershell.config.json` at one of this directories:

- User level: `Split-Path $PROFILE.CurrentUserCurrentHost`
- All users level: `$PSHOME`

#### [PowerShell Profiles](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_profiles#profile-types-and-locations)

Create / Edit the profile file at one of this directories:

- **Current user, Current Host** `$PROFILE.CurrentUserCurrentHost`
- Current User, All Hosts `$PROFILE.CurrentUserAllHosts`
- All Users, Current Host `$PROFILE.AllUsersCurrentHost`
- All Users, All Hosts `$PROFILE.AllUsersAllHosts`

## PowerShell Tips

Some useful powershell tips

### PATH and ENV Vars

Usefull tips for env vars and paths

```powershell
<# Get My Documents path #>
[Environment]::GetFolderPath([Environment+SpecialFolder]::MyDocuments)
[Environment]::GetFolderPath("mydocuments")
```

```powershell
<# Print PATH env var #>
[Environment]::GetEnvironmentVariable("Path")
```
