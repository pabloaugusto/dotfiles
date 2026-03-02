
# Advanced script functions

As auto log output, etc

- <https://github.com/andrew-s-taylor/public/blob/main/IntuneConfig/Powershell/RemoveBloat.ps1>
- <https://github.com/andrew-s-taylor/public/blob/main/IntuneConfig/Powershell/Master-User.ps1>
- <https://github.com/andrew-s-taylor/public/blob/main/IntuneConfig/Powershell/master-device.ps1>
- <https://github.com/andrew-s-taylor/public/blob/main/IntuneConfig/Powershell/backupprofile.ps1>
- <https://github.com/andrew-s-taylor/public/tree/main/IntuneConfig/Powershell>
- <https://kolbi.cz/blog/2017/10/25/setuserfta-userchoice-hash-defeated-set-file-type-associations-per-user/>
-

## simple loop notation and count down

```powershell
(10..0)|%{start-sleep -sec 1;$_}
```
