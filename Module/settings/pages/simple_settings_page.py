"""
简化的设置页面组件
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QCheckBox, QGroupBox,
                             QScrollArea, QMessageBox, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal
import os

class SimpleSettingsPage(QWidget):
    """简化的设置页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_theme = "dark"  # 默认主题
        self._setup_ui()
        self._load_current_settings()
        self._connect_signals()
        
    def _setup_ui(self):
        """设置UI"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)
        
        # 页面标题
        title = QLabel("设置")
        title.setStyleSheet("""
            font-size: 28px; 
            font-weight: bold; 
            color: #F7FAFC;
            margin-bottom: 20px;
        """)
        main_layout.addWidget(title)
        
        # 主题设置组
        theme_group = self._create_theme_group()
        main_layout.addWidget(theme_group)
        
        # 应用程序设置组
        app_group = self._create_application_group()
        main_layout.addWidget(app_group)
        
        # 操作按钮
        buttons_layout = self._create_buttons()
        main_layout.addLayout(buttons_layout)
        
        # 添加弹性空间
        main_layout.addStretch()
        
    def _create_theme_group(self) -> QGroupBox:
        """创建主题设置组"""
        group = QGroupBox("主题设置")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                color: #F7FAFC;
                border: 2px solid #4A5568;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
            }
        """)
        
        layout = QVBoxLayout(group)
        layout.setSpacing(20)
        
        # 主题选择说明
        desc_label = QLabel("选择您喜欢的界面主题:")
        desc_label.setObjectName("themeDescLabel")
        layout.addWidget(desc_label)
        
        # 创建滚动区域以支持更多主题
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setObjectName("themeScrollArea")
        
        # 主题按钮容器
        themes_container = QWidget()
        themes_container.setObjectName("themesContainer")
        
        # 尝试使用FlowLayout实现自适应布局
        flow_layout_available = False
        try:
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(__file__)))
            from MainGUI.components import FlowLayout
            themes_layout = FlowLayout(spacing=15)
            themes_layout.setContentsMargins(10, 10, 10, 10)
            themes_layout.max_columns = 6  # 最大列数
            flow_layout_available = True
            print("✅ 简单设置页面使用FlowLayout自适应布局")
        except Exception as e:
            # 备用：使用QHBoxLayout
            themes_layout = QHBoxLayout()
            themes_layout.setSpacing(15)
            themes_layout.setContentsMargins(10, 10, 10, 10)
            print(f"⚠️ FlowLayout不可用({e})，使用QHBoxLayout作为备用")
        
        themes_container.setLayout(themes_layout)
        scroll_area.setWidget(themes_container)
        
        # 扩展主题定义，支持更多主题选项
        self.themes = {
            "morandi": {"name": "Morandi\n优雅", "color": "#D3CBC5", "file": "Style/global_stylesheet.qss"},
            "blue": {"name": "蓝色\n经典", "color": "#3182CE", "file": "Style/style1.qss"},
            "green": {"name": "绿色\n自然", "color": "#10B981", "file": "Style/style2.qss"},
            "dark": {"name": "深色\n现代", "color": "#68D391", "file": "Style/style3.qss"},
            "ocean": {"name": "海洋\n清新", "color": "#0EA5E9", "file": "Style/themes/ocean/light_simple.qss"},
            "modern": {"name": "现代\n简约", "color": "#6366F1", "file": "Style/themes/modern/light_simple.qss"},
            "contrast": {"name": "高对比\n醒目", "color": "#F59E0B", "file": "Style/themes/contrast/light_simple.qss"},
        }
        
        self.theme_buttons = {}
        for theme_key, theme_info in self.themes.items():
            btn = self._create_theme_button(theme_key, theme_info)
            self.theme_buttons[theme_key] = btn
            themes_layout.addWidget(btn)
            
        # 只有在使用QHBoxLayout时才添加伸缩空间
        if not flow_layout_available and hasattr(themes_layout, 'addStretch'):
            themes_layout.addStretch()
        
        layout.addWidget(scroll_area)
        
        return group
        
    def _create_theme_button(self, theme_key: str, theme_info: dict) -> QPushButton:
        """创建主题按钮"""
        btn = QPushButton(theme_info["name"])
        btn.setFixedSize(100, 80)
        btn.setCheckable(True)
        btn.setProperty("theme_key", theme_key)
        
        # 设置样式
        btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 {theme_info['color']}, 
                                            stop:1 rgba(255,255,255,0.1));
                color: white;
                border: 2px solid #4A5568;
                border-radius: 8px;
                font-size: 11px;
                font-weight: bold;
                text-align: center;
            }}
            QPushButton:hover {{
                border-color: #68D391;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 {theme_info['color']}, 
                                            stop:1 rgba(104, 211, 145, 0.2));
            }}
            QPushButton:checked {{
                border-color: #68D391;
                border-width: 3px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                            stop:0 {theme_info['color']}, 
                                            stop:1 rgba(104, 211, 145, 0.3));
            }}
        """)
        
        btn.clicked.connect(self._on_theme_button_clicked)
        return btn
        
    def _create_application_group(self) -> QGroupBox:
        """创建应用程序设置组"""
        group = QGroupBox("应用程序设置")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                color: #F7FAFC;
                border: 2px solid #4A5568;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
            }
        """)
        
        layout = QVBoxLayout(group)
        layout.setSpacing(15)
        
        # 语言选择
        lang_layout = QHBoxLayout()
        lang_label = QLabel("界面语言:")
        lang_label.setObjectName("simpleLangLabel")
        self.language_combo = QComboBox()
        self.language_combo.setObjectName("simpleLangCombo")
        
        # 添加语言选项
        self.language_combo.addItem("中文 (简体)", "zh_CN")
        self.language_combo.addItem("English", "en_US")
        self.language_combo.addItem("日本語", "ja_JP")
            
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.language_combo)
        lang_layout.addStretch()
        layout.addLayout(lang_layout)
        
        # 自动保存设置
        self.auto_save_check = QCheckBox("启动时自动加载上次的主题设置")
        self.auto_save_check.setStyleSheet("""
            QCheckBox {
                color: #F7FAFC;
                font-size: 14px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                background-color: #2D3748;
                border: 2px solid #4A5568;
                border-radius: 4px;
            }
            QCheckBox::indicator:unchecked:hover {
                border-color: #68D391;
            }
            QCheckBox::indicator:checked {
                background-color: #68D391;
                border: 2px solid #48BB78;
                border-radius: 4px;
                image: none;
            }
        """)
        layout.addWidget(self.auto_save_check)
        
        # 显示提示
        self.show_tips_check = QCheckBox("显示操作提示和帮助信息")
        self.show_tips_check.setStyleSheet(self.auto_save_check.styleSheet())
        layout.addWidget(self.show_tips_check)
        
        return group
        
    def _create_buttons(self) -> QHBoxLayout:
        """创建操作按钮"""
        layout = QHBoxLayout()
        layout.setSpacing(15)
        
        # 重置按钮
        self.reset_btn = QPushButton("重置为默认")
        self.reset_btn.setFixedSize(120, 40)
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #E53E3E;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #C53030;
            }
            QPushButton:pressed {
                background-color: #9B2C2C;
            }
        """)
        
        # 应用按钮
        self.apply_btn = QPushButton("应用设置")
        self.apply_btn.setFixedSize(120, 40)
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #68D391;
                color: #1A202C;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #48BB78;
            }
            QPushButton:pressed {
                background-color: #38A169;
            }
        """)
        
        layout.addStretch()
        layout.addWidget(self.reset_btn)
        layout.addWidget(self.apply_btn)
        
        return layout
        
    def _load_current_settings(self):
        """加载当前设置"""
        # 检查是否有设置文件
        settings_file = "settings.json"
        if os.path.exists(settings_file):
            try:
                import json
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    
                # 加载主题设置
                self.current_theme = settings.get("theme", "dark")
                self._update_theme_selection()
                
                # 加载语言设置
                current_lang = settings.get("language", "zh_CN")
                for i in range(self.language_combo.count()):
                    if self.language_combo.itemData(i) == current_lang:
                        self.language_combo.setCurrentIndex(i)
                        break
                        
                # 加载其他设置
                self.auto_save_check.setChecked(settings.get("auto_save", True))
                self.show_tips_check.setChecked(settings.get("show_tips", True))
                
            except Exception as e:
                print(f"加载设置失败: {e}")
        else:
            # 使用默认设置
            self._update_theme_selection()
            
    def _update_theme_selection(self):
        """更新主题选择状态"""
        for theme_key, btn in self.theme_buttons.items():
            btn.setChecked(theme_key == self.current_theme)
            
    def _connect_signals(self):
        """连接信号"""
        self.apply_btn.clicked.connect(self._apply_settings)
        self.reset_btn.clicked.connect(self._reset_settings)
        
    def _on_theme_button_clicked(self):
        """主题按钮点击处理"""
        sender = self.sender()
        if sender:
            theme_key = sender.property("theme_key")
            if theme_key:
                # 更新选中状态
                for key, btn in self.theme_buttons.items():
                    btn.setChecked(key == theme_key)
                    
                self.current_theme = theme_key
                self._apply_theme_immediately(theme_key)
                
    def _apply_theme_immediately(self, theme_key: str):
        """立即应用主题"""
        if theme_key in self.themes:
            theme_info = self.themes[theme_key]
            style_file = theme_info["file"]
            
            if os.path.exists(style_file):
                try:
                    with open(style_file, "r", encoding="utf-8") as f:
                        style_content = f.read()
                        
                    from PyQt6.QtWidgets import QApplication
                    app = QApplication.instance()
                    if app:
                        app.setStyleSheet(style_content)
                        print(f"已应用主题: {theme_info['name']}")
                        
                except Exception as e:
                    print(f"应用主题失败: {e}")
        
    def _apply_settings(self):
        """应用并保存设置"""
        try:
            import json
            
            settings = {
                "theme": self.current_theme,
                "language": self.language_combo.currentData() or "zh_CN",
                "auto_save": self.auto_save_check.isChecked(),
                "show_tips": self.show_tips_check.isChecked(),
                "window_size": [800, 600],
                "window_maximized": False,
                "log_level": "INFO"
            }
            
            # 保存到文件
            with open("settings.json", 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
                
            # 显示成功消息
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setWindowTitle("设置")
            msg.setText("设置已保存成功！\n\n重启应用程序后语言设置将生效。")
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #2D3748;
                    color: #F7FAFC;
                }
                QMessageBox QPushButton {
                    background-color: #68D391;
                    color: #1A202C;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 20px;
                    font-weight: bold;
                }
                QMessageBox QPushButton:hover {
                    background-color: #48BB78;
                }
            """)
            msg.exec()
            
        except Exception as e:
            # 显示错误消息
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setWindowTitle("错误")
            msg.setText(f"保存设置失败：{e}")
            msg.exec()
        
    def _reset_settings(self):
        """重置设置"""
        # 确认对话框
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle("重置设置")
        msg.setText("确定要将所有设置重置为默认值吗？")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.No)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #2D3748;
                color: #F7FAFC;
            }
            QMessageBox QPushButton {
                background-color: #68D391;
                color: #1A202C;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-weight: bold;
                min-width: 60px;
            }
            QMessageBox QPushButton:hover {
                background-color: #48BB78;
            }
        """)
        
        if msg.exec() == QMessageBox.StandardButton.Yes:
            # 重置为默认值
            self.current_theme = "dark"
            self.language_combo.setCurrentIndex(0)  # 中文
            self.auto_save_check.setChecked(True)
            self.show_tips_check.setChecked(True)
            
            # 更新UI
            self._update_theme_selection()
            self._apply_theme_immediately(self.current_theme)
            
            # 删除设置文件
            if os.path.exists("settings.json"):
                try:
                    os.remove("settings.json")
                except:
                    pass
                    
            print("设置已重置为默认值")
