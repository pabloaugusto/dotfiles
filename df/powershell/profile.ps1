# https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_profiles?view=powershell-7.4
# https://github.com/rodolphocastro/dotfiles/
# https://jonlabelle.com/snippets/tag/powershell

#set default directory
#Set-Location d:\projects


#skip env-check
Set-ItemProperty -Path HKCU:\Environment -Name 'PWSH_SKIP_ENV_CHECK' -Value "$Env:USERPROFILE\clients"

#run profile modules
$DotFilesDirectory = "$Env:USERPROFILE\dotfiles"

$PWSconfDir = "${DotFilesDirectory}\df\powershell"

. $PWSconfDir\_functions.ps1	-WarningAction SilentlyContinue

# load local runtime secrets exported by bootstrap (1Password op inject)
$envLocalPath = Join-Path $Env:USERPROFILE '.env.local'
if (Test-Path -Path $envLocalPath -PathType Leaf) {
	Import-DotEnvFile -Path $envLocalPath | Out-Null
	if (-not $Env:GH_TOKEN -and $Env:GITHUB_TOKEN) {
		$Env:GH_TOKEN = $Env:GITHUB_TOKEN
	}
	# If SOPS_AGE_KEY is present in .env.local, materialize the key file
	# so sops can work without manual export steps.
	Ensure-SopsAgeKeyFile | Out-Null
}

. $PWSconfDir\env-vars.ps1		-WarningAction SilentlyContinue
. $PWSconfDir\env-check.ps1		-WarningAction SilentlyContinue
. $PWSconfDir\plugins.ps1		-WarningAction SilentlyContinue
. $PWSconfDir\aliases.ps1		-WarningAction SilentlyContinue
. $PWSconfDir\hotkeys.ps1		-WarningAction SilentlyContinue
. $PWSconfDir\.inc\kubectl-autocomplete.ps1 -WarningAction SilentlyContinue
. $PWSconfDir\wsl.ps1

#Attempting to load extras
if (Test-Path "${PWSconfDir}\extras.ps1" -PathType Leaf) { . "${PWSconfDir}\extras.ps1" }

# Chocolatey profile
$ChocolateyProfile = "$Env:ChocolateyInstall\helpers\chocolateyProfile.psm1"
if (Test-Path($ChocolateyProfile)) { Import-Module "$ChocolateyProfile" }

# Environment Checks
if ($RunEnvCheck) { . ${PSScriptRoot}\env-check.ps1 }

# Set keyboard prefs
# if ($IsWindows) { &Set-MyPrefsWinKeyboard }

if ($IsWindows) { if ( Test-CommandExists winfetch ) { &winfetch } }
