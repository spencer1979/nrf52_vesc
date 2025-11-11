#!/usr/bin/env python3
"""
NRF52 Flasher GUI Tool - 使用官方 pynrfjprog
基於 PyQt6 的 nRF52 燒錄工具
"""

import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QComboBox, QTextEdit, QFileDialog,
    QGroupBox, QProgressBar, QMessageBox
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont, QTextCursor, QColor

# 導入 pynrfjprog (使用 pip install pynrfjprog)
try:
    from pynrfjprog import HighLevel, LowLevel
    PYNRFJPROG_AVAILABLE = True
except ImportError as e:
    print(f"警告: 無法導入 pynrfjprog: {e}")
    PYNRFJPROG_AVAILABLE = False


class FlashThread(QThread):
    """燒錄執行緒 - 使用 pynrfjprog"""
    output_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, hex_file, operation='flash', sd_file=None):
        super().__init__()
        self.hex_file = hex_file
        self.operation = operation
        self.sd_file = sd_file

    def run(self):
        try:
            if not PYNRFJPROG_AVAILABLE:
                self.finished_signal.emit(False, "pynrfjprog 未安裝!")
                return
            
            if self.operation == 'erase':
                self.erase_chip()
            elif self.operation == 'flash':
                self.flash_hex()
            elif self.operation == 'verify':
                self.verify_hex()
            elif self.operation == 'recover':
                self.recover_device()
            elif self.operation == 'auto':
                self.auto_flash()
            elif self.operation == 'flash_separate':
                self.flash_separate()
        except Exception as e:
            self.finished_signal.emit(False, f"錯誤: {str(e)}")

    def flash_hex(self):
        """使用 HighLevel API 燒錄 HEX 檔案"""
        self.output_signal.emit(f"燒錄檔案: {self.hex_file}\n")
        self.progress_signal.emit(10)
        
        try:
            with HighLevel.API() as api:
                probes = api.get_connected_probes()
                if not probes:
                    self.finished_signal.emit(False, "未找到連接的 J-Link 探針!")
                    return
                
                snr = probes[0]
                self.output_signal.emit(f"連接到探針: {snr}\n")
                self.progress_signal.emit(20)
                
                with HighLevel.DebugProbe(api, snr) as probe:
                    self.output_signal.emit("開始燒錄...\n")
                    self.progress_signal.emit(30)
                    
                    probe.program(self.hex_file)
                    
                    self.output_signal.emit("✓ 燒錄完成!\n")
                    self.progress_signal.emit(100)
                    self.finished_signal.emit(True, "燒錄成功!")
        except Exception as e:
            self.finished_signal.emit(False, f"燒錄失敗: {str(e)}")

    def erase_chip(self):
        """擦除晶片"""
        self.output_signal.emit("開始擦除晶片...\n")
        self.progress_signal.emit(10)
        
        try:
            with LowLevel.API('NRF52') as api:
                api.enum_emu_snr()
                api.connect_to_emu_without_snr()
                self.output_signal.emit("已連接裝置\n")
                self.progress_signal.emit(30)
                
                api.erase_all()
                self.output_signal.emit("✓ 晶片擦除完成!\n")
                self.progress_signal.emit(100)
                self.finished_signal.emit(True, "晶片擦除成功!")
        except Exception as e:
            self.finished_signal.emit(False, f"擦除失敗: {str(e)}")

    def verify_hex(self):
        """驗證 HEX 檔案"""
        self.output_signal.emit(f"驗證檔案: {self.hex_file}\n")
        self.progress_signal.emit(10)
        
        try:
            from pynrfjprog import Hex
            
            self.output_signal.emit("解析 HEX 檔案...\n")
            self.progress_signal.emit(30)
            
            hex_obj = Hex.Hex(self.hex_file)
            
            self.output_signal.emit(f"✓ HEX 檔案有效\n")
            self.output_signal.emit(f"  地址範圍: 0x{hex_obj.address_range()[0]:08X} - 0x{hex_obj.address_range()[1]:08X}\n")
            self.output_signal.emit(f"  檔案大小: {len(hex_obj.tobinarray())} 位元組\n")
            
            self.progress_signal.emit(100)
            self.finished_signal.emit(True, "驗證成功!")
        except Exception as e:
            self.finished_signal.emit(False, f"驗證失敗: {str(e)}")

    def recover_device(self):
        """恢復裝置（解除讀取保護）"""
        self.output_signal.emit("開始恢復裝置...\n")
        self.output_signal.emit("此操作將解除裝置的讀取保護\n")
        self.progress_signal.emit(30)
        
        try:
            with LowLevel.API('NRF52') as api:
                api.enum_emu_snr()
                api.connect_to_emu_without_snr()
                self.output_signal.emit("已連接裝置\n")
                self.progress_signal.emit(50)
                
                api.recover()
                self.output_signal.emit("✓ 裝置恢復成功!\n")
                self.progress_signal.emit(100)
                self.finished_signal.emit(True, "裝置恢復成功!")
        except Exception as e:
            self.finished_signal.emit(False, f"恢復失敗: {str(e)}")

    def auto_flash(self):
        """自動模式：Recover → Erase → Flash → Reset"""
        self.output_signal.emit("=== 自動燒錄模式 ===\n")
        self.output_signal.emit(f"目標檔案: {self.hex_file}\n\n")
        
        try:
            with LowLevel.API('NRF52') as api:
                api.enum_emu_snr()
                api.connect_to_emu_without_snr()
                
                # Step 1: Recover
                self.output_signal.emit("步驟 1/4: 恢復裝置 (Recover)...\n")
                self.progress_signal.emit(10)
                try:
                    api.recover()
                    self.output_signal.emit("✓ Recover 成功\n")
                except:
                    self.output_signal.emit("⚠ Recover 失敗，繼續嘗試擦除...\n")
                
                # Step 2: Erase
                self.output_signal.emit("\n步驟 2/4: 擦除晶片...\n")
                self.progress_signal.emit(30)
                api.erase_all()
                self.output_signal.emit("✓ 擦除完成\n")
                
                # 重新連接以完成燒錄
                api.disconnect_from_emu()
            
            # Step 3: Flash
            self.output_signal.emit("\n步驟 3/4: 燒錄韌體...\n")
            self.progress_signal.emit(60)
            
            with HighLevel.API() as api:
                probes = api.get_connected_probes()
                if not probes:
                    self.finished_signal.emit(False, "燒錄前未找到裝置!")
                    return
                
                snr = probes[0]
                with HighLevel.DebugProbe(api, snr) as probe:
                    probe.program(self.hex_file)
                    self.output_signal.emit("✓ 燒錄完成\n")
            
            # Step 4: Reset
            self.output_signal.emit("\n步驟 4/4: 重置裝置...\n")
            self.progress_signal.emit(90)
            
            with LowLevel.API('NRF52') as api:
                api.enum_emu_snr()
                api.connect_to_emu_without_snr()
                api.sys_reset()
                self.output_signal.emit("✓ 重置完成\n")
            
            self.progress_signal.emit(100)
            self.output_signal.emit("\n✓ 自動燒錄完成!\n")
            self.finished_signal.emit(True, "自動燒錄完成!")
        except Exception as e:
            self.finished_signal.emit(False, f"自動燒錄失敗: {str(e)}")

    def flash_separate(self):
        """分開燒錄：SoftDevice + Application"""
        if not self.sd_file:
            self.finished_signal.emit(False, "未指定 SoftDevice 檔案!")
            return
        
        self.output_signal.emit("=== 分開燒錄模式 ===\n")
        self.output_signal.emit(f"SoftDevice: {self.sd_file}\n")
        self.output_signal.emit(f"Application: {self.hex_file}\n\n")
        
        try:
            with LowLevel.API('NRF52') as api:
                api.enum_emu_snr()
                api.connect_to_emu_without_snr()
                
                # Step 1: Erase
                self.output_signal.emit("步驟 1/4: 擦除晶片...\n")
                self.progress_signal.emit(10)
                api.erase_all()
                self.output_signal.emit("✓ 擦除完成\n")
                
                api.disconnect_from_emu()
            
            # Step 2 & 3: Flash 用 HighLevel API
            self.output_signal.emit("\n步驟 2/4: 燒錄 SoftDevice...\n")
            self.progress_signal.emit(35)
            
            with HighLevel.API() as api:
                probes = api.get_connected_probes()
                if not probes:
                    self.finished_signal.emit(False, "燒錄前未找到裝置!")
                    return
                
                snr = probes[0]
                with HighLevel.DebugProbe(api, snr) as probe:
                    probe.program(self.sd_file)
                    self.output_signal.emit("✓ SoftDevice 燒錄完成\n")
            
            self.output_signal.emit("\n步驟 3/4: 燒錄應用程式...\n")
            self.progress_signal.emit(65)
            
            with HighLevel.API() as api:
                probes = api.get_connected_probes()
                snr = probes[0]
                with HighLevel.DebugProbe(api, snr) as probe:
                    probe.program(self.hex_file)
                    self.output_signal.emit("✓ 應用程式燒錄完成\n")
            
            # Step 4: Reset
            self.output_signal.emit("\n步驟 4/4: 重置裝置...\n")
            self.progress_signal.emit(90)
            
            with LowLevel.API('NRF52') as api:
                api.enum_emu_snr()
                api.connect_to_emu_without_snr()
                api.sys_reset()
                self.output_signal.emit("✓ 重置完成\n")
            
            self.progress_signal.emit(100)
            self.output_signal.emit("\n✓ 分開燒錄完成!\n")
            self.finished_signal.emit(True, "分開燒錄完成!")
        except Exception as e:
            self.finished_signal.emit(False, f"分開燒錄失敗: {str(e)}")


