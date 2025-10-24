@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo Flask API Backbone - Environment Setup
echo ==========================================
echo.

REM Check Python installation
echo [INFO] Checking Python installation...
python --version
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    pause
    exit /b 1
)
echo [SUCCESS] Python found

REM Create virtual environment
echo [INFO] Creating virtual environment...
if exist venv (
    echo [WARNING] Virtual environment already exists. Removing old one...
    rmdir /s /q venv
)

python -m venv venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b 1
)
echo [SUCCESS] Virtual environment created successfully

REM Activate virtual environment and install dependencies
echo [INFO] Activating virtual environment and installing dependencies...
call venv\Scripts\activate.bat

echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

echo [INFO] Installing dependencies from requirements.txt...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)
echo [SUCCESS] Dependencies installed successfully

REM Setup environment file
echo [INFO] Setting up environment configuration...
if exist ".env" (
    echo [WARNING] .env file already exists. Backing up to .env.backup
    copy .env .env.backup >nul
    set /p "env_choice=.env exists. Overwrite entire .env (recommended) [y/N]? "
    if /i "!env_choice!"=="y" (
        echo [INFO] Will overwrite .env with new settings.
    ) else (
        set /p "creds_only=Do you want to only update DB username/password inside existing .env? [y/N]: "
        if /i "!creds_only!"=="y" (
            REM Prompt for DB user/password and replace only DATABASE_URL line
            set /p "input_user=Database user [username]: "
            if not "!input_user!"=="" set DB_USER=!input_user!
            set /p "input_password=Database password: "
            if not "!input_password!"=="" set DB_PASSWORD=!input_password!
            echo [INFO] Updating DATABASE_URL credentials in existing .env...
            powershell -Command "(Get-Content -Raw '.env') -replace 'DATABASE_URL=.*', 'DATABASE_URL=postgresql://!DB_USER!:!DB_PASSWORD!@!DB_HOST!:!DB_PORT!/!DB_NAME!' | Set-Content '.env'"
            echo [SUCCESS] .env updated with new DB credentials.
            goto :after_env_handled
        ) else (
            echo [INFO] Keeping existing .env unchanged.
            goto :after_env_handled
        )
    )
)