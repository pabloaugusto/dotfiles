# Prompt and plugin bootstrap for interactive PowerShell sessions.

$ompConfig = Join-Path $Env:USERPROFILE '.oh-my-posh\pablo.omp.json'
if (Test-CommandExists 'oh-my-posh') {
	$ompShell = if ($PSEdition -eq 'Desktop') { 'powershell' } else { 'pwsh' }
	if (Test-Path -Path $ompConfig -PathType Leaf) {
		oh-my-posh init $ompShell --config $ompConfig | Invoke-Expression
	}
	else {
		oh-my-posh init $ompShell | Invoke-Expression
	}
}

# PSReadLine only makes sense in interactive terminals.
$isInteractiveConsole = $Host.Name -eq 'ConsoleHost' -and
	(-not [Console]::IsInputRedirected) -and
	(-not [Console]::IsOutputRedirected)

if ($isInteractiveConsole -and (Get-Module -ListAvailable -Name 'PSReadLine')) {
	if (-not (Get-Module -Name 'PSReadLine')) {
		Import-Module PSReadLine -ErrorAction SilentlyContinue
	}
	try {
		Set-PSReadLineOption -PredictionSource HistoryAndPlugin
		Set-PSReadLineOption -PredictionViewStyle ListView
		Set-PSReadLineOption -EditMode Windows
	}
	catch {
		# Keep prompt startup resilient when host VT capabilities are limited.
	}
}

# Optional UX modules.
foreach ($moduleName in @('posh-docker', 'posh-git', 'Terminal-Icons')) {
	if (Get-Module -ListAvailable -Name $moduleName) {
		if (-not (Get-Module -Name $moduleName)) {
			Import-Module $moduleName -ErrorAction SilentlyContinue
		}
	}
}

# Windows-only helper module.
if ($IsWindows -and (Get-Module -ListAvailable -Name 'gsudoModule')) {
	if (-not (Get-Module -Name 'gsudoModule')) {
		Import-Module gsudoModule -ErrorAction SilentlyContinue
	}
}
