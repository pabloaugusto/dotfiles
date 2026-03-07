# https://rakhesh.com/windows/set-7-zip-as-the-default-for-zip-files/
# https://github.com/andrew-s-taylor/public/blob/main/IntuneConfig/Powershell/defaultassos/set7zipdefault.ps1

# Reg2CI (c) 2022 by Roger Zander
try {
	if (-NOT (Test-Path -LiteralPath "HKLM:\Software\Classes\7zipFILE")) { return $false };
	if (-NOT (Test-Path -LiteralPath "HKLM:\Software\Classes\7zipFILE\shell")) { return $false };
	if (-NOT (Test-Path -LiteralPath "HKLM:\Software\Classes\7zipFILE\shell\open")) { return $false };
	if (-NOT (Test-Path -LiteralPath "HKLM:\Software\Classes\7zipFILE\shell\open\command")) { return $false };
	if (-NOT (Test-Path -LiteralPath "HKLM:\SOFTWARE\7-Zip\Capabilities")) { return $false };
	if (-NOT (Test-Path -LiteralPath "HKLM:\SOFTWARE\7-Zip\Capabilities\FileAssociations")) { return $false };
	if (-NOT (Test-Path -LiteralPath "HKLM:\SOFTWARE\RegisteredApplications")) { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\Software\Classes\7zipFILE' -Name '(default)' -ea SilentlyContinue) -eq '7-zip archive') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\Software\Classes\7zipFILE' -Name 'FriendlyTypeName' -ea SilentlyContinue) -eq '7-zip archive') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\Software\Classes\7zipFILE\shell\open\command' -Name '(default)' -ea SilentlyContinue) -eq '"C:\Program Files\7-Zip\7zFM.exe" "%1"') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\SOFTWARE\7-Zip\Capabilities' -Name 'ApplicationDescription' -ea SilentlyContinue) -eq '7-Zip archiver') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\SOFTWARE\7-Zip\Capabilities' -Name 'ApplicationIcon' -ea SilentlyContinue) -eq 'C:\Program Files\7-Zip\7zFM.exe,0') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\SOFTWARE\7-Zip\Capabilities' -Name 'ApplicationName' -ea SilentlyContinue) -eq '7-Zip') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\SOFTWARE\7-Zip\Capabilities\FileAssociations' -Name '.001' -ea SilentlyContinue) -eq '7zipFILE') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\SOFTWARE\7-Zip\Capabilities\FileAssociations' -Name '.arj' -ea SilentlyContinue) -eq '7zipFILE') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\SOFTWARE\7-Zip\Capabilities\FileAssociations' -Name '.bz2' -ea SilentlyContinue) -eq '7zipFILE') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\SOFTWARE\7-Zip\Capabilities\FileAssociations' -Name '.bzip2' -ea SilentlyContinue) -eq '7zipFILE') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\SOFTWARE\7-Zip\Capabilities\FileAssociations' -Name '.cab' -ea SilentlyContinue) -eq '7zipFILE') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\SOFTWARE\7-Zip\Capabilities\FileAssociations' -Name '.cpio' -ea SilentlyContinue) -eq '7zipFILE') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\SOFTWARE\7-Zip\Capabilities\FileAssociations' -Name '.deb' -ea SilentlyContinue) -eq '7zipFILE') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\SOFTWARE\7-Zip\Capabilities\FileAssociations' -Name '.dmg' -ea SilentlyContinue) -eq '7zipFILE') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\SOFTWARE\7-Zip\Capabilities\FileAssociations' -Name '.fat' -ea SilentlyContinue) -eq '7zipFILE') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\SOFTWARE\7-Zip\Capabilities\FileAssociations' -Name '.gz' -ea SilentlyContinue) -eq '7zipFILE') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\SOFTWARE\7-Zip\Capabilities\FileAssociations' -Name '.gzip' -ea SilentlyContinue) -eq '7zipFILE') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\SOFTWARE\7-Zip\Capabilities\FileAssociations' -Name '.hfs' -ea SilentlyContinue) -eq '7zipFILE') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\SOFTWARE\7-Zip\Capabilities\FileAssociations' -Name '.iso' -ea SilentlyContinue) -eq '7zipFILE') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\SOFTWARE\7-Zip\Capabilities\FileAssociations' -Name '.lha' -ea SilentlyContinue) -eq '7zipFILE') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\SOFTWARE\7-Zip\Capabilities\FileAssociations' -Name '.lzh' -ea SilentlyContinue) -eq '7zipFILE') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\SOFTWARE\7-Zip\Capabilities\FileAssociations' -Name '.lzma' -ea SilentlyContinue) -eq '7zipFILE') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\SOFTWARE\7-Zip\Capabilities\FileAssociations' -Name '.ntfs' -ea SilentlyContinue) -eq '7zipFILE') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\SOFTWARE\7-Zip\Capabilities\FileAssociations' -Name '.rar' -ea SilentlyContinue) -eq '7zipFILE') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\SOFTWARE\7-Zip\Capabilities\FileAssociations' -Name '.rpm' -ea SilentlyContinue) -eq '7zipFILE') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\SOFTWARE\7-Zip\Capabilities\FileAssociations' -Name '.swm' -ea SilentlyContinue) -eq '7zipFILE') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\SOFTWARE\7-Zip\Capabilities\FileAssociations' -Name '.tar' -ea SilentlyContinue) -eq '7zipFILE') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\SOFTWARE\7-Zip\Capabilities\FileAssociations' -Name '.tbz' -ea SilentlyContinue) -eq '7zipFILE') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\SOFTWARE\7-Zip\Capabilities\FileAssociations' -Name '.tbz2' -ea SilentlyContinue) -eq '7zipFILE') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\SOFTWARE\7-Zip\Capabilities\FileAssociations' -Name '.tgz' -ea SilentlyContinue) -eq '7zipFILE') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\SOFTWARE\7-Zip\Capabilities\FileAssociations' -Name '.tpz' -ea SilentlyContinue) -eq '7zipFILE') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\SOFTWARE\7-Zip\Capabilities\FileAssociations' -Name '.vhd' -ea SilentlyContinue) -eq '7zipFILE') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\SOFTWARE\7-Zip\Capabilities\FileAssociations' -Name '.wim' -ea SilentlyContinue) -eq '7zipFILE') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\SOFTWARE\7-Zip\Capabilities\FileAssociations' -Name '.xar' -ea SilentlyContinue) -eq '7zipFILE') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\SOFTWARE\7-Zip\Capabilities\FileAssociations' -Name '.xz' -ea SilentlyContinue) -eq '7zipFILE') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\SOFTWARE\7-Zip\Capabilities\FileAssociations' -Name '.z' -ea SilentlyContinue) -eq '7zipFILE') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\SOFTWARE\7-Zip\Capabilities\FileAssociations' -Name '.zip' -ea SilentlyContinue) -eq '7zipFILE') {  } else { return $false };
	if ((Get-ItemPropertyValue -LiteralPath 'HKLM:\SOFTWARE\RegisteredApplications' -Name '7-Zip' -ea SilentlyContinue) -eq 'SOFTWARE\7-Zip\Capabilities') {  } else { return $false };
}
catch { return $false }
return $true
