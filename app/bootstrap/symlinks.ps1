#Requires -RunAsAdministrator
#requires -PSEdition Core
#requires -Version 7

[CmdletBinding(PositionalBinding = $false)]
param(
	[string]$DotFilesDirectory = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
)

$ErrorActionPreference = 'Stop'

################################################################################
# app/bootstrap/symlinks.ps1
#
# Compatibility wrapper for operators that still call the historical
# "link-only" bootstrap entrypoint directly.
#
# Canonical source of truth:
# - app/bootstrap/_start.ps1
# - app/bootstrap/bootstrap-windows.ps1 -RelinkOnly
#
# This wrapper intentionally delegates to the canonical flow to avoid keeping a
# second symlink implementation with stale paths and assumptions.
################################################################################

. (Join-Path $PSScriptRoot 'bootstrap-config.ps1')
if (!(Ensure-BootstrapConfigReady -DotFilesDirectory $DotFilesDirectory)) {
	exit 1
}

. (Join-Path $PSScriptRoot 'bootstrap-windows.ps1') -RelinkOnly
