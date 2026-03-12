################################################################################
# app/bootstrap/software-list.ps1
#
# Canonical catalog of software used by Windows bootstrap.
# Each entry is a hashtable with:
# - installer: installer backend expected by _functions.ps1
# - id: package identifier in that backend
# - name: human-friendly package label shown in logs
# - bootstrap: when "true", package is eligible for bootstrap runs
# - url: optional project/source reference
#
# Important operational notes:
# - This list is intentionally broad (full workstation profile).
# - app/bootstrap/bootstrap-windows.ps1 can still skip groups depending on mode.
# - Keep package ids stable; installer helpers cache and compare by id/name.
################################################################################

$softwareList = @(

	####################################################
	# Onedrive (base to dotfile configs)
	####################################################
	@{installer = 'winget'; id = 'Microsoft.OneDrive'; name = 'OneDrive'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'SyncTrayzor.SyncTrayzor'; name = 'SyncTrayzor'; bootstrap = 'true'; url='' }


	####################################################
	# Windows Terminal & Powershell Core
	####################################################
	@{installer = 'winget'; id = 'Microsoft.WindowsTerminal'; name = 'Windows Terminal'; bootstrap = 'true'; url='' }
	#@{installer = 'winget'; id = 'Microsoft.WindowsTerminal.Preview'; name = 'WindowsTerminal Preview'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'Microsoft.PowerShell'; name = 'PowerShell'; bootstrap = 'true'; url='' }
	#@{installer = 'winget'; id = 'Microsoft.PowerShell.Preview'; name = 'PowerShell Preview'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'JanDeDobbeleer.OhMyPosh'; name = 'OhMyPosh'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'gerardog.gsudo'; name = 'GSudo'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'SourceFoundry.HackFonts'; name = 'Nerd Fonts'; bootstrap = 'true'; url='' }
	@{installer = 'choco'; id = 'nerd-fonts-hack'; name = 'Nerd Fonts: Hack'; bootstrap = 'true'; url='' }


	####################################################
	# Powershell Modules
	####################################################
	@{installer = 'powershell-module'; id = 'PowerShellGet'; name = 'PowerShellGet'; bootstrap = 'true' ; url = 'https://www.powershellgallery.com/packages/PowerShellGet/' }
	@{installer = 'powershell-module'; id = 'PSReadLine'; name = 'PSReadLine'; bootstrap = 'true' ; url = '' }
	@{installer = 'powershell-module'; id = 'oh-my-posh'; name = 'Oh My Posh'; bootstrap = 'true' ; url = '' }
	@{installer = 'powershell-module'; id = 'Terminal-Icons'; name = 'Terminal-Icons'; bootstrap = 'true' ; url = '' }
	@{installer = 'powershell-module'; id = 'posh-docker'; name = 'posh-docker'; bootstrap = 'true' ; url = '' }
	@{installer = 'powershell-module'; id = 'posh-git'; name = 'posh-git'; bootstrap = 'true' ; url = '' }
	@{installer = 'powershell-module'; id = 'PowerType'; name = 'PowerType'; bootstrap = 'true' ; url = '' }
	@{installer = 'powershell-module'; id = 'WslInterop'; name = 'WslInterop'; bootstrap = 'true' ; url = 'https://github.com/mikebattista/PowerShell-WSL-Interop' }
	@{installer = 'powershell-module'; id = 'Get-ChildItemColor'; name = 'Get-ChildItemColor'; bootstrap = 'true' ; url = 'https://github.com/joonro/Get-ChildItemColor' }
	@{installer = 'powershell-module'; id = 'PSScriptAnalyzer'; name = 'PSScriptAnalyzer'; bootstrap = 'true' ; url = '' }
	@{installer = 'powershell-module'; id = 'CredentialManager'; name = 'CredentialManager'; bootstrap = 'true' ; url = 'https://github.com/echalone/PowerShell_Credential_Manager' }
	@{installer = 'powershell-module'; id = 'PSWindowsUpdate'; name = 'PSWindowsUpdate'; bootstrap = 'true' ; url = 'https://www.powershellgallery.com/packages/PSWindowsUpdate/2.2.1.3' }
	@{installer = 'powershell-module'; id = 'Pscx'; name = 'Pscx'; bootstrap = 'true' ; url = '#https://github.com/Pscx/Pscx' }
	@{installer = 'powershell-module'; id = 'WinGet-Essentials'; name = 'WinGet-Essentials'; bootstrap = 'true' ; url = 'https://github.com/jjcarrier/PS-WinGet-Essentials' }
	@{installer = 'powershell-module'; id = 'winfetch'; name = 'winfetch'; bootstrap = 'true' ; url = '' }



	####################################################
	# Windows Pkg Installers & Modules
	####################################################
	@{installer = 'winget'; id = 'MartiCliment.UniGetUI'; name = 'UniGetUI'; bootstrap = 'true'; url='' } #old WingetUi Store
	@{installer = 'choco';	id = 'chocolatey-core.extension'; name = ''; bootstrap = 'true'; url='' }
	@{installer = 'choco';	id = 'chocolatey-windowsupdate.extension'; name = ''; bootstrap = 'true'; url='' }
	@{installer = 'choco'; id = 'choco-cleaner'; name = ''; bootstrap = 'true'; url='' }


	####################################################
	# WSL & Modules
	####################################################
	@{installer = 'winget'; id = 'Bostrot.WSLManager'; name = 'WSLManager'; bootstrap = 'true'; url='https://github.com/bostrot/wsl2-distro-manager/' }
	@{installer = 'winget'; id = 'Canonical.Ubuntu.2204'; name = 'WSL Ubuntu'; bootstrap = 'true'; url='' }


	####################################################
	# Development Tools
	####################################################
	@{installer = 'winget'; id = 'GLab.GLab'; name = 'GitLab cli'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'Git.Git'; name = 'Git'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'GitHub.cli'; name = 'GitHub cli'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'GitTools.GitVersion'; name = 'GitVersion'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'GitHub.GitHubDesktop'; name = 'GitHub Desktop'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'Microsoft.VisualStudioCode'; name = 'VsCode'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'Docker.DockerCLI'; name = 'Docker cli'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'Docker.DockerCompose'; name = 'Docker Compose'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'Docker.DockerDesktop'; name = 'Docker Desktop'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'Postman.Postman'; name = 'Postman'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'Insomnia.Insomnia'; name = 'Insomnia'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'OpenJS.NodeJS'; name = 'NodeJS'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'nektos.act'; name = 'GitHub Actions Local'; bootstrap = 'true'; url='https://github.com/nektos/act' }
	@{installer = 'winget'; id = 'Figma.Figma'; name = 'Figma'; bootstrap = 'true'; url='' }
	# @{installer = 'winget'; id = 'dbeaver.dbeaver'; name = 'Dbeaver'; bootstrap = 'true'; url='' } # install not found anymore, moved to choco install
	@{installer = 'winget'; id = 'CoreyButler.NVMforWindows'; name = 'nvm'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'Python.Python.3.12'; name = 'python 3.12'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'direnv.direnv'; name = 'direnv'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'Cloudflare.cloudflared'; name = 'cloudflared'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'FiloSottile.age'; name = 'age'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'Mozilla.SOPS'; name = 'sops'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'Hashicorp.Terraform'; name = 'terraform'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'Kubernetes.kubectl'; name = 'kubectl'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'Kubernetes.kustomize'; name = 'kustomize'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'YannHamon.kubeconform'; name = 'kubeconform'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'MikeFarah.yq'; name = 'yq'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'jqlang.jq'; name = 'jq'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'FluxCD.Flux'; name = 'flux'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'Helm.Helm'; name = 'helm'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'Task.Task'; name = 'go-task'; bootstrap = 'true'; url='https://taskfile.dev' }
	@{installer = 'winget'; id = 'Mirantis.Lens'; name = 'K8s Lens'; bootstrap = 'true'; url='https://k8slens.dev/' }
	@{installer = 'pip'; id = 'uv'; name = 'uv'; bootstrap = 'true'; url='PIP alternative, much faster' } # pip package manager alternative - way faster and performatic
	@{installer = 'pip'; id = 'ansible'; name = 'ansible'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'albertony.npiperelay'; name = 'npiperelay'; bootstrap = 'true'; url='https://github.com/albertony/npiperelay' }
	@{installer = 'winget'; id = 'Firejox.WinSocat'; name = 'WinSocat'; bootstrap = 'true'; url='https://github.com/Firejox/winsocat' }
	@{installer = 'choco'; id = 'pgsql'; name = 'postgre cli'; bootstrap = 'true'; url='' }
	@{installer = 'choco'; id = 'dbeaver'; name = 'dbeaver'; bootstrap = 'true'; url='' }



	# Yarn.Yarn

	# 'git',
	# 'gh', #github CLI
	# 'vscode',
	# 'visualstudio2022community'
	# 'notepadplusplus.install',
	# 'ngrok'
	# 'fiddler',
	# 'rapidee', #windows env vars editor
	# 'python',
	# 'php',
	# 'snoop', #windows wpf spy as tree (inspect/debug web browser render and actions as tree)
	# 'postman',
	# #'yarn',
	# #'docker-desktop',
	# #'terraform',
	# #'kubernetes-helm',
	# #'kubernetes-cli',
	# #'azure-cli',
	# #'tortoisegit',
	# #'filezilla',
	# #'nodejs',
	# #'winmerge',
	# #'graphviz', #needed for Terraform visualizer and VS Code Graphviz preview


	####################################################
	# Communication
	####################################################
	@{installer = 'winget'; id = 'SlackTechnologies.Slack'; name = 'Slack'; bootstrap = 'true'; url='' }
	#@{installer = 'winget'; id = '9NKSQGP7F2NH'; name = 'WhatsApp'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = '9NBDXK71NK08'; name = 'WhatsApp Beta'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'Zoom.Zoom'; name = 'Zoom'; bootstrap = 'true'; url='' }
	#@{installer = 'winget'; id = 'Microsoft.Skype'; name = 'Skype'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'Microsoft.Teams'; name = 'Microsoft Teams'; bootstrap = 'true'; url='' }
	@{installer = 'choco'; id = '9WZDNCRF0083'; name = 'Facebook Messenger'; bootstrap = 'true'; url='' }


	####################################################
	# Email CLients
	####################################################
	#@{installer = 'winget'; id = 'Mailbird.Mailbird'; name = 'Mailbird'; bootstrap = 'true'; url='' }
	#@{installer = 'winget'; id = 'Readdle.Spark'; name = 'Spark Mail'; bootstrap = 'true'; url='' }
	#@{installer = 'winget'; id = 'Betterbird.Betterbird' }


	####################################################
	# Power User
	####################################################
	@{installer = 'winget'; id = 'Microsoft.PowerToys'; name = 'PowerToys'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = '9P7KNL5RWT25'; name = 'SysInternals Suite'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'IObit.IObitUnlocker'; name = 'IObitUnlocker'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'AutoHotkey.AutoHotkey'; name = 'AutoHotkey'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'TeamViewer.TeamViewer'; name = 'TeamViewer'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'Rufus.Rufus'; name = 'Rufus'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'Balena.Etcher'; name = 'etcher'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'voidtools.Everything'; name = 'Everything'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'Famatech.AdvancedIPScanner'; name = 'Advanced IP Scanner'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'Piriform.Recuva'; name = 'Recuvau'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = '9PC7BZZ28G0X'; name = 'Custom Context Menus'; bootstrap = 'true'; url='https://github.com/ikas-mc/ContextMenuForWindows11' }
	@{installer = 'winget'; id = 'Rclone.Rclone'; name = 'RClone'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'WinFsp.WinFsp'; name = 'winfsp'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'CrystalDewWorld.CrystalDiskInfo'; name = 'CristalDisk Info'; bootstrap = 'true'; url='' }


	# choco install cpu-z
	# choco install hwmonitor
	# choco install gpu-z
	# choco install pci-z

	# 'coretemp',
	# 'cpu-z',
	# 'crystaldiskmark',
	# 'crystaldiskinfo',
	# 'everything',
	# 'winscp',
	# 'putty.install',
	# 'sysinternals',
	# #	'teamviewer',
	# #	'typora',
	# #	'microsoft-windows-terminal',
	# #	'wireguard',
	# #	'wireshark',


	####################################################
	# Security
	####################################################
	# @{installer = 'winget'; id = 'Twilio.Authy'; name = 'Authy'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'Microsoft.OpenSSH.Preview '; name = 'OpenSSH'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'AgileBits.1Password'; name = '1Password'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'AgileBits.1Password.CLI'; name = '1Password CLI'; bootstrap = 'true'; url='' }

	# @{installer = 'winget'; id = 'NordSecurity.NordVPN'; name = 'NordVPN'; bootstrap = 'true'; url='' }


	####################################################
	# Productivity
	####################################################
	@{installer = 'winget'; id = 'Microsoft.Office'; name = 'Office 365'; bootstrap = 'true'; url='' }
	# @{installer = 'winget'; id = 'Tableau.Reader'; name = 'Tableau'; bootstrap = 'true'; url='' }
	# @{installer = 'winget'; id = 'Rambox.Rambox'; name = 'Rambox'; bootstrap = 'true'; url='# AIO Chat Client / PWA Container' }


	####################################################
	# Utils
	####################################################
	@{installer = 'winget'; id = 'Foxit.FoxitReader'; name = 'FoxitReader'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'qBittorrent.qBittorrent'; name = 'qBittorrent'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = '7zip.7zip'; name = '7zip'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'RARLab.WinRAR'; name = 'WinRAR'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'CodeSector.TeraCopy'; name = 'TeraCopy'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'aria2.aria2'; name = 'Aria2'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'AngusJohnson.ResourceHacker'; name = 'Resource Hacker'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'BotProductions.IconViewer'; name = 'Icon Viewer'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'Skillbrains.Lightshot'; name = 'Icon Viewer'; bootstrap = 'true'; url='' }



	# 	#'lightshot.install',
	# #'qbittorrent',
	# #'screentogif',
	# #'vlc',
	# 'jre8',
	# #'7zip',
	# 'clipdiary',
	# 'spotube',
	# 'puretext',
	# #	'winrar',
	# #	'greenshot',
	# #	'irfanview',


	####################################################
	# Audio & Video & Stream
	####################################################
	@{installer = 'winget'; id = 'CodecGuide.K-LiteCodecPack.Standard'; name = 'K-Lite'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'VideoLAN.VLC'; name = 'VLC'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'OBSProject.OBSStudio'; name = 'OBSStudio'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'Genymobile.scrcpy'; name = 'ScrCpy'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'Audacity.Audacity'; name = 'Audacity'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'youtube-dl.youtube-dl'; name = 'Youtube Download cli'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'Gyan.FFmpeg'; name = 'FFmpeg'; bootstrap = 'true'; url='' }
	@{installer = 'choco'; id = 'nvidia-broadcast'; name = 'Nvidia broadcast'; bootstrap = 'true'; url='' } #nvidia broadcast actually can't be installed by winget
	@{installer = 'choco'; id = 'touchportal'; name = 'Touch Portal'; bootstrap = 'true'; url='' } #touchportal  actually can't be installed by winget

	# 'obs-studio',
	# 'voicemeeter.install',
	# 'voicemeeter',
	# 'voicemeeter-banana',
	# 'voicemeeter-potato',
	# 'vb-cable',
	# 'scrcpy',	#mobile screen share
	# 'adb', #driver iser by scrcpy
	# 'ffmpeg',
	# 'youtube-dl',
	# 'touchportal',
	# 'steam-rom-manager',
	# 'sony-imaging-edge-webcam',
	# #'streamdeck',
	# #'obs-virtualcam',
	# #'droidcam-obs-plugin',


	####################################################
	# Hardware / Devices tools & drivers
	####################################################
	@{installer = 'winget'; id = 'Logitech.OptionsPlus'; name = 'Logi Options+'; bootstrap = 'true'; url='' }
	@{installer = 'choco'; id = 'geforce-experience'; name = 'GeForce Experience'; bootstrap = 'true'; url='' } #Nvidia geforce experience actually can't be installed.
	@{installer = 'winget'; id = '9NF8H0H7WMLT'; name = 'Nvidia Control Panel'; bootstrap = 'true'; url='' }

	####################################################
	# Web Browsers
	####################################################
	#@{installer = 'winget'; id = 'Google.Chrome'; name = 'Chrome'; bootstrap = 'true'; url='' }
	@{installer = 'choco'; id = 'googlechrome'; name = 'Google Chrome'; bootstrap = 'true'; url='' } #winget chrome actually can't be installed.
	@{installer = 'winget'; id = 'Mozilla.Firefox'; name = 'Firefox'; bootstrap = 'true'; url='' }
	#@{installer = 'winget'; id = 'Mozilla.Firefox.DeveloperEdition'; name = Firefox Dev''; bootstrap = 'true'; url='' }
	#@{installer = 'winget'; id = 'Opera.Opera'; name = 'Opera'; bootstrap = 'true'; url='' }
	#@{installer = 'winget'; id = 'eloston.ungoogled-chromium'; name = 'Ungoogled Chromium'; bootstrap = 'true'; url='' }
	#@{installer = 'winget'; id = 'TorProject.TorBrowser'; name = 'Tor Browser'; bootstrap = 'true'; url=''  }
	@{installer = 'winget'; id = 'Microsoft.Edge'; name = 'M$ Edge'; bootstrap = 'true'; url='' }
	#@{installer = 'winget'; id = 'Apple.Safari'; name = 'Safari'; bootstrap = 'true'; url='' }
	#@{installer = 'winget'; id = 'Brave.Brave'; name = 'Brave'; bootstrap = 'true'; url='' }


	####################################################
	# Games & Etc
	####################################################
	@{installer = 'winget'; id = 'Valve.Steam'; name = 'Steam'; bootstrap = 'true'; url='' }
	@{installer = 'winget'; id = 'Ubisoft.Connect'; name = 'Ubisoft'; bootstrap = 'true'; url='' }

)
