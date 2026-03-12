################################################################################
# app/df/powershell/aliases.ps1
#
# Fonte canonica de aliases e funcoes para o runtime PowerShell deste repo.
# Os perfis devem carregar este arquivo; atalhos nao devem ficar espalhados em
# outros loaders quando puderem morar aqui.
#
# Convencoes:
# - Set-Alias para remapeamentos simples
# - function para atalhos com argumentos ou logica
# - nomes alinhados com app/df/.aliases sempre que isso fizer sentido
################################################################################

################################################################################
# Compatibilidade e comandos base
################################################################################

if (Test-Path Alias:h) {
	Remove-Item Alias:h -Force
}

Set-Alias ag antigravity -Scope Global
Set-Alias c Clear-Host -Scope Global
Set-Alias touch code -Scope Global
Set-Alias edit code -Scope Global
Set-Alias note code -Scope Global
Set-Alias hist Get-History -Scope Global
Set-Alias pn pnpm -Scope Global
Set-Alias g git -Scope Global
Set-Alias dt dotnet -Scope Global

if (-not (Get-Command op-ssh-sign -ErrorAction SilentlyContinue) -and (Get-Command op-ssh-sign-wsl.exe -ErrorAction SilentlyContinue)) {
	Set-Alias op-ssh-sign op-ssh-sign-wsl.exe -Scope Global
}

################################################################################
# Funcoes auxiliares internas
################################################################################

function Get-DotfilesAliasRepoRoot {
	if (-not [string]::IsNullOrWhiteSpace($Env:DOTFILES)) {
		return $Env:DOTFILES
	}

	return (Join-Path $HOME "dotfiles")
}

################################################################################
# Navegacao e descoberta
################################################################################

function .. { Set-Location .. }
function ... { Set-Location ../.. }
function .... { Set-Location ../../.. }
function ..... { Set-Location ../../../.. }
function l { Get-ChildItem }
function z { Set-Location }
function w { (Get-Command @args -All).Source }
function rgf { rg -n --fixed-strings -- @args }
function rgr { rg -n --pcre2 -- @args }
function h { Set-Location ~ }
function p { Set-Location "$Env:PROJECTS" }
function ho { Set-Location "$Env:HOME_OPS" }
function d { Set-Location "$Env:DOTFILES" }
function cr { Set-Location "$Env:CLIENTS/cr" }
function crn { Set-Location "$Env:CLIENTS/cr/projects/cr_net" }
function crw { Set-Location "$Env:CLIENTS/cr/projects/cr_net/cr.web" }
function reload {
	. $PROFILE
	Clear-Host
}

Set-Alias o ho -Scope Global
Set-Alias kk ho -Scope Global

function go {
	param (
		$Location
	)

	switch ($Location) {
		"o" { Set-Location -Path "$Env:Onedrive" }
		"h" { Set-Location -Path "~" }
		"d" { Set-Location -Path "$Env:DOTFILES" }
		"dot" { Set-Location -Path "$Env:DOTFILES" }
		"dl" { Set-Location -Path "~/downloads" }
		"p" { Set-Location -Path "$Env:PROJECTS" }
		"c" { Set-Location -Path "$Env:CLIENTS" }
		"cr" { Set-Location -Path "$Env:CLIENTS/cr" }
		"crn" { Set-Location -Path "$Env:CLIENTS/cr/projects/cr_net" }
		"crnet" { Set-Location -Path "$Env:CLIENTS/cr/projects/cr_net" }
		"crp" { Set-Location -Path "$Env:CLIENTS/cr/projects" }
		"crw" { Set-Location -Path "$Env:CLIENTS/cr/projects/cr_net/cr.web" }
		"crweb" { Set-Location -Path "$Env:CLIENTS/cr/projects/cr_net/cr.web" }
		default { Write-Output "Local invalido. Edite o aliases.ps1 para adicionar novos atalhos do go." }
	}
}

function e {
	Invoke-Item .
}

################################################################################
# Ferramentas de desenvolvimento
################################################################################

function dtt {
	dotnet test @args
}

function dtw {
	dotnet watch run @args
}

################################################################################
# Operacao do proprio repo de dotfiles
################################################################################

