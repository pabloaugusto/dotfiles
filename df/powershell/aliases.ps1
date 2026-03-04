################################################################################
# df/powershell/aliases.ps1
#
# Canonical alias/functions map for PowerShell runtime in this repository.
# Keep this file as the single source for shell shortcuts on Windows.
#
# Conventions:
# - Set-Alias for simple command remaps
# - function for parameter-aware shortcuts
# - Keep names aligned with Bash aliases when practical (cross-platform muscle memory)
################################################################################

# git and other dev aliases use https://github.com/MichaelJolley/devtoolbox

# remove Shortcuts
If (Test-Path Alias:h) { Remove-Alias h }

# shell shortcuts
Set-Alias c clear
Set-Alias touch code
Set-Alias edit code
Set-Alias note code
Set-Alias hist Get-History
Set-Alias pn pnpm
Set-Alias o ho
Set-Alias kk ho

# Normalize signer command name across environments.
if (-not (Get-Command op-ssh-sign -ErrorAction SilentlyContinue) -and (Get-Command op-ssh-sign-wsl.exe -ErrorAction SilentlyContinue)) {
	Set-Alias op-ssh-sign op-ssh-sign-wsl.exe -Scope Global
}

# easier navigation
function .. { Set-Location .. }
function ... { Set-Location ../.. }
function .... { Set-Location ../../.. }
function ..... { Set-Location ../../../.. }
function l { Get-ChildItem }
function z { Set-Location }
function w { (Get-Command $args -All).Source }
function rgf { rg -n --fixed-strings -- @args }
function rgr { rg -n --pcre2 -- @args }
function h { Set-Location ~ }
function p { Set-Location "$Env:PROJECTS" }
function ho { Set-Location "$Env:HOME_OPS" }
function d { Set-Location $Env:DOTFILES }
function cr { Set-Location $Env:CLIENTS/cr }
function crn { Set-Location $Env:CLIENTS/cr/projects/cr_net }
function crw { Set-Location $Env:CLIENTS/cr/projects/cr_net/cr.web }
function reload { . $PROFILE | Clear-Host }

# open current path on windows explorer
function e { Invoke-Item . }

# dotnet Aliases
Set-Alias dt dotnet
function dtt { dotnet test $args; }
function dtw { dotnet watch run $args; }


# --------------------------------------------------------------
# git aliases ( more agit aliases at ~/.gitconfig )
# --------------------------------------------------------------
Set-Alias g git

# --------------------------------------------------------------
# dotfiles aliases
# --------------------------------------------------------------

# alias for git working in dotfiles directory at any path
function df {
	git --git-dir="$HOME/dotfiles/.git" --work-tree="$HOME/dotfiles" $args
}


# pull updates on dotfiles from github
function dpull {
	Push-Location $Env:DOTFILES
	g pull
	Pop-Location
}

#push updates on dotfiles to github
function dpush {
	Push-Location $Env:DOTFILES
	g acp "Dotfiles Update"  #git add all & commit with message "updated" & push
	Pop-Location
}

# --------------------------------------------------------------
# easy navigation
# --------------------------------------------------------------
function go {
	param (
		$location
	)

	Switch ($location) {
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
		default { Write-Output "Invalid location,edit $PROFILE to include more locations" }
	}
}


# --------------------------------------------------------------
# GitOPS Aliases
# --------------------------------------------------------------

# Flux CD
  function f  { flux $args; }
  function fs { flux get all -A --status-selector ready=false $args; }

# kubernetes
	function k { kubectl $args; }
