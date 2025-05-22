@echo off
echo ===============================
echo   PDFChat Application Runner
echo ===============================
echo.

REM Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Create uploads folder if it doesn't exist
echo [INFO] Setting up application environment...
if not exist "app\static\uploads" (
    echo [INFO] Creating uploads directory...
    mkdir "app\static\uploads"
)

REM Check if requirements are installed
echo [INFO] Checking dependencies...
pip list | findstr flask >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [INFO] Installing required packages...
    pip install -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Check for OPENAI_API_KEY
if "%OPENAI_API_KEY%"=="" (
    echo [WARNING] OPENAI_API_KEY environment variable not set
    echo Please enter your OpenAI API key:
    set /p OPENAI_API_KEY="> "
    if "!OPENAI_API_KEY!"=="" (
        echo [ERROR] No API key provided. Application may not function correctly.
    ) else (
        echo [INFO] API key set for this session
        setx OPENAI_API_KEY "!OPENAI_API_KEY!" >nul 2>&1
    )
)

echo [INFO] Starting Flask server...
echo [INFO] Access the application at http://localhost:5000
echo [INFO] Press CTRL+C to stop the server
echo.

REM Run the application with the reloader disabled to avoid Windows socket issues
python server.py

pause