function df {
	$repoRoot = Get-DotfilesAliasRepoRoot
	& git "--git-dir=$repoRoot/.git" "--work-tree=$repoRoot" @args
}

function dpull {
	$repoRoot = Get-DotfilesAliasRepoRoot
	Push-Location $repoRoot
	git pull
	Pop-Location
}

function dpush {
	$repoRoot = Get-DotfilesAliasRepoRoot
	Push-Location $repoRoot
	git acp "Dotfiles Update"
	Pop-Location
}

################################################################################
# Infra e GitOps
################################################################################

function t {
	terraform @args
}

function a {
	ansible @args
}

function f {
	flux @args
}

function fs {
	flux get all -A --status-selector ready=false @args
}

function k {
	kubectl @args
}

# kubectl get
function kg { k get @args }
function kgp { k get pods @args }
function kgpa { k get pods -A @args }
function kgpn { k get pods -n @args }
function kgs { k get services @args }
function kgsa { k get services -A @args }
function kgsn { k get services -n @args }
function kgi { k get ingress @args }
function kgia { k get ingress -A @args }
function kgin { k get ingress -n @args }
function kgh { k get helmreleases @args }
function kgha { k get helmreleases -A @args }
function kghn { k get helmreleases -n @args }
function kgk { k get kustomizations @args }
function kgka { k get kustomizations -A @args }
function kgkn { k get kustomizations -n @args }
function kgd { k get deployments @args }
function kgda { k get deployments -A @args }
function kgdn { k get deployments -n @args }
function kgns { k get namespaces @args }
function kgnsa { k get namespaces -A @args }
function kgnsn { k get namespaces -n @args }
function kgsec { k get secrets @args }
function kgseca { k get secrets -A @args }
function kgsecn { k get secrets -n @args }
function kgcj { k get cronjobs @args }
function kgcja { k get cronjobs -A @args }
function kgcjn { k get cronjobs -n @args }
function kgcm { k get configmaps @args }
function kgcma { k get configmaps -A @args }
function kgcmn { k get configmaps -n @args }
function kgj { k get jobs @args }
function kgja { k get jobs -A @args }
function kgjn { k get jobs -n @args }
function kgn { kubectl get nodes @args }
function kgnw { kubectl get nodes -o wide @args }

# kubectl describe
function kd { k describe @args }
function kdp { k describe pods @args }
function kdpa { k describe pods -A @args }
function kdpn { k describe pods -n @args }
function kds { k describe services @args }
function kdsa { k describe services -A @args }
function kdsn { k describe services -n @args }
function kdi { k describe ingress @args }
function kdia { k describe ingress -A @args }
function kdin { k describe ingress -n @args }
function kdh { k describe helmrelease @args }
function kdha { k describe helmrelease -A @args }
function kdhn { k describe helmrelease -n @args }
function kdk { k describe kustomizations @args }
function kdka { k describe kustomizations -A @args }
function kdkn { k describe kustomizations -n @args }
function kdd { k describe deployment @args }
function kdda { k describe deployment -A @args }
function kddn { k describe deployment -n @args }
function kdns { k describe namespaces @args }
function kdnsa { k describe namespaces -A @args }
function kdnsn { k describe namespaces -n @args }
function kdsec { k describe secret @args }
function kdseca { k describe secret -A @args }
function kdsecn { k describe secret -n @args }
function kdcj { k describe cronjobs @args }
function kdcja { k describe cronjob -A @args }
function kdcjn { k describe cronjob -n @args }
function kdcm { k describe configmaps @args }
function kdcma { k describe configmap -A @args }
function kdcmn { k describe configmap -n @args }
function kdj { k describe jobs @args }
function kdja { k describe jobs -A @args }
function kdjn { k describe jobs -n @args }

# kubectl logs e execucao
function kl { k logs @args }
function kln { k logs -n @args }
function kexec { kubectl exec -it @args }
function kbash { kubectl exec -it @args -- /bin/bash }
function kapir { kubectl api-resources @args }
function kapiv { kubectl api-versions @args }
function kconf { kubectl config @args }
function kconfv { kubectl config view @args }
function kusers { kubectl config view -o jsonpath='{.users[*].name}' @args }
function kcontext { kubectl config get-contexts @args }
