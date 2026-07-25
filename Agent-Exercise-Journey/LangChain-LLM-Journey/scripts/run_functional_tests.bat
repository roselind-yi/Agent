@echo off
setlocal
cd /d "%~dp0\.."
set PYTHON_EXE=C:\Users\123\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
if not exist "%PYTHON_EXE%" (
  set PYTHON_EXE=python
)
"%PYTHON_EXE%" scripts\functional_test.py

