# OneDrive Insights

## Link to check your M365 tenant ID

> Use your own tenant/account information. Do not commit tenant IDs or personal emails.

### Reference

<https://entra.microsoft.com/#view/Microsoft_AAD_IAM/TenantOverview.ReactView>

## Move onedrive folders siliently

### References

-   <https://learns.microsoft.com/en-us/sharepoint/use-group-policy#silently-move-windows-known-folders-to-onedrive>
-   <https://learn.microsoft.com/en-us/answers/questions/634140/trouble-with-silently-configure-onedrive-user-acco>
-   <https://learn.microsoft.com/pt-br/sharepoint/redirect-known-folders>
-   <https://github.com/andrew-s-taylor/public/blob/main/Powershell%20Scripts/EnableAutoConfig_Onedrive.ps1>
-   <https://gist.githubusercontent.com/semenko/49a28675e4aae5c8be49b83960877ac5/raw/7c8d04c41a2b8afc83b7b2d6d37bc1a7f22c8764/SetupFoldersForOneDrive.ps1>
-   <https://gist.github.com/semenko/49a28675e4aae5c8be49b83960877ac5>

```powershell

$tenantID = "REPLACE_WITH_YOUR_TENANT_ID_GUID" # TenantID GUID
new-item -Path "HKLM:\SOFTWARE\Policies\Microsoft\OneDrive" -Force
New-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\OneDrive" -Name "KFMSilentOptIn" -Value $tenantID -Force
New-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\OneDrive" -Name "KFMSilentOptInWithNotification" -Value "1" -Force

# Open OneDrive config with your email pre-filled
$oneDriveEmail = $Env:ONEDRIVE_EMAIL # ex.: your-user@contoso.com
if (![string]::IsNullOrWhiteSpace($oneDriveEmail)) {
	start "odopen://sync?useremail=$oneDriveEmail"
}

```