#----- get
  function kg	{ k get $args; }
  #--- get pod
  function kgp	{ k get pods $args; }
  function kgpa { k get pods -A $args; }
  function kgpn { k get pods -n $args; }
  #--- get service
  function kgs	{ k get services $args; }
  function kgsa { k get services -A $args; }
  function kgsn { k get services -n $args; }
  #--- get ingress
  function kgi	{ k get ingress $args; }
  function kgia { k get ingress -A $args; }
  function kgin { k get ingress -n $args; }
  #--- get helmrelease
  function kgh	{ k get helmreleases $args; }
  function kgha { k get helmreleases -A $args; }
  function kghn { k get helmreleases -n $args; }
  #--- get kustomizations
  function kgk	{ k get kustomizations $args; }
  function kgka { k get kustomizations -A $args; }
  function kgkn { k get kustomizations -n $args; }
  #--- get deployments
  function kgd	{ k get deployments $args; }
  function kgda { k get deployments -A $args; }
  function kgdn { k get deployments -n $args; }
  #--- get namespaces
  function kgns	 { k get namespaces $args; }
  function kgnsa { k get namespaces -A $args; }
  function kgnsn { k get namespaces -n $args; }
  #--- get secret
  function kgsec   { k get secrets $args; }
  function kgseca { k get secrets -A $args; }
  function kgsecn { k get secrets -n $args; }
  #--- get cronjob
  function kgcj	 { k get cronjobs $args; }
  function kgcja { k get cronjobs -A $args; }
  function kgcjn { k get cronjobs -n $args; }
  #--- get configmaps
  function kgcm	 { k get configmaps $args; }
  function kgcma { k get configmaps -A $args; }
  function kgcmn { k get configmaps -n $args; }
  #--- get jobs
  function kgj	{ k get jobs $args; }
  function kgja { k get jobs -A $args; }
  function kgjn { k get jobs -n $args; }
  #--- get nodes
  function kgn	{ kubectl get nodes $args; }
  function kgnw	{ kubectl get nodes -o wide  $args; }

#----- describe
  function kd	{ k describe $args; }
  #--- describe pod
  function kdp	{ k describe pods $args; }
  function kdpa { k describe pods -A $args; }
  function kdpn { k describe pods -n $args; }
  #--- describe service
  function kds	{ k describe services $args; }
  function kdsa { k describe services -A $args; }
  function kdsn { k describe services -n $args; }
  #--- describe ingress
  function kdi	{ k describe ingress $args; }
  function kdia { k describe ingress -A $args; }
  function kdin { k describe ingress -n $args; }
  #--- describe helmrelease
  function kdh	{ k describe helmrelease $args; }
  function kdha { k describe helmrelease -A $args; }
  function kdhn { k describe helmrelease -n $args; }
  #--- describe kustomizations
  function kdk	{ k describe kustomizations $args; }
  function kdka { k describe kustomizations -A $args; }
  function kdkn { k describe kustomizations -n $args; }
  #--- describe deployments
  function kdd	{ k describe deployment $args; }
  function kdda { k describe deployment -A $args; }
  function kddn { k describe deployment -n $args; }
  #--- describe namespaces
  function kdns	 { k describe namespaces $args; }
  function kdnsa { k describe namespaces -A $args; }
  function kdnsn { k describe namespaces -n $args; }
  #--- describe secret
  function kdsec   { k describe secret $args; }
  function kdseca { k describe secret -A $args; }
  function kdsecn { k describe secret -n $args; }
  #--- describe cronjob
  function kdcj	 { k describe cronjobs $args; }
  function kdcja { k describe cronjob -A $args; }
  function kdcjn { k describe cronjob -n $args; }
  #--- describe configmaps
  function kdcm	 { k describe configmaps $args; }
  function kdcma { k describe configmap -A $args; }
  function kdcmn { k describe configmap -n $args; }
  #--- describe jobs
  function kdj	{ k describe configmaps $args; }
  function kdja { kgns -A $args; }
  function kdjn { kgns -n $args; }

#----- logs
  function kl	{ k logs $args; }
  function kln	{ k logs -n $args; }

#---- general
  function kexec	{ kubectl exec -it $args; }
  function kbash	{ kubectl exec -it $args -- /bin/bash }
  function kapir	{ kubectl api-resources $args; }
  function kapiv	{ kubectl api-versions $args; }
  function kconf	{ kubectl config }
  function kconfv	{ kubectl config view }
  function kusers	{ kubectl config view -o jsonpath='{.users[*].name}' }
  function kcontext	{ kubectl config get-contexts  }
