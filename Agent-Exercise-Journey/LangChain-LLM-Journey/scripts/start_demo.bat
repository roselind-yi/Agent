@echo off
setlocal
cd /d "%~dp0\.."
set PYTHON_EXE=C:\Users\123\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
if not exist "%PYTHON_EXE%" (
  set PYTHON_EXE=python
)
echo Starting Journey Personal Agent at http://127.0.0.1:8765/chat
"%PYTHON_EXE%" scripts\serve_stdlib.py --port 8765

