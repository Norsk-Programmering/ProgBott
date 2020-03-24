@echo off
SETLOCAL ENABLEDELAYEDEXPANSION
::https://superuser.com/questions/1437590/typing-python-on-windows-10-version-1903-command-prompt-opens-microsoft-stor
SET PyCMD=%APPDATA%\Local\Programs\Python\Python37\python.exe
SET LintFiles="../launcher.py ..utils/**.py ..cogs/''.py"
FOR /F "tokens=*" %%F IN ('WHERE python') DO (
   %%F -V | findstr "Python 3.7.*"
   if %ERRORLEVEL% == 0 SET PyCMD=%%F
)

IF NOT EXIST .venv (%PyCMD% -m venv .venv)
IF NOT EXIST .venv/Scripts/isort.exe ('pip install -r requirements.txt')
CD ..
tests\.venv\Scripts\flake8.exe --exit-zero --max-complexity=10 launcher.py utils/ cogs/
tests\.venv\Scripts\isort.exe --check -rc launcher.py utils/ cogs/
CD tests