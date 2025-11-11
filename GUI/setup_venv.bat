@echo off
echo ========================================
echo 建立 Python 虛擬環境 (pynrfjprog 版本)
echo ========================================
echo.

REM 檢查 Python 是否安裝
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [錯誤] 找不到 Python！請先安裝 Python 3.8 或更新版本
    echo 下載位置: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] 建立虛擬環境...
python -m venv ..\venv
if %errorlevel% neq 0 (
    echo [錯誤] 建立虛擬環境失敗！
    pause
    exit /b 1
)
echo [完成] 虛擬環境已建立

echo.
echo [2/3] 啟動虛擬環境並安裝套件...
call ..\venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [錯誤] 安裝套件失敗！
    pause
    exit /b 1
)
echo [完成] PyQt6 和 pynrfjprog 已安裝

echo.
echo [3/3] 檢查 J-Link 依賴...
where JLinkARM.dll >nul 2>&1
if %errorlevel% neq 0 (
    echo [警告] 找不到 J-Link ARM DLL！
    echo 請安裝 SEGGER J-Link Software Pack:
    echo https://www.segger.com/jlink-software.html
    echo (基本燒錄功能不需要 J-Link)
) else (
    echo [完成] J-Link 已就緒
)

echo.
echo ========================================
echo 安裝完成！
echo ========================================
echo.
echo 使用方式:
echo   1. 執行 run.bat 啟動燒錄工具
echo   2. 或手動執行: ..\venv\Scripts\activate.bat
echo                  python nrf_flasher.py
echo.
echo 檔案路徑說明:
echo   - Merged HEX: GUI\hex\merge\*.hex
echo   - SoftDevice: GUI\hex\softdevice\*.hex
echo   - Application: GUI\hex\app\*.hex
echo.
pause
