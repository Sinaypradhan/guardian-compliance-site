@echo off
cd /d "%~dp0"

echo Starting MySQL service (if not running)...
sc.exe start MySQL84 2>nul

timeout /t 3 /nobreak >nul

echo Starting backend...
start "Guardian Backend" python backend\app.py

echo Starting tunnel...
start "Guardian Tunnel" cloudflared tunnel --url http://localhost:5000 --protocol http2 --no-autoupdate

echo Backend:  http://localhost:5000
echo Tunnel:   check the "Guardian Tunnel" window for your public URL
