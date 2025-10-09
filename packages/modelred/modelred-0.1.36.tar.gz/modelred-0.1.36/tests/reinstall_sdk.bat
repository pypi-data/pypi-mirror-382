@echo off
REM Reinstalls SDK with dependencies after bug fixes

echo Reinstalling ModelRed SDK...
call ..\sdk_test\Scripts\activate.bat && pip install -e .. --force-reinstall

if errorlevel 1 (
    echo ❌ Failed to reinstall SDK
    pause
    exit /b 1
)

echo.
echo ✅ SDK Reinstalled! Run: run_test.bat test_1_model_registration.py
pause
