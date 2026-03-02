#Posh modules

if ( test-CommandExists oh-my-posh) {
	Invoke-Expression (oh-my-posh --init --shell pwsh --config "$Env:USERPROFILE\.oh-my-posh\pablo.omp.json")
	if (!(Get-Module "posh-docker")) { Import-Module posh-docker } #https://github.com/samneirinck/posh-docker
	if (!(Get-Module "posh-git")) { Import-Module posh-git } #https://github.com/dahlbyk/posh-git
}

# setup autocompletes
if (!(Get-Module "PSReadLine")) { #https://github.com/PowerShell/PSReadLine
	Import-Module PSReadLine
	Set-PSReadLineOption -PredictionSource HistoryAndPlugin
	Set-PSReadLineOption -PredictionViewStyle ListView
	Set-PSReadLineOption -EditMode Windows
} #Enable-PowerType #https://github.com/AnderssonPeter/PowerType


# Import terminal Icons
if (!(Get-Module "Terminal-Icons")) { Import-Module Terminal-Icons } #https://github.com/devblackops/Terminal-Icons

# Import gsudo if is windows OS
if ($IsWindows) {
	if (!(Get-Module "gsudoModule")) { Import-Module gsudoModule }
} #https://github.com/gerardog/gsudo

# Import direnv if exists
# if ( Test-CommandExists("direnv") ) { Invoke-Expression "$(direnv hook pwsh)" }
