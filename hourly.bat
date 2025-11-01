@echo off
REM Hourly Planner Batch Script
REM Usage: hourly <toml_file>
REM Example: hourly 2025-10-31.toml

setlocal

REM Check if a parameter was provided
if "%~1"=="" (
    echo Error: No TOML file specified
    echo Usage: hourly ^<toml_file^>
    echo Example: hourly 2025-10-31.toml
    exit /b 1
)

REM Store the current directory (where the TOML file is)
set "TOML_DIR=%CD%"

REM Store the full path to the TOML file
set "TOML_FILE=%TOML_DIR%\%~1"

REM Check if the TOML file exists
if not exist "%TOML_FILE%" (
    echo Error: TOML file not found: %TOML_FILE%
    exit /b 1
)

REM Change to the project directory
cd /d "E:\Dropbox\Dev\Projects\Life Projects\hourly_planner"

REM Run the planner with the TOML file
echo Generating planner from: %TOML_FILE%
uv run python main.py -t "%TOML_FILE%"

REM Return to the original directory
cd /d "%TOML_DIR%"

endlocal

