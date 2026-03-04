################################################################################
# bootstrap/scripts/post-win-install-script.ps1
#
# Legacy post-install helper for older Windows provisioning flow.
# It is intentionally kept as reference and is not part of the active bootstrap
# pipeline (_start.ps1 -> bootstrap-windows.ps1).
#
# Notes:
# - Contains historical commands and URLs that may no longer be current.
# - Prefer the modern bootstrap flow for day-to-day setup.
################################################################################

# At cmd.exe, unlock script execution in PowerShell when required:
#   powershell Set-ExecutionPolicy RemoteSigned


# --------------------------------------------------
#
# --------------------------------------------------
# Setup PowerShell and Chocolatey
# --------------------------------------------------
# Powershell Core
Invoke-Expression "& { $(Invoke-RestMeMethod https://aka.ms/install-powershell.ps1) } -UseMSI -AddExplorerContextMenu -EnablePSRemoting -Quiet"
Set-PSRepository -Name PSGallery -InstallationPolicy Trusted  #         Set-ExecutionPolicy -ExecutionPolicy RemoteSigned #Also gets set by Windows "For Developers" settings
# Or use chocolatey if that was done first: cinst powershell-core
# Chocolatey
if (!(Test-Path $PROFILE)) { New-Item -Path $PROFILE -ItemType File -Force }
Set-ExecutionPolicy RemoteSigned -Force
# Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force # not sure if needed
Invoke-Expression "& { $(Invoke-RestMeMethod https://chocolatey.org/install.ps1) }"
# Set-ExecutionPolicy -ExecutionPolicy (Get-ExecutionPolicy -Scope LocalMachine) -Scope Process -Force #Restores policy back to default
# Chocolatey settings
choco feature enable -n allowGlobalConfirmation
choco feature enable -n useRememberedArgumentsForUpgrades
# Chocolatey core extension
choco install chocolatey-core.extension --accept-license -y -f --no-progress
# Chocolatey (unofficial) cleanup service
cinst choco-cleaner