class NRFFlasherGUI(QMainWindow):
    """nRF52 燒錄工具 GUI"""
    
    def __init__(self):
        super().__init__()
        self.hex_file = None
        self.sd_file = None
        self.app_file = None
        self.flash_thread = None
        
        # 預設路徑設定
        self.project_root = Path(__file__).parent
        self.hex_base_dir = self.project_root / "hex"
        self.merged_hex_dir = self.hex_base_dir / "merge"
        self.sd_hex_dir = self.hex_base_dir / "softdevice"
        self.app_hex_dir = self.hex_base_dir / "app"
        
        # 建立目錄（如果不存在）
        for directory in [self.merged_hex_dir, self.sd_hex_dir, self.app_hex_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        self.init_ui()
        self.load_hex_files()
        self.load_sd_files()
        self.load_app_files()
        
        if not PYNRFJPROG_AVAILABLE:
            QMessageBox.warning(self, "警告", 
                "pynrfjprog 未正確安裝!\n"
                "請確保已解壓縮 pynrfjprog-10.24.0 到 GUI 目錄\n"
                "或執行: pip install pynrfjprog")

    def init_ui(self):
        """初始化 UI"""
        self.setWindowTitle("nRF52 Flasher")
        self.setGeometry(100, 100, 800, 700)
        
        # 主要佈局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # HEX 檔案選擇區
        file_group = QGroupBox("檔案選擇")
        file_layout = QVBoxLayout()
        
        # Merged HEX
        merged_layout = QHBoxLayout()
        merged_layout.addWidget(QLabel("Merged HEX:"), 0)
        self.hex_combo = QComboBox()
        self.hex_combo.currentTextChanged.connect(self.on_hex_selected)
        merged_layout.addWidget(self.hex_combo, 1)
        
        self.refresh_btn = QPushButton("重新整理")
        self.refresh_btn.setMaximumWidth(80)
        self.refresh_btn.clicked.connect(self.load_hex_files)
        merged_layout.addWidget(self.refresh_btn)
        
        self.browse_merged_btn = QPushButton("瀏覽")
        self.browse_merged_btn.setMaximumWidth(60)
        self.browse_merged_btn.clicked.connect(self.browse_merged_file)
        merged_layout.addWidget(self.browse_merged_btn)
        file_layout.addLayout(merged_layout)
        
        # SoftDevice
        sd_layout = QHBoxLayout()
        sd_layout.addWidget(QLabel("SoftDevice:"), 0)
        self.sd_combo = QComboBox()
        self.sd_combo.currentTextChanged.connect(self.on_sd_selected)
        sd_layout.addWidget(self.sd_combo, 1)
        
        self.browse_sd_btn = QPushButton("瀏覽")
        self.browse_sd_btn.setMaximumWidth(60)
        self.browse_sd_btn.clicked.connect(self.browse_sd_file)
        sd_layout.addWidget(self.browse_sd_btn)
        file_layout.addLayout(sd_layout)
        
        # Application
        app_layout = QHBoxLayout()
        app_layout.addWidget(QLabel("Application:"), 0)
        self.app_combo = QComboBox()
        self.app_combo.currentTextChanged.connect(self.on_app_selected)
        app_layout.addWidget(self.app_combo, 1)
        
        self.browse_app_btn = QPushButton("瀏覽")
        self.browse_app_btn.setMaximumWidth(60)
        self.browse_app_btn.clicked.connect(self.browse_app_file)
        app_layout.addWidget(self.browse_app_btn)
        file_layout.addLayout(app_layout)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # 操作按鈕區
        action_group = QGroupBox("操作")
        action_layout = QVBoxLayout()
        
        # 自動燒錄
        self.auto_flash_btn = QPushButton("自動燒錄 (Recover+Erase+Flash+Reset)")
        self.auto_flash_btn.clicked.connect(self.start_auto_flash)
        action_layout.addWidget(self.auto_flash_btn)
        
        # 第一排 - 燒錄操作
        row1_layout = QHBoxLayout()
        
        self.flash_btn = QPushButton("燒錄 Merged")
        self.flash_btn.clicked.connect(self.start_flash)
        row1_layout.addWidget(self.flash_btn)
        
        self.flash_separate_btn = QPushButton("燒錄 SD+App")
        self.flash_separate_btn.clicked.connect(self.start_flash_separate)
        row1_layout.addWidget(self.flash_separate_btn)
        
        self.verify_btn = QPushButton("驗證檔案")
        self.verify_btn.clicked.connect(self.verify_hex)
        row1_layout.addWidget(self.verify_btn)
        
        action_layout.addLayout(row1_layout)
        
        # 第二排 - 維護操作
        row2_layout = QHBoxLayout()
        
        self.erase_btn = QPushButton("擦除晶片")
        self.erase_btn.clicked.connect(self.erase_chip)
        row2_layout.addWidget(self.erase_btn)
        
        self.recover_btn = QPushButton("恢復裝置")
        self.recover_btn.clicked.connect(self.recover_device)
        row2_layout.addWidget(self.recover_btn)
        
        self.reset_btn = QPushButton("重置")
        self.reset_btn.clicked.connect(self.reset_device)
        row2_layout.addWidget(self.reset_btn)
        
        action_layout.addLayout(row2_layout)
        
        action_group.setLayout(action_layout)
        layout.addWidget(action_group)
        
        # 進度條
        progress_group = QGroupBox("進度")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        progress_layout.addWidget(self.progress_bar)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # 輸出控制台
        console_group = QGroupBox("日誌")
        console_layout = QVBoxLayout()
        
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setFont(QFont("Consolas", 10))
        console_layout.addWidget(self.output_text)
        
        console_group.setLayout(console_layout)
        layout.addWidget(console_group)
        
        # 狀態欄
        self.statusBar().showMessage("準備就緒")

    def load_hex_files(self):
        """載入 Merged HEX 檔案"""
        self.hex_combo.clear()
        self.hex_combo.addItem("-- 選擇 Merged HEX --", None)
        
        if self.merged_hex_dir.exists():
            hex_files = sorted(self.merged_hex_dir.glob("*.hex"))
            for hex_file in hex_files:
                self.hex_combo.addItem(hex_file.name, str(hex_file))
            
            if hex_files:
                self.log_message(f"找到 {len(hex_files)} 個 Merged HEX 檔案 (路徑: {self.merged_hex_dir})\n")
            else:
                self.log_message(f"{self.merged_hex_dir} 目錄中沒有 HEX 檔案\n")
        else:
            self.log_message(f"{self.merged_hex_dir} 目錄不存在\n")

    def load_sd_files(self):
        """載入 SoftDevice HEX 檔案"""
        self.sd_combo.clear()
        self.sd_combo.addItem("-- 選擇 SoftDevice --", None)
        
        if self.sd_hex_dir.exists():
            sd_files = sorted(self.sd_hex_dir.glob("*.hex"))
            for sd_file in sd_files:
                self.sd_combo.addItem(sd_file.name, str(sd_file))
            
            if sd_files:
                self.log_message(f"找到 {len(sd_files)} 個 SoftDevice 檔案 (路徑: {self.sd_hex_dir})\n")
        else:
            self.log_message(f"{self.sd_hex_dir} 目錄不存在\n")

    def load_app_files(self):
        """載入 Application HEX 檔案"""
        self.app_combo.clear()
        self.app_combo.addItem("-- 選擇 Application --", None)
        
        if self.app_hex_dir.exists():
            app_files = sorted(self.app_hex_dir.glob("*.hex"))
            for app_file in app_files:
                self.app_combo.addItem(app_file.name, str(app_file))
            
            if app_files:
                self.log_message(f"找到 {len(app_files)} 個 Application 檔案 (路徑: {self.app_hex_dir})\n")
        else:
            self.log_message(f"{self.app_hex_dir} 目錄不存在\n")

    def on_hex_selected(self, text):
        """Merged HEX 檔案選擇改變"""
        if self.hex_combo.currentData():
            self.hex_file = self.hex_combo.currentData()
            self.log_message(f"已選擇 Merged HEX: {text}")

    def on_sd_selected(self, text):
        """SoftDevice 選擇改變"""
        if self.sd_combo.currentData():
            self.sd_file = self.sd_combo.currentData()
            self.log_message(f"已選擇 SoftDevice: {text}")

    def on_app_selected(self, text):
        """Application 選擇改變"""
        if self.app_combo.currentData():
            self.app_file = self.app_combo.currentData()
            self.log_message(f"已選擇 Application: {text}")

    def browse_merged_file(self):
        """瀏覽 Merged HEX 檔案"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "選擇 Merged HEX 檔案",
            str(self.app_hex_dir) if self.app_hex_dir.exists() else "",
            "HEX Files (*.hex);;All Files (*.*)"
        )
        
        if file_path:
            self.hex_file = file_path
            self.hex_combo.setCurrentIndex(0)
            self.log_message(f"已選擇 Merged HEX: {Path(file_path).name}")

    def browse_sd_file(self):
        """瀏覽 SoftDevice 檔案"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "選擇 SoftDevice HEX 檔案",
            str(self.sd_hex_dir) if self.sd_hex_dir.exists() else "",
            "HEX Files (*.hex);;All Files (*.*)"
        )
        
        if file_path:
            self.sd_file = file_path
            self.sd_combo.setCurrentIndex(0)
            self.log_message(f"已選擇 SoftDevice: {Path(file_path).name}")

    def browse_app_file(self):
        """瀏覽 Application 檔案"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "選擇 Application HEX 檔案",
            str(self.project_root / "_build") if (self.project_root / "_build").exists() else "",
            "HEX Files (*.hex);;All Files (*.*)"
        )
        
        if file_path:
            self.app_file = file_path
            self.app_combo.setCurrentIndex(0)
            self.log_message(f"已選擇 Application: {Path(file_path).name}")

    def start_auto_flash(self):
        """開始自動燒錄"""
        if not self.hex_file:
            QMessageBox.warning(self, "警告", "請先選擇 Merged HEX 檔案!")
            return
        
        if not Path(self.hex_file).exists():
            QMessageBox.critical(self, "錯誤", f"檔案不存在:\n{self.hex_file}")
            return
        
        reply = QMessageBox.information(
            self,
            "自動燒錄",
            "自動燒錄將執行:\n"
            "1. Recover (恢復裝置)\n"
            "2. Erase All (擦除全部)\n"
            "3. Flash (燒錄)\n"
            "4. Reset (重置)\n\n"
            "繼續?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.set_buttons_enabled(False)
            self.progress_bar.setValue(0)
            
            self.flash_thread = FlashThread(self.hex_file, 'auto')
            self.flash_thread.output_signal.connect(self.log_message)
            self.flash_thread.progress_signal.connect(self.progress_bar.setValue)
            self.flash_thread.finished_signal.connect(self.on_operation_finished)
            self.flash_thread.start()
            
            self.statusBar().showMessage("自動燒錄中...")

    def start_flash(self):
        """開始燒錄 Merged HEX"""
        if not self.hex_file:
            QMessageBox.warning(self, "警告", "請先選擇 Merged HEX 檔案!")
            return
        
        if not Path(self.hex_file).exists():
            QMessageBox.critical(self, "錯誤", f"檔案不存在:\n{self.hex_file}")
            return
        
        self.set_buttons_enabled(False)
        self.progress_bar.setValue(0)
        
        self.flash_thread = FlashThread(self.hex_file, 'flash')
        self.flash_thread.output_signal.connect(self.log_message)
        self.flash_thread.progress_signal.connect(self.progress_bar.setValue)
        self.flash_thread.finished_signal.connect(self.on_operation_finished)
        self.flash_thread.start()
        
        self.statusBar().showMessage("燒錄中...")

    def start_flash_separate(self):
        """開始分開燒錄 SoftDevice + Application"""
        if not self.sd_file:
            QMessageBox.warning(self, "警告", "請先選擇 SoftDevice 檔案!")
            return
        
        if not self.app_file:
            QMessageBox.warning(self, "警告", "請先選擇 Application 檔案!")
            return
        
        if not Path(self.sd_file).exists():
            QMessageBox.critical(self, "錯誤", f"SoftDevice 檔案不存在:\n{self.sd_file}")
            return
        
        if not Path(self.app_file).exists():
            QMessageBox.critical(self, "錯誤", f"Application 檔案不存在:\n{self.app_file}")
            return
        
        self.set_buttons_enabled(False)
        self.progress_bar.setValue(0)
        
        self.flash_thread = FlashThread(self.app_file, 'flash_separate', self.sd_file)
        self.flash_thread.output_signal.connect(self.log_message)
        self.flash_thread.progress_signal.connect(self.progress_bar.setValue)
        self.flash_thread.finished_signal.connect(self.on_operation_finished)
        self.flash_thread.start()
        
        self.statusBar().showMessage("分開燒錄中...")

    def erase_chip(self):
        """擦除晶片"""
        reply = QMessageBox.warning(
            self,
            "擦除確認",
            "確定要擦除晶片?此操作無法復原!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.set_buttons_enabled(False)
            self.progress_bar.setValue(0)
            
            self.flash_thread = FlashThread("", 'erase')
            self.flash_thread.output_signal.connect(self.log_message)
            self.flash_thread.progress_signal.connect(self.progress_bar.setValue)
            self.flash_thread.finished_signal.connect(self.on_operation_finished)
            self.flash_thread.start()
            
            self.statusBar().showMessage("擦除中...")

    def verify_hex(self):
        """驗證 HEX 檔案"""
        if not self.hex_file:
            QMessageBox.warning(self, "警告", "請先選擇 HEX 檔案!")
            return
        
        if not Path(self.hex_file).exists():
            QMessageBox.critical(self, "錯誤", f"檔案不存在:\n{self.hex_file}")
            return
        
        self.set_buttons_enabled(False)
        self.progress_bar.setValue(0)
        
        self.flash_thread = FlashThread(self.hex_file, 'verify')
        self.flash_thread.output_signal.connect(self.log_message)
        self.flash_thread.progress_signal.connect(self.progress_bar.setValue)
        self.flash_thread.finished_signal.connect(self.on_operation_finished)
        self.flash_thread.start()
        
        self.statusBar().showMessage("驗證中...")

    def recover_device(self):
        """恢復裝置"""
        reply = QMessageBox.warning(
            self,
            "恢復裝置",
            "恢復裝置將:\n"
            "• 解除讀取保護\n"
            "• 擦除所有資料\n"
            "• 恢復裝置連接\n\n"
            "確定繼續?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.set_buttons_enabled(False)
            self.progress_bar.setValue(0)
            
            self.flash_thread = FlashThread("", 'recover')
            self.flash_thread.output_signal.connect(self.log_message)
            self.flash_thread.progress_signal.connect(self.progress_bar.setValue)
            self.flash_thread.finished_signal.connect(self.on_operation_finished)
            self.flash_thread.start()
            
            self.statusBar().showMessage("恢復中...")

    def reset_device(self):
        """重置裝置"""
        try:
            with LowLevel.API('NRF52') as api:
                api.enum_emu_snr()
                api.connect_to_emu_without_snr()
                api.sys_reset()
                self.log_message("✓ 裝置已重置\n")
                self.statusBar().showMessage("裝置已重置")
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"重置失敗: {str(e)}")

    def on_operation_finished(self, success, message):
        """操作完成"""
        self.set_buttons_enabled(True)
        
        if success:
            self.statusBar().showMessage("✓ 操作成功")
            QMessageBox.information(self, "成功", message)
        else:
            self.statusBar().showMessage("✗ 操作失敗")
            QMessageBox.critical(self, "失敗", message)

    def log_message(self, message, color="default"):
        """輸出日誌訊息"""
        self.output_text.moveCursor(QTextCursor.MoveOperation.End)
        
        # 簡化配色 - 只用黑色文字
        self.output_text.setTextColor(QColor("black"))
        
        self.output_text.insertPlainText(message)
        self.output_text.moveCursor(QTextCursor.MoveOperation.End)

    def set_buttons_enabled(self, enabled):
        """設定按鈕啟用狀態"""
        self.auto_flash_btn.setEnabled(enabled)
        self.flash_btn.setEnabled(enabled)
        self.flash_separate_btn.setEnabled(enabled)
        self.erase_btn.setEnabled(enabled)
        self.verify_btn.setEnabled(enabled)
        self.recover_btn.setEnabled(enabled)
        self.reset_btn.setEnabled(enabled)
        self.browse_merged_btn.setEnabled(enabled)
        self.browse_sd_btn.setEnabled(enabled)
        self.browse_app_btn.setEnabled(enabled)
        self.refresh_btn.setEnabled(enabled)


def main():
    """主函數"""
    app = QApplication(sys.argv)
    window = NRFFlasherGUI()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
