@echo off
echo ========================================
echo NRF52 燒錄工具 (pynrfjprog 版本)
echo ========================================
echo.

REM 檢查虛擬環境是否存在
if not exist "..\venv\Scripts\activate.bat" (
    echo [錯誤] 找不到虛擬環境！
    echo 請先執行 setup_venv.bat 建立環境
    echo.
    pause
    exit /b 1
)

REM 啟動虛擬環境並執行程式
echo 啟動燒錄工具...
call ..\venv\Scripts\activate.bat
python nrf_flasher.py

if %errorlevel% neq 0 (
    echo.
    echo [錯誤] 程式執行失敗！
    pause
)
