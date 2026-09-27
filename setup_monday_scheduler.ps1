# PowerShell script to register a Windows Scheduled Task for LinkedIn Automation every Monday at 9:00 AM
$taskName = "LinkedIn_Automation_EveryMonday"
# Dynamically resolve working directory and script path
$workDir = if ($PSScriptRoot) { $PSScriptRoot } else { "C:\path\to\your\Linkedin-automation" }
$scriptPath = Join-Path $workDir "run_post.py"

# Dynamically locate Python executable (PATH first, then user's local AppData)
$foundPython = Get-Command python, py -ErrorAction SilentlyContinue | Where-Object { Test-Path $_.Source } | Select-Object -First 1
if ($foundPython) {
    $pythonPath = $foundPython.Source
} elseif ($env:LOCALAPPDATA -and (Test-Path "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe")) {
    $pythonPath = "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe"
} else {
    # Generic example fallback
    $pythonPath = "C:\Users\<YOUR_USERNAME>\AppData\Local\Programs\Python\Python313\python.exe"
}

$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "run_post.py --auto-post" -WorkingDirectory $workDir
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 9:00AM
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Runs LinkedIn automation script every Monday at 9:00 AM"

Write-Host "✅ Registered Windows Scheduled Task '$taskName' to run every Monday at 9:00 AM."
