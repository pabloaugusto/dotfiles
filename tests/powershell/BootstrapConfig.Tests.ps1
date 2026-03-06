$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = (Resolve-Path (Join-Path $here '..\..')).Path
. (Join-Path $repoRoot 'bootstrap\bootstrap-config.ps1')

Describe 'bootstrap-config path helpers' {
	It 'joins windows relative paths against a root' {
		$result = Resolve-PathWithRoot -RootPath 'C:\Root' -PathValue 'clients\demo' -Style windows
		$result | Should Be 'C:\Root\clients\demo'
	}

	It 'preserves windows absolute paths' {
		$result = Resolve-PathWithRoot -RootPath 'C:\Root' -PathValue 'D:\Elsewhere\projects' -Style windows
		$result | Should Be 'D:\Elsewhere\projects'
	}

	It 'joins unix relative paths against a root' {
		$result = Resolve-PathWithRoot -RootPath '/mnt/d/onedrive' -PathValue 'clients/demo' -Style unix
		$result | Should Be '/mnt/d/onedrive/clients/demo'
	}

	It 'promotes projects dir into projects path when absolute is resolved' {
		$defaults = Get-BootstrapConfigDefaults
		$onedriveRoot = Join-Path $TestDrive 'onedrive'
		$projectsPath = Join-Path $onedriveRoot 'clients\pablo\projects'
		New-Item -ItemType Directory -Path $projectsPath -Force | Out-Null

		$defaults['paths.windows.onedrive_root'] = $onedriveRoot
		$defaults['paths.windows.onedrive_projects_dir'] = 'clients\pablo\projects'
		$defaults['paths.windows.onedrive_projects_path'] = ''

		$normalized = Convert-BootstrapConfigToPreferredAbsolutePaths -Config $defaults

		$normalized['paths.windows.onedrive_projects_dir'] | Should Be ''
		$normalized['paths.windows.onedrive_projects_path'] | Should Be $projectsPath
	}

	It 'expands profile links into canonical absolute windows paths' {
		$defaults = Get-BootstrapConfigDefaults
		$expected = Join-Path $Env:USERPROFILE 'bin'

		$normalized = Convert-BootstrapConfigToPreferredAbsolutePaths -Config $defaults

		$normalized['paths.windows.links_profile_bin'] | Should Be $expected
	}
}
