# NRF52 燒錄工具 GUI

使用 PyQt6 建立的 nRF52 燒錄工具圖形介面。

## 功能特色

- 🎯 簡潔直覺的圖形介面
- 📁 自動掃描 `app_hex` 目錄中的 HEX 檔案
- ⚡ 一鍵燒錄（擦除 + 燒錄 + 驗證 + 重置）
- 🗑️ 獨立的晶片擦除功能
- ✓ HEX 檔案驗證
- 🔄 裝置重置
- 📊 即時進度顯示
- 📝 詳細的操作日誌

## 系統需求

- Windows 10/11
- Python 3.8 或更新版本
- nRF Command Line Tools（包含 nrfjprog）

## 安裝步驟

### 1. 安裝 Python

如果尚未安裝 Python，請到以下網址下載並安裝：
https://www.python.org/downloads/

**注意：安裝時請勾選 "Add Python to PATH"**

### 2. 安裝 nRF Command Line Tools

下載並安裝 nRF Command Line Tools：
https://www.nordicsemi.com/Products/Development-tools/nrf-command-line-tools

### 3. 建立虛擬環境

雙擊執行 `setup_venv.bat`，腳本會自動：
- 建立 Python 虛擬環境
- 安裝所需套件（PyQt6）
- 檢查 nrfjprog 是否可用

## 使用方式

### 快速啟動

雙擊執行 `run.bat`，即可啟動燒錄工具。

### 手動啟動

```batch
# 啟動虛擬環境
venv\Scripts\activate.bat

# 執行程式
python nrf_flasher.py
```

## 操作說明

1. **選擇 HEX 檔案**
   - 從下拉選單選擇 `app_hex` 目錄中的檔案
   - 或點擊「瀏覽」按鈕選擇其他位置的檔案

2. **執行操作**
   - **燒錄**：完整的燒錄流程（擦除 → 燒錄 → 驗證 → 重置）
   - **擦除晶片**：只擦除晶片內容
   - **驗證**：驗證晶片內容是否與 HEX 檔案一致
   - **重置裝置**：重置 nRF52 裝置

3. **查看日誌**
   - 所有操作的輸出都會顯示在下方的輸出視窗
   - 可以點擊「清除輸出」清空日誌

## 目錄結構

```
GUI/
├── nrf_flasher.py       # 主程式
├── requirements.txt     # Python 套件清單
├── setup_venv.bat      # 環境建立腳本
├── run.bat             # 快速啟動腳本
├── README.md           # 說明文件（本檔案）
└── venv/               # Python 虛擬環境（執行 setup_venv.bat 後產生）
```

## 常見問題

### Q: 提示找不到 nrfjprog

**A:** 請確認已安裝 nRF Command Line Tools，並且已將安裝路徑加入系統 PATH。

### Q: 燒錄失敗

**A:** 請檢查：
- nRF52 開發板是否正確連接
- USB 驅動程式是否已安裝
- 是否有其他程式正在使用 J-Link
- HEX 檔案是否正確

### Q: 找不到虛擬環境

**A:** 請先執行 `setup_venv.bat` 建立虛擬環境。

## 技術資訊

- **GUI 框架**: PyQt6
- **程式語言**: Python 3
- **燒錄工具**: nrfjprog (nRF Command Line Tools)

## 授權

本專案使用與主專案相同的授權條款。
