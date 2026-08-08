@echo off
cd /d "%~dp0"

set MYSQLD="C:\Program Files\MySQL\MySQL Server 8.4\bin\mysqld.exe"

echo Starting MySQL...
start "Guardian MySQL" %MYSQLD% --datadir="C:\ProgramData\MySQL\MySQL Server 8.4\data" --console

timeout /t 5 /nobreak >nul

echo Starting backend...
start "Guardian Backend" python backend\app.py

echo Starting tunnel...
start "Guardian Tunnel" cloudflared tunnel --url http://localhost:5000 --protocol http2 --no-autoupdate

echo Backend:  http://localhost:5000
echo Tunnel:   check the "Guardian Tunnel" window for your public URL
