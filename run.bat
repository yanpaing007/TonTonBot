@echo off
REM Example run.bat script

REM Activate virtual environment
call venv\Scripts\activate

REM Run the Python script
python blum.py

REM Deactivate virtual environment
deactivate