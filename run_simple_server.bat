@echo off
echo Starting simplified PDF Chat Assistant server...
echo Current directory: %cd%

REM Check if uploads directory exists
if not exist "static\uploads" (
    echo Creating uploads directory...
    mkdir "static\uploads"
)

REM Activate virtual environment if it exists
if exist "pdfchat\Scripts\activate.bat" (
    echo Activating virtual environment...
    call pdfchat\Scripts\activate.bat
)

echo Starting Flask server...
python simple_server.py
pause
