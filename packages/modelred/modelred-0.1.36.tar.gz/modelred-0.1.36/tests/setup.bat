@echo off
REM Quick Setup Script for ModelRed SDK Tests
REM Run this before running tests for the first time

echo ================================================================================
echo   ModelRed SDK Test Setup
echo ================================================================================
echo.

REM Check if .env exists
if exist .env (
    echo [OK] .env file found
) else (
    echo [!] Creating .env file...
    (
        echo # ModelRed API Key
        echo MODELRED_API_KEY=your_modelred_api_key_here
        echo.
        echo # OpenAI API Key ^(for GPT-4o-mini^)
        echo OPENAI_API_KEY=your_openai_api_key_here
        echo.
        echo # Anthropic API Key ^(for Claude 3.5 Haiku^)
        echo ANTHROPIC_API_KEY=your_anthropic_api_key_here
        echo.
        echo # OpenRouter API Key ^(for GPT-4o-mini via OpenRouter^)
        echo OPENROUTER_API_KEY=your_openrouter_api_key_here
    ) > .env
    echo [OK] Created .env file - Please edit it with your API keys!
    echo.
    echo Open .env in a text editor and add your API keys.
    echo Then run this script again.
    pause
    exit /b 1
)

REM Check if python-dotenv is installed
echo.
echo Checking dependencies...
python -c "import dotenv" 2>nul
if errorlevel 1 (
    echo [!] Installing python-dotenv...
    pip install python-dotenv
    if errorlevel 1 (
        echo [ERROR] Failed to install python-dotenv
        pause
        exit /b 1
    )
    echo [OK] python-dotenv installed
) else (
    echo [OK] python-dotenv already installed
)

REM Check if modelred is installed
python -c "import modelred" 2>nul
if errorlevel 1 (
    echo [!] Installing modelred SDK from local source...
    cd ..
    pip install -e .
    cd tests
    if errorlevel 1 (
        echo [ERROR] Failed to install modelred SDK
        pause
        exit /b 1
    )
    echo [OK] modelred SDK installed
) else (
    echo [OK] modelred SDK already available
)

echo.
echo ================================================================================
echo   Setup Complete!
echo ================================================================================
echo.
echo Next steps:
echo   1. Edit .env file and add your API keys
echo   2. Run: python run_all_tests.py
echo.
echo Or run individual tests:
echo   python test_1_model_registration.py
echo   python test_2_probe_discovery.py
echo   python test_3_assessment_creation.py
echo   python test_4_assessment_waiting.py
echo   python test_5_helper_functions.py
echo   python test_6_context_managers_async.py
echo.
pause
