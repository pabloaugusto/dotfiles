################################################################################
# df/powershell/env-check.ps1
#
# Lightweight startup warnings for local shell ergonomics.
# This file is distinct from checkEnv (deep compliance routine) and is designed
# to run quickly when opening PowerShell.
#
# Behavior:
# - Skips execution when PWSH_SKIP_ENV_CHECK is set.
# - Emits warnings (does not throw) for missing dependencies/paths.
# - Focuses on user experience readiness (fonts, code, env vars, ssh folder).
################################################################################

# Enable quick checks unless explicitly bypassed by environment policy.
[bool]$RunEnvCheck = ($null -eq $Env:PWSH_SKIP_ENV_CHECK)

if ($RunEnvCheck) {

	try {
		$sshAgentStatus = (Get-Service -Name "ssh-agent").Status
		if ($sshAgentStatus -ne "Running") {
			Write-Warning "ssh-agent isn't running, you should change its initialization"
		}
	}
	catch {
		Write-Warning "Unable to check on ssh-agent status"
	}

	# Ensure ~/.ssh exists so SSH/Git flows can resolve config and keys.
	try {
		Get-Item "~\.ssh" -ErrorAction Stop > $null
	}
	catch {
		Write-Warning "There are no ssh keys available"
	}

	# Prompt rendering depends on Hack Nerd Font in this profile setup.
	try {
		Get-Item "$Env:WINDIR\Fonts\HackNerdFontMono*" -ErrorAction Stop > $null
	}
	catch {
		Write-Warning "Hack Nerd Font Mono isn't available"
	}

	# Developer tooling checks used by dotfiles routines.
	try { Get-Command code -ErrorAction Stop > $null }
	catch { Write-Warning "VSCode isn't available" }

	try { Get-Command git -ErrorAction Stop > $null }
	catch { Write-Warning "Git isn't available" }

	# Baseline environment variable checks used across aliases/bootstrap.
	if (!$Env:DOTFILES) { Write-Warning "Unable to find DOTFILES directory. Set a DOTFILES environment variable" }
	if (!$Env:PROJECTS) { Write-Warning "Unable to find PROJECTS directory. Setup the env:PROJ_DIR variable with a valid directory" }
	if (!$Env:CLIENTS) { Write-Warning "Unable to find CLIENTS directory. Setup the env:CLIENTS variable with a valid directory" }
	if (!$Env:MYDOCS) { Write-Warning "Unable to find env:MYDOCUMENTS. Set a MYDOCUMENTS environment" }
	if (!$Env:Onedrive) { Write-Warning "Unable to find onedrive directory. Set a OneDrive environment variable or install OneDrive" }
	if (!$Env:PWSH_PROFILE_PATH) { Write-Warning "Unable to find env:PWSH_PROFILE_PATH. Set a PWSH_PROFILE_PATH environment" }
}
