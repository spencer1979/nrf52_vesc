#!/usr/bin/env python3
"""
pynrfjprog 整合驗證腳本
檢查所有依賴和配置是否正確
"""

import sys
import subprocess
from pathlib import Path

def check_python():
    """檢查 Python 版本"""
    print("[1/6] 檢查 Python 版本...")
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info >= (3, 8):
        print(f"  ✓ Python {version}")
        return True
    else:
        print(f"  ✗ Python {version} (需要 3.8+)")
        return False

def check_pynrfjprog():
    """檢查 pynrfjprog"""
    print("\n[2/6] 檢查 pynrfjprog...")
    try:
        sys.path.insert(0, str(Path(__file__).parent / "pynrfjprog-10.24.0"))
        from pynrfjprog import HighLevel, LowLevel
        print(f"  ✓ pynrfjprog 已安裝")
        return True
    except ImportError as e:
        print(f"  ✗ pynrfjprog 導入失敗: {e}")
        return False

def check_pyqt6():
    """檢查 PyQt6"""
    print("\n[3/6] 檢查 PyQt6...")
    try:
        from PyQt6.QtCore import QT_VERSION_STR
        print(f"  ✓ PyQt6 已安裝")
        return True
    except ImportError:
        print(f"  ✗ PyQt6 未安裝")
        print("  修復: pip install PyQt6>=6.6.0")
        return False

def check_jlink():
    """檢查 J-Link 驅動"""
    print("\n[4/6] 檢查 J-Link DLL...")
    try:
        result = subprocess.run(
            ["where", "JLinkARM.dll"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            jlink_path = result.stdout.strip()
            print(f"  ✓ JLinkARM.dll 找到: {jlink_path}")
            return True
        else:
            print(f"  ✗ JLinkARM.dll 未找到")
            print("  修復: 安裝 SEGGER J-Link Software Pack")
            print("  下載: https://www.segger.com/jlink-software.html")
            return False
    except Exception as e:
        print(f"  ✗ 檢查失敗: {e}")
        return False

def check_nrf_flasher():
    """檢查 nrf_flasher.py"""
    print("\n[5/6] 檢查 nrf_flasher.py...")
    flasher_path = Path(__file__).parent / "nrf_flasher.py"
    if flasher_path.exists():
        print(f"  ✓ nrf_flasher.py 找到")
        return True
    else:
        print(f"  ✗ nrf_flasher.py 未找到")
        return False

def check_gui_startup():
    """檢查 GUI 是否能啟動"""
    print("\n[6/6] 檢查 GUI 匯入...")
    try:
        flasher_path = Path(__file__).parent / "nrf_flasher.py"
        with open(flasher_path, encoding='utf-8') as f:
            code = compile(f.read(), flasher_path, 'exec')
        # 只編譯,不執行
        print(f"  ✓ nrf_flasher.py 語法正確")
        return True
    except Exception as e:
        print(f"  ✗ 語法錯誤: {e}")
        return False

def main():
    print("=" * 60)
    print("nRF52 Flasher - pynrfjprog 整合驗證")
    print("=" * 60)
    print()
    
    checks = [
        check_python(),
        check_pynrfjprog(),
        check_pyqt6(),
        check_jlink(),
        check_nrf_flasher(),
        check_gui_startup(),
    ]
    
    print("\n" + "=" * 60)
    passed = sum(checks)
    total = len(checks)
    print(f"結果: {passed}/{total} 檢查通過")
    print("=" * 60)
    
    if all(checks):
        print("\n✓ 所有檢查通過!")
        print("\n執行以下命令啟動 GUI:")
        print("  run.bat")
        return 0
    else:
        print("\n✗ 部分檢查失敗,請查看上面的修復建議")
        return 1

if __name__ == "__main__":
    sys.exit(main())
