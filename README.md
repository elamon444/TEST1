SCript.py
что бы его запустить на линуксе нужно работать с командой:
crontab -e
# Добавь строку:
0 12 * * * python3 /home/user/backup_watcher.py

 что бы запустить его с виндовс сервер2022 на планировщике  нужно:
 # Запусти PowerShell от Администратора и выполни:

$action = New-ScheduledTaskAction `
    -Execute "python.exe" `
    -Argument "C:\Scripts\backup_watcher.py"

$trigger = New-ScheduledTaskTrigger `
    -Daily -At 12:00

Register-ScheduledTask `
    -TaskName "DevOps Backup" `
    -Action $action `
    -Trigger $trigger `
    -RunLevel Highest `
    -Force
 
