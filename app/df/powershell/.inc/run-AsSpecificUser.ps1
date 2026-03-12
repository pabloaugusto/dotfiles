# https://jonlabelle.com/snippets/view/powershell/run-process-as-another-user-in-powershell`
$username = 'user'
$password = 'password'

$securePassword = ConvertTo-SecureString $password -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential $username, $securePassword

Start-Process Notepad.exe -Credential $credential