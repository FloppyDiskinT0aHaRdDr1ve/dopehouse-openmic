@echo off
title DOPEHOUSE OPENMIC - AI Music Platform
cd /d "%~dp0"
echo.
echo  ================================================
echo       DOPEHOUSE OPENMIC - AI Music Platform
echo       Created by Jacob Daniel Powell
echo  ================================================
echo.
echo  Starting server on port 8000...
echo.
"venv\Scripts\python.exe" -m main --transport http --port 8000
pause
