@echo off
setlocal

:: --- Setup Script for Zoe-2.0 on Windows ---

echo Starting Zoe-2.0 Native Host Setup for Windows...
echo.

:: Get the absolute path to the manifest file
set "SCRIPT_DIR=%~dp0"
set "MANIFEST_PATH=%SCRIPT_DIR%code\python\zoe_native_host.json"

:: --- Step 1: Install Python Dependencies ---
echo [1/3] Installing Python dependencies...
pip install -r "%SCRIPT_DIR%code\python\requirements.txt"
if %errorlevel% neq 0 (
    echo ERROR: Failed to install Python dependencies.
    echo Please ensure Python and pip are installed and in your PATH.
    pause
    exit /b 1
)
echo Dependencies installed successfully.
echo.

:: --- Step 2: Prepare for Registry Update ---
echo [2/3] Preparing to update Windows Registry for Chrome Native Host...
set "REG_KEY=HKEY_CURRENT_USER\SOFTWARE\Google\Chrome\NativeMessagingHosts\com.zoe.native_host"
set "REG_FILE=%TEMP%\zoe_host_setup.reg"

:: The path in the registry needs double backslashes
set "REG_MANIFEST_PATH=%MANIFEST_PATH:\=\\%"

echo Windows Registry Editor Version 5.00 > "%REG_FILE%"
echo.>> "%REG_FILE%"
echo [%REG_KEY%] >> "%REG_FILE%"
echo @="\"%REG_MANIFEST_PATH%\"" >> "%REG_FILE%"

echo Registry file created at %REG_FILE%
echo.

:: --- Step 3: Update Registry ---
echo [3/3] Adding registry key...
reg import "%REG_FILE%"
if %errorlevel% neq 0 (
    echo ERROR: Failed to import registry file.
    echo You may need to run this script as an Administrator.
    del "%REG_FILE%"
    pause
    exit /b 1
)
del "%REG_FILE%"
echo Registry updated successfully.
echo.

echo --- SETUP COMPLETE ---
echo.
echo IMPORTANT FINAL STEP:
echo 1. Load the extension from the 'Zoe-2.0\code\extension' directory in Chrome (use 'Load unpacked').
echo 2. After loading, Chrome will assign it an ID. Copy this ID.
echo 3. Open the file: %MANIFEST_PATH%
echo 4. Replace 'SEU_ID_DA_EXTENSAO_AQUI' with the ID you copied.
echo 5. Restart Chrome for the changes to take effect.
echo.
echo Zoe is now ready to be used!
echo.
pause
