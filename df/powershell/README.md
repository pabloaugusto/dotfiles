---
title: PowerShell Profile Paths
subtitle: Shows the various PowerShell profile paths by platform and version.
author: Uzma Younas
date: September 13, 2023
source: https://adamtheautomator.com/powershell-profile-a-getting-started-guide/
snippet: https://jonlabelle.com/snippets/view/markdown/powershell-profile-paths
gist: https://gist.github.com/jonlabelle/f2a4fdd989dbfe59e444e0beaf07bcc9
notoc: false
---

## Windows PowerShell 5.1 (e.g. PowerShell Desktop)

| Profile                     | Path                                                                     |
| --------------------------- | ------------------------------------------------------------------------ |
| Current User - Current Host | `$Home\[My]Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1` |
| Current User - All Hosts    | `$Home\[My]Documents\WindowsPowerShell\Profile.ps1`                      |
| All Users - Current Host    | `$PSHOME\Microsoft.PowerShell_profile.ps1`                               |
| All Users - All Hosts       | `$PSHOME\Profile.ps1`                                                    |

## PowerShell 7.x (e.g. PowerShell Core)

### Windows

| Profile                     | Path                                                              |
| --------------------------- | ----------------------------------------------------------------- |
| Current User - Current Host | `$Home\[My]Documents\Powershell\Microsoft.Powershell_profile.ps1` |
| Current User - All Hosts    | `$Home\[My]Documents\Powershell\Profile.ps1`                      |
| All Users - Current Host    | `$PSHOME\Microsoft.Powershell_profile.ps1`                        |
| All Users - All Hosts       | `$PSHOME\Profile.ps1`                                             |

### Linux/macOS

| Profile                     | Path                                                                 |
| --------------------------- | -------------------------------------------------------------------- |
| Current User - Current Host | `~/.config/powershell/Microsoft.Powershell_profile.ps1`              |
| Current User - All Hosts    | `~/.config/powershell/profile.ps1`                                   |
| All Users - Current Host    | `/usr/local/microsoft/powershell/7/Microsoft.Powershell_profile.ps1` |
| All Users - All Hosts       | `/usr/local/microsoft/powershell/7/profile.ps1`                      |
