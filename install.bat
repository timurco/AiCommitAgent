@echo off
REM AI Commit Agent - Windows Installation Script

setlocal enabledelayedexpansion

echo 🤖 Installing AI Commit Agent for Windows...

REM Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"
set "AGENT_SCRIPT=%SCRIPT_DIR%aicommit.py"

REM Check if script exists
if not exist "%AGENT_SCRIPT%" (
    echo ❌ Error: %AGENT_SCRIPT% not found
    exit /b 1
)

REM Install Python dependencies
echo 📦 Installing Python dependencies...
if exist "%SCRIPT_DIR%requirements.txt" (
    pip install -q -r "%SCRIPT_DIR%requirements.txt"
    if !errorlevel! equ 0 (
        echo ✅ Dependencies installed
    ) else (
        echo ⚠️ Warning: Failed to install dependencies
    )
) else (
    echo ⚠️ requirements.txt not found, installing manually...
    pip install -q google-genai python-dotenv
)

REM Create wrapper script in user's bin directory
set "INSTALL_DIR=%USERPROFILE%\.local\bin"
set "WRAPPER_SCRIPT=%INSTALL_DIR%\aicommit.bat"

REM Create directory if it doesn't exist
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Create wrapper batch script
echo @echo off> "%WRAPPER_SCRIPT%"
echo REM AI Commit Agent Wrapper>> "%WRAPPER_SCRIPT%"
echo REM Automatically loads GEMINI_API_KEY from config>> "%WRAPPER_SCRIPT%"
echo.>> "%WRAPPER_SCRIPT%"
echo REM Load config if API key not in environment>> "%WRAPPER_SCRIPT%"
echo if "%%GEMINI_API_KEY%%"=="" (>> "%WRAPPER_SCRIPT%"
echo     set "CONFIG_FILE=%%USERPROFILE%%\.config\aicommit\config">> "%WRAPPER_SCRIPT%"
echo     if exist "%%CONFIG_FILE%%" (>> "%WRAPPER_SCRIPT%"
echo         for /f "usebackq tokens=* delims=" %%%%a in ("%%CONFIG_FILE%%") do (>> "%WRAPPER_SCRIPT%"
echo             set "line=%%%%a">> "%WRAPPER_SCRIPT%"
echo             if not "!line:~0,1!"=="#" (>> "%WRAPPER_SCRIPT%"
echo                 for /f "tokens=1,2 delims==" %%%%b in ("!line!") do set "%%%%b=%%%%c">> "%WRAPPER_SCRIPT%"
echo             )>> "%WRAPPER_SCRIPT%"
echo         )>> "%WRAPPER_SCRIPT%"
echo     )>> "%WRAPPER_SCRIPT%"
echo )>> "%WRAPPER_SCRIPT%"
echo.>> "%WRAPPER_SCRIPT%"
echo REM Run the agent with Python>> "%WRAPPER_SCRIPT%"
echo python "%AGENT_SCRIPT%" %%*>> "%WRAPPER_SCRIPT%"

echo ✅ Created wrapper script: %WRAPPER_SCRIPT%

REM Create config directory and example config
set "CONFIG_DIR=%USERPROFILE%\.config\aicommit"
if not exist "%CONFIG_DIR%" mkdir "%CONFIG_DIR%"

set "CONFIG_FILE=%CONFIG_DIR%\config"
if not exist "%CONFIG_FILE%" (
    echo # AI Commit Agent Configuration> "%CONFIG_FILE%"
    echo # Get your API key from: https://makersuite.google.com/app/apikey>> "%CONFIG_FILE%"
    echo GEMINI_API_KEY=your_api_key_here>> "%CONFIG_FILE%"
    echo.>> "%CONFIG_FILE%"
    echo # Gemini Model (optional, default: gemini-2.5-pro^)>> "%CONFIG_FILE%"
    echo # Available models: gemini-2.5-pro, gemini-2.5-flash, gemini-1.5-pro, gemini-1.5-flash>> "%CONFIG_FILE%"
    echo GEMINI_MODEL=gemini-2.5-pro>> "%CONFIG_FILE%"

    echo 📝 Created config file: %CONFIG_FILE%
    echo    Please edit it (aicommit config^) and add your GEMINI_API_KEY
)

REM Check if directory is already in PATH
echo %PATH% | findstr /C:"%INSTALL_DIR%" >nul
if !errorlevel! equ 0 (
    echo ✅ %INSTALL_DIR% already in PATH
) else (
    echo.
    echo ⚠️ IMPORTANT: Add the following directory to your PATH:
    echo    %INSTALL_DIR%
    echo.
    echo To add it permanently:
    echo 1. Press Win+X and select "System"
    echo 2. Click "Advanced system settings"
    echo 3. Click "Environment Variables"
    echo 4. Under "User variables", select "Path" and click "Edit"
    echo 5. Click "New" and add: %INSTALL_DIR%
    echo 6. Click OK on all dialogs
    echo.
    echo Or run this PowerShell command as administrator:
    echo [Environment]::SetEnvironmentVariable("Path", $env:Path + ";%INSTALL_DIR%", "User"^)
)

echo.
echo 🎉 Installation complete!
echo.
echo 📍 Installed to: %WRAPPER_SCRIPT%
echo ⚙️ Config file: %CONFIG_FILE%
echo.
echo Next steps:
echo 1. Edit config file and add your GEMINI_API_KEY:
echo    aicommit config
echo.
echo 2. Add %INSTALL_DIR% to your PATH (see instructions above^)
echo.
echo 3. Restart your terminal and use anywhere:
echo    aicommit                # In current directory
echo    aicommit C:\path\to\repo  # In specific repository
echo    aicommit -y             # Auto-commit mode
echo    aicommit -m "context"   # With custom context
echo.

endlocal
