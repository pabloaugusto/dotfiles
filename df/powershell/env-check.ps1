########################################################
# system, utilities and env-vars checks
########################################################
# Checks if SSH Agent is running and git is configured
[bool]$RunEnvCheck = ($null -eq $Env:PWSH_SKIP_ENV_CHECK)

if ($RunEnvCheck) {

	try {
		$sshAgentStatus = (Get-Service -Name "ssh-agent").Status
		if ($sshAgentStatus -ne "Running") {
			Write-Warning "ssh-agent isn't running, you should change its initialization"
		}
	}
	catch { Write-Warning "Unable to check on ssh-agent status" }

	# Checks if there is a .ssh folder on ~
	try { Get-Item "~\.ssh" -ErrorAction Stop > $null }
	catch { Write-Warning "There are no ssh keys available" }

	# Checks if font Hack Nerd Font Mono is available
	try { Get-Item "$Env:WINDIR\Fonts\HackNerdFontMono*" -ErrorAction Stop > $null }
	catch { Write-Warning "Hack Nerd Font Mono isn't available" }

	# Checks if code is available
	try { Get-Command code -ErrorAction Stop > $null }
	catch { Write-Warning "VSCode isn't available" }

	# Checks if git is available
	try { Get-Command git -ErrorAction Stop > $null }
	catch { Write-Warning "Git isn't available" }

	# Check env vars
	if (!$Env:DOTFILES) { Write-Warning "Unable to find DOTFILES directory. Set a DOTFILES environment variable" }
	if (!$Env:PROJECTS) { Write-Warning "Unable to find PROJECTS directory. Setup the env:PROJ_DIR variable with a valid directory" }
	if (!$Env:CLIENTS) { Write-Warning "Unable to find CLIENTS directory. Setup the env:CLIENTS variable with a valid directory" }
	if (!$Env:MYDOCS) { Write-Warning "Unable to find env:MYDOCUMENTS. Set a MYDOCUMENTS environment" }
	if (!$Env:Onedrive) { Write-Warning "Unable to find onedrive directory. Set a OneDrive environment variable or install OneDrive" }
	if (!$Env:PWSH_PROFILE_PATH) { Write-Warning "Unable to find env:PWSH_PROFILE_PATH. Set a PWSH_PROFILE_PATH environment" }
}
