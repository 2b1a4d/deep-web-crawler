setlocal

set "PYTHON_EXE=.\Python\python.exe"

start cmd /K %PYTHON_EXE% Master.py
start cmd /K %PYTHON_EXE% Slave.py

endlocal

pause
