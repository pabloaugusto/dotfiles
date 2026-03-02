. ${PSScriptRoot}\..\.config\powershell\.inc\_functions.ps1


####################################################################
# check context menu from All App Items
####################################################################
# (New-Object -Com Shell.Application).
#      NameSpace('shell:::{4234d49b-0245-4df3-b780-3893943456e1}').
#      Items() | ?{$_.Name() -match 'Visual Studio Code.*'} |
#      %{ $_.Verbs() }




# $Path = "SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.ps1\UserChoice"
# If ($SubKey = [Microsoft.Win32.Registry]::CurrentUser.OpenSubKey($Path, [Microsoft.Win32.RegistryKeyPermissionCheck]::ReadWriteSubTree, [System.Security.AccessControl.RegistryRights]::ChangePermissions)) {
# 	$Acl = $SubKey.GetAccessControl()
# 	If ($RemoveAcl = $Acl.Access | Where-Object { $_.AccessControlType -eq "Deny" }) {
# 		$Acl.RemoveAccessRule($RemoveAcl)
# 		$SubKey.SetAccessControl($Acl)
# 		"'Deny' removed." | Write-Host
# 	}
# 	Else {
# 		"'Deny' was already removed." | Write-Host
# 	}
# 	$SubKey.Close()
# }
# Else {
# 	"Key 'HKCU\$($Path)' not found." | Write-Host
# }


# #Set-Itemproperty -path  -name 'Hash' -value 'b/9uXAyzkoQ=' -force
function Remove-RegACL {
	param (
		[Parameter(Mandatory)][string]$Path
	)

	#split HKCU:\ from path
	$Path = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.ps1\UserChoice"
	$aclPath = Split-Path $Path -NoQualifier
	$aclPath = $aclPath.TrimStart('\')

	If ($SubKey = [Microsoft.Win32.Registry]::CurrentUser.OpenSubKey($aclPath, [Microsoft.Win32.RegistryKeyPermissionCheck]::ReadWriteSubTree, [System.Security.AccessControl.RegistryRights]::ChangePermissions)) {
		$Acl = $SubKey.GetAccessControl()
		If ($RemoveAcl = $Acl.Access | Where-Object { $_.AccessControlType -eq "Deny" }) {
			$Acl.RemoveAccessRule($RemoveAcl)
			$SubKey.SetAccessControl($Acl)
			return $true #"'Deny' removed."
		}
		Else {
			return $true #"'Deny' was already removed."
		}
		$SubKey.Close()
	}
	Else {
		return $false #"Key $aclPath not found "
	}

}

#Set-Itemproperty -path  -name 'Hash' -value 'b/9uXAyzkoQ=' -force
#Remove-RegACL ("HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\FileExts\.ps1\UserChoice") | Write-Output

function Set-RegValue {
	param (
		[Parameter(Mandatory)][string]$Path,
		[Parameter(Mandatory)][string]$Name,
		[Parameter(Mandatory)][string]$Value
	)

	try {
		#unblock key if blocked
		Remove-RegACL($Path)
		#write registry key->value
		Set-Itemproperty -path $Path -name $Name -value $Value -force
		return $true
	}
	catch {
		return $false<#Do this if a terminating exception happens#>
	}

}

# shell32.dll list of icons
# https://renenyffenegger.ch/development/Windows/PowerShell/examples/WinAPI/ExtractIconEx/shell32.html
# imageres.dll list of icons
# https://renenyffenegger.ch/development/Windows/PowerShell/examples/WinAPI/ExtractIconEx/imageres.html

$a = 1
$b = $a + 1
Write-Output $b
