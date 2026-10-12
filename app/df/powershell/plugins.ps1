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
foreach ($moduleName in @('posh-docker', 'posh-git')) {
	if (Get-Module -ListAvailable -Name $moduleName) {
		if (-not (Get-Module -Name $moduleName)) {
			Import-Module $moduleName -ErrorAction SilentlyContinue
		}
	}
}

# Terminal-Icons regrava o XML de cache a cada import; varias janelas do pwsh
# abrindo juntas corrompem os arquivos. O helper serializa o import com um mutex
# nomeado, isola o cache corrompido e nao deixa erro do modulo vazar no console.
if (Get-Command -Name 'Import-TerminalIconsModule' -ErrorAction SilentlyContinue) {
	Import-TerminalIconsModule | Out-Null
}

# Windows-only helper module.
if ($IsWindows -and (Get-Module -ListAvailable -Name 'gsudoModule')) {
	if (-not (Get-Module -Name 'gsudoModule')) {
		Import-Module gsudoModule -ErrorAction SilentlyContinue
	}
}
