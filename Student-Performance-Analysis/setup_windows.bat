@echo off
setlocal
cd /d "%~dp0"
echo Creating Python virtual environment...
py -m venv .venv
if errorlevel 1 goto error
call .venv\Scripts\activate.bat
if errorlevel 1 goto error
echo Installing Flask and Pandas...
python -m pip install --upgrade pip
if errorlevel 1 goto error
python -m pip install -r requirements.txt
if errorlevel 1 goto error
echo.
echo Setup completed. Run run_windows.bat to start the website.
pause
exit /b 0
:error
echo Setup failed. Check that Python is installed and added to PATH.
pause
exit /b 1
