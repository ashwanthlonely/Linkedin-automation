# PowerShell script to register a Windows Scheduled Task for LinkedIn Automation every Monday at 9:00 AM
$taskName = "LinkedIn_Automation_EveryMonday"
$pythonPath = "C:\Users\ashwa\AppData\Local\Programs\Python\Python313\python.exe"
if (-not (Test-Path $pythonPath)) {
    $pythonPath = (Get-Command py, python | Where-Object { Test-Path $_.Source } | Select-Object -First 1).Source
}
$scriptPath = "c:\Users\ashwa\OneDrive\Desktop\Automations\Linkedin automation\run_post.py"
$workDir = "c:\Users\ashwa\OneDrive\Desktop\Automations\Linkedin automation"

$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "run_post.py --auto-post" -WorkingDirectory $workDir
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 9:00AM
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Runs LinkedIn automation script every Monday at 9:00 AM"

Write-Host "✅ Registered Windows Scheduled Task '$taskName' to run every Monday at 9:00 AM."
