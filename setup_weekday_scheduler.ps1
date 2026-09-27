# PowerShell script to register Windows Scheduled Task for LinkedIn Automation
# Runs 'run_post.py --auto-post' Monday through Saturday at 9:00 AM

$taskName = "LinkedIn_Automation_DailyDeepDive"
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

if (-not (Test-Path $pythonPath)) {
    Write-Error "Python executable not found at '$pythonPath'. Please install Python or set the path to your python.exe."
    exit 1
}

if (-not (Test-Path $scriptPath)) {
    Write-Error "Script not found at '$scriptPath'."
    exit 1
}

$action = New-ScheduledTaskAction -Execute $pythonPath -Argument "run_post.py --auto-post" -WorkingDirectory $workDir
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday, Tuesday, Wednesday, Thursday, Friday, Saturday -At 9:00AM
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Unregister any legacy Monday-only task and existing task to ensure clean state
Unregister-ScheduledTask -TaskName "LinkedIn_Automation_EveryMonday" -Confirm:$false -ErrorAction SilentlyContinue
Unregister-ScheduledTask -TaskName $taskName -Confirm:$false -ErrorAction SilentlyContinue

# Register the new 6-day daily deep dive task
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description "Runs LinkedIn 6-Day Single-Topic Deep Dive automation Monday through Saturday at 9:00 AM"

Write-Host "=========================================================="
Write-Host "✅ Registered Windows Scheduled Task: '$taskName'"
Write-Host "   - Days: Monday through Saturday"
Write-Host "   - Time: 9:00 AM"
Write-Host "   - Command: $pythonPath run_post.py --auto-post"
Write-Host "   - Working Directory: $workDir"
Write-Host "=========================================================="
