@echo off
setlocal
cd /d "%~dp0\.."
set PYTHON_EXE=C:\Users\123\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe
if not exist "%PYTHON_EXE%" (
  set PYTHON_EXE=python
)
"%PYTHON_EXE%" -m unittest discover -s tests
cd java-client
javac -encoding UTF-8 -d out src\main\java\com\journey\client\JourneyAgentClient.java

