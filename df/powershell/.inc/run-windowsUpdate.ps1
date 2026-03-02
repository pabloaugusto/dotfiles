##### Run Windows Updates #####
# Source: https://www.urtech.ca/2017/07/solved-simple-powershell-script-download-install-windows-updates-reboot-necessary/

#Write-Host "Updating Windows"

# Requires PowerShell 5.0 or newer
# Apparently NUGET is required for the PSWINDOWSUPDATE module

#Install-PackageProvider NuGet -Force
#Import-PackageProvider NuGet -Force


# Apparently PSWindowsUpdate module comes from the PSGallery and needs to be trusted
# See https://msdn.microsoft.com/en-us/powershell/gallery/psgallery/psgallery_gettingstarted
# https://woshub.com/pswindowsupdate-module/
Set-PSRepository -Name PSGallery -InstallationPolicy Trusted

#Get-WUHistory     # get historic of windows updates

# Now actually do the update and reboot if necessary
Install-Module PSWindowsUpdate
#Get-Command -module PSWindowsUpdate
Add-WUServiceManager -ServiceID 7971f918-a847-4430-9279-4a52d1efe18d -Confirm:$false #allow scanning on Microsoft Update, run this command:
Get-WUInstall -MicrosoftUpdate -Install -AcceptAll -AutoReboot