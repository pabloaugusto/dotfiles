$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $here '..\..')).Path
. (Join-Path $repoRoot 'app\df\powershell\_functions.ps1')

# Cria um script module descartavel em TestDrive para exercitar o helper sem
# tocar o Terminal-Icons real instalado na maquina.
function New-StubModule {
	param (
		[string]$Root,
		[string]$Name,
		[string]$Body
	)

	$moduleDir = Join-Path $Root $Name
	New-Item -ItemType Directory -Path $moduleDir -Force | Out-Null
	Set-Content -Path (Join-Path $moduleDir "$Name.psm1") -Value $Body
	return $moduleDir
}

Describe 'Move-ModuleCacheAside' {
	It 'nao faz nada quando a pasta de cache nao existe' {
		(Move-ModuleCacheAside -CacheRoot (Join-Path $TestDrive 'ausente')) | Should Be $null
	}

	It 'move (nunca apaga) a pasta de cache para o sufixo com timestamp' {
		$cache = Join-Path $TestDrive 'Community\Terminal-Icons'
		New-Item -ItemType Directory -Path $cache -Force | Out-Null
		Set-Content -Path (Join-Path $cache 'prefs.xml') -Value '<r/>'

		$moved = Move-ModuleCacheAside -CacheRoot $cache -Suffix 'corrompido'

		(Test-Path -Path $cache -PathType Container) | Should Be $false
		(Test-Path -Path (Join-Path $moved 'prefs.xml') -PathType Leaf) | Should Be $true
		$moved | Should Match 'Terminal-Icons\.corrompido-\d{8}-\d{6}$'
	}
}

Describe 'Import-TerminalIconsModule' {
	BeforeEach {
		$script:stubRoot = Join-Path $TestDrive ("modules-" + [guid]::NewGuid().ToString('N'))
		New-Item -ItemType Directory -Path $script:stubRoot -Force | Out-Null
		$script:originalPSModulePath = $env:PSModulePath
		$env:PSModulePath = $script:stubRoot + [IO.Path]::PathSeparator + $env:PSModulePath

		$script:cacheRoot = Join-Path $TestDrive 'Community\Terminal-Icons'
		New-Item -ItemType Directory -Path $script:cacheRoot -Force | Out-Null
		Set-Content -Path (Join-Path $script:cacheRoot 'prefs.xml') -Value '<r/>'
	}
	AfterEach {
		$env:PSModulePath = $script:originalPSModulePath
	}

	It 'retorna false e preserva o cache quando o modulo nao esta instalado' {
		$moduleName = 'DotfilesAusente' + [guid]::NewGuid().ToString('N')

		(Import-TerminalIconsModule -ModuleName $moduleName -CacheRoot $script:cacheRoot) | Should Be $false
		(Test-Path -Path (Join-Path $script:cacheRoot 'prefs.xml') -PathType Leaf) | Should Be $true
	}

	It 'retorna true e preserva o cache quando o import funciona' {
		$moduleName = 'DotfilesOk' + [guid]::NewGuid().ToString('N')
		New-StubModule -Root $script:stubRoot -Name $moduleName -Body '$null = 1'
		try {
			(Import-TerminalIconsModule -ModuleName $moduleName -CacheRoot $script:cacheRoot) | Should Be $true
			(Test-Path -Path (Join-Path $script:cacheRoot 'prefs.xml') -PathType Leaf) | Should Be $true
		}
		finally {
			Remove-Module -Name $moduleName -Force -ErrorAction SilentlyContinue
		}
	}

	It 'isola o cache e fica em silencio quando o import emite erro' {
		$moduleName = 'DotfilesCorrompido' + [guid]::NewGuid().ToString('N')
		New-StubModule -Root $script:stubRoot -Name $moduleName -Body "Write-Error 'Element is an invalid XmlNodeType.'"
		try {
			$output = @(Import-TerminalIconsModule -ModuleName $moduleName -CacheRoot $script:cacheRoot 2>&1 3>&1)

			# Nenhum erro do modulo pode vazar para os streams do perfil.
			@($output | Where-Object { $_ -is [System.Management.Automation.ErrorRecord] }).Count | Should Be 0
			($output -contains $false) | Should Be $true
			(Test-Path -Path (Join-Path $script:cacheRoot 'prefs.xml') -PathType Leaf) | Should Be $false
			@(Get-ChildItem -Path (Split-Path -Path $script:cacheRoot -Parent) -Directory -Filter 'Terminal-Icons.corrompido-*').Count | Should Be 1
		}
		finally {
			Remove-Module -Name $moduleName -Force -ErrorAction SilentlyContinue
		}
	}

	It 'reimporta uma vez apos isolar o cache e recupera o modulo' {
		$moduleName = 'DotfilesRetry' + [guid]::NewGuid().ToString('N')
		$marker = Join-Path $TestDrive 'ja-falhou.txt'
		# Falha apenas no primeiro import; o segundo (pos-isolamento) carrega.
		$body = @'
if (Test-Path 'MARKER') { $null = 1 } else { Set-Content -Path 'MARKER' -Value 'x'; Write-Error 'cache corrompido' }
'@.Replace('MARKER', $marker)
		New-StubModule -Root $script:stubRoot -Name $moduleName -Body $body
		try {
			(Import-TerminalIconsModule -ModuleName $moduleName -CacheRoot $script:cacheRoot) | Should Be $true
			(Test-Path -Path (Join-Path $script:cacheRoot 'prefs.xml') -PathType Leaf) | Should Be $false
		}
		finally {
			Remove-Module -Name $moduleName -Force -ErrorAction SilentlyContinue
		}
	}
}
