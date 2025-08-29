"""
增强的设置页面
支持主题管理、自动切换、时间设置等功能
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QComboBox, QCheckBox, QGroupBox, QTimeEdit, QTabWidget,
                             QScrollArea, QFrame, QSizePolicy, QSpacerItem, QGridLayout,
                             QSlider, QSpinBox, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, QTime, pyqtSignal
from PyQt6.QtGui import QPixmap, QPainter, QColor
import os

try:
    from Module.settings.managers.theme_manager import theme_manager
except ImportError:
    # 如果导入失败，创建一个简单的占位符
    class ThemeManager:
        def __init__(self):
            self.settings = {}
            self.default_settings = {}
        
        def get_available_themes(self):
            return {
                'morandi': {'name': '莫兰蒂', 'description': '温暖优雅'},
                'modern': {'name': '现代', 'description': '简洁现代'},
                'contrast': {'name': '高对比', 'description': '高对比度'},
                'ocean': {'name': '海洋', 'description': '清新海洋蓝'}
            }
        
        def get_current_theme(self):
            return 'morandi', 'light'
        
        def set_theme(self, theme, variant):
            print(f"设置主题: {theme} - {variant}")
        
        def toggle_variant(self):
            print("切换变体")
        
        def set_auto_switch(self, enabled, mode):
            print(f"设置自动切换: {enabled}, 模式: {mode}")
        
        def set_time_schedule(self, light_time, dark_time):
            print(f"设置时间: {light_time} - {dark_time}")
        
        def export_theme_settings(self, file_path):
            print(f"导出设置到: {file_path}")
            return True
        
        def import_theme_settings(self, file_path):
            print(f"从文件导入设置: {file_path}")
            return True
        
        def save_settings(self):
            print("保存设置")
        
        def initialize_theme(self):
            print("初始化主题")
    
    theme_manager = ThemeManager()


class ThemePreviewWidget(QWidget):
    """主题预览组件"""
    
    def __init__(self, theme_name: str, variant: str, parent=None):
        super().__init__(parent)
        self.theme_name = theme_name
        self.variant = variant
        self.setFixedSize(200, 120)
        self.setObjectName("themePreviewWidget")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # 创建预览布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # 主题名称
        theme_info = theme_manager.get_available_themes().get(theme_name, {})
        name_label = QLabel(f"{theme_info.get('name', theme_name)}")
        name_label.setObjectName("themeNameLabel")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 14px;
                color: #2D3748;
                background: transparent;
                border: none;
                padding: 2px;
            }
        """)
        layout.addWidget(name_label)
        
        # 变体标签
        variant_label = QLabel("浅色模式" if variant == 'light' else "深色模式")
        variant_label.setObjectName("themeVariantLabel")
        variant_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        variant_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #718096;
                background: transparent;
                border: none;
                padding: 2px;
            }
        """)
        layout.addWidget(variant_label)
        
        # 颜色预览
        self.create_color_preview(layout)
        
        # 设置整个卡片的样式
        self.update_card_style()
    
    def update_card_style(self):
        """更新卡片样式"""
        base_style = """
            QWidget[objectName="themePreviewWidget"] {
                border: 2px solid #E2E8F0;
                border-radius: 12px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #FFFFFF, stop:1 #F7FAFC);
                margin: 2px;
            }
            QWidget[objectName="themePreviewWidget"]:hover {
                border-color: #3182CE;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #F7FAFC, stop:1 #EDF2F7);
            }
        """
        
        # 根据主题变体调整卡片颜色
        if self.variant == 'dark':
            base_style += """
                QWidget[objectName="themePreviewWidget"] {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #2D3748, stop:1 #1A202C);
                }
                QWidget[objectName="themePreviewWidget"]:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #4A5568, stop:1 #2D3748);
                }
            """
            # 深色模式下的文字颜色调整
            self.findChild(QLabel, "themeNameLabel").setStyleSheet("""
                QLabel {
                    font-weight: bold;
                    font-size: 14px;
                    color: #F7FAFC;
                    background: transparent;
                    border: none;
                    padding: 2px;
                }
            """)
            self.findChild(QLabel, "themeVariantLabel").setStyleSheet("""
                QLabel {
                    font-size: 11px;
                    color: #A0AEC0;
                    background: transparent;
                    border: none;
                    padding: 2px;
                }
            """)
        
        self.setStyleSheet(base_style)
    
    def create_color_preview(self, layout):
        """创建颜色预览"""
        colors_frame = QFrame()
        colors_frame.setObjectName("colorPreviewFrame")
        colors_frame.setFixedHeight(30)
        colors_layout = QHBoxLayout(colors_frame)
        colors_layout.setContentsMargins(5, 5, 5, 5)
        colors_layout.setSpacing(4)
        
        # 根据主题和变体显示不同的颜色
        colors = self.get_theme_colors()
        
        for i, color in enumerate(colors):
            color_widget = QWidget()
            color_widget.setFixedSize(18, 18)
            color_widget.setObjectName(f"colorPreview_{i}")
            color_widget.setStyleSheet(f"""
                QWidget {{
                    background-color: {color};
                    border-radius: 9px;
                    border: 1px solid rgba(0,0,0,0.1);
                }}
                QWidget:hover {{
                    border: 2px solid #3182CE;
                }}
            """)
            color_widget.setToolTip(f"颜色: {color}")
            colors_layout.addWidget(color_widget)
        
        layout.addWidget(colors_frame)
    
    def get_theme_colors(self):
        """获取主题颜色"""
        if self.theme_name == 'morandi':
            if self.variant == 'light':
                return ['#F7F5F3', '#A69C94', '#8B7E74', '#4A453F']
            else:
                return ['#2B2622', '#A69C94', '#E6DDD6', '#C7BEB5']
        elif self.theme_name == 'modern':
            if self.variant == 'light':
                return ['#FFFFFF', '#3B82F6', '#2563EB', '#1E293B']
            else:
                return ['#0F172A', '#60A5FA', '#3B82F6', '#F1F5F9']
        elif self.theme_name == 'contrast':
            if self.variant == 'light':
                return ['#FFFFFF', '#000000', '#0000FF', '#FF0000']
            else:
                return ['#000000', '#FFFFFF', '#00FFFF', '#FF0000']
        elif self.theme_name == 'ocean':
            if self.variant == 'light':
                return ['#F0F9FF', '#0EA5E9', '#0284C7', '#0C4A6E']
            else:
                return ['#082F49', '#0EA5E9', '#38BDF8', '#E0F2FE']
        else:
            return ['#E2E8F0', '#A0AEC0', '#718096', '#2D3748']
    
    def mousePressEvent(self, event):
        """点击选择主题"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 向上遍历找到 AdvancedSettingsPage 实例
            parent = self.parent()
            while parent and not isinstance(parent, AdvancedSettingsPage):
                parent = parent.parent()
            
            if parent and hasattr(parent, 'select_theme'):
                parent.select_theme(self.theme_name, self.variant)


class AdvancedSettingsPage(QWidget):
    """增强的设置页面"""
    
    # 信号
    theme_changed = pyqtSignal(str, str)  # 主题名称, 变体
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.connect_signals()
        self.load_current_settings()
    
    def setup_ui(self):
        """设置用户界面"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(0)
        
        # 页面标题
        title = QLabel("高级设置")
        title.setObjectName("pageTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)
        
        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 滚动内容
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(25)
        
        # 创建各个设置组
        scroll_layout.addWidget(self.create_theme_selection_group())
        scroll_layout.addWidget(self.create_auto_switch_group())
        scroll_layout.addWidget(self.create_time_schedule_group())
        scroll_layout.addWidget(self.create_appearance_group())
        scroll_layout.addWidget(self.create_import_export_group())
        
        # 添加弹性空间
        scroll_layout.addStretch()
        
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll)
    
    def create_theme_selection_group(self):
        """创建主题选择组 - 自适应布局"""
        group = QGroupBox("主题选择")
        group.setObjectName("themeSelectionGroup")
        group.setStyleSheet("""
            QGroupBox#themeSelectionGroup {
                font-size: 16px;
                font-weight: bold;
                color: #2D3748;
                border: 2px solid #E2E8F0;
                border-radius: 12px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: rgba(255, 255, 255, 0.8);
            }
            QGroupBox#themeSelectionGroup::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 10px 0 10px;
                background-color: rgba(255, 255, 255, 0.9);
                border-radius: 5px;
            }
        """)
        layout = QVBoxLayout(group)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 20, 15, 15)
        
        # 添加描述文字
        desc_label = QLabel("选择您喜欢的主题风格和模式")
        desc_label.setObjectName("themeDescLabel")
        desc_label.setStyleSheet("""
            QLabel#themeDescLabel {
                color: #718096;
                font-size: 14px;
                padding: 5px 10px;
                background-color: rgba(247, 250, 252, 0.8);
                border-radius: 6px;
                border: 1px solid #E2E8F0;
            }
        """)
        layout.addWidget(desc_label)
        
        # 主题预览容器 - 使用滚动区域支持更多主题
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setObjectName("themeScrollArea")
        scroll_area.setStyleSheet("""
            QScrollArea#themeScrollArea {
                border: 1px solid #CBD5E0;
                border-radius: 8px;
                background-color: #F7FAFC;
                padding: 5px;
            }
            QScrollBar:vertical {
                background-color: #EDF2F7;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #A0AEC0;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #718096;
            }
        """)
        
        # 主题预览容器
        themes_container = QWidget()
        themes_container.setObjectName("themesContainer")
        themes_container.setStyleSheet("""
            QWidget#themesContainer {
                background-color: transparent;
                border: none;
            }
        """)
        
        # 尝试导入FlowLayout来实现自适应布局
        flow_layout_available = False
        try:
            import sys
            sys.path.append(os.path.dirname(os.path.dirname(__file__)))
            from MainGUI.components import FlowLayout
            themes_layout = FlowLayout(spacing=15)
            themes_layout.setContentsMargins(15, 15, 15, 15)
            themes_layout.max_columns = 8  # 最大列数，会根据窗口宽度自动调整
            flow_layout_available = True
            print("✅ 使用FlowLayout进行主题卡片自适应布局")
        except Exception as e:
            # 如果FlowLayout不可用，使用QGridLayout作为备用
            themes_layout = QGridLayout()
            themes_layout.setSpacing(15)
            themes_layout.setContentsMargins(15, 15, 15, 15)
            flow_layout_available = False
            print(f"⚠️ FlowLayout不可用({e})，使用QGridLayout作为备用布局")
        
        themes_container.setLayout(themes_layout)
        scroll_area.setWidget(themes_container)
        
        themes = theme_manager.get_available_themes()
        
        # 创建主题预览卡片
        if flow_layout_available:
            # FlowLayout - 自适应布局
            for theme_name, theme_info in themes.items():
                # 浅色变体
                light_preview = ThemePreviewWidget(theme_name, 'light', self)
                light_preview.setToolTip(f"{theme_info.get('name', theme_name)} - 浅色模式")
                themes_layout.addWidget(light_preview)
                
                # 深色变体
                dark_preview = ThemePreviewWidget(theme_name, 'dark', self)
                dark_preview.setToolTip(f"{theme_info.get('name', theme_name)} - 深色模式")
                themes_layout.addWidget(dark_preview)
        else:
            # QGridLayout - 固定网格布局（备用）
            row, col = 0, 0
            max_cols = 4  # 每行最多4个卡片
            for theme_name, theme_info in themes.items():
                # 浅色变体
                light_preview = ThemePreviewWidget(theme_name, 'light', self)
                light_preview.setToolTip(f"{theme_info.get('name', theme_name)} - 浅色模式")
                if isinstance(themes_layout, QGridLayout):
                    themes_layout.addWidget(light_preview, row, col)
                else:
                    themes_layout.addWidget(light_preview)
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
                
                # 深色变体
                dark_preview = ThemePreviewWidget(theme_name, 'dark', self)
                dark_preview.setToolTip(f"{theme_info.get('name', theme_name)} - 深色模式")
                if isinstance(themes_layout, QGridLayout):
                    themes_layout.addWidget(dark_preview, row, col)
                else:
                    themes_layout.addWidget(dark_preview)
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
        
        layout.addWidget(scroll_area)
        
        # 当前主题信息
        self.current_theme_label = QLabel()
        self.current_theme_label.setObjectName("currentThemeLabel")
        layout.addWidget(self.current_theme_label)
        
        # 快速切换按钮
        buttons_layout = QHBoxLayout()
        
        self.variant_toggle_btn = QPushButton("切换深色/浅色")
        self.variant_toggle_btn.clicked.connect(self.toggle_variant)
        buttons_layout.addWidget(self.variant_toggle_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        return group
    
    def create_auto_switch_group(self):
        """创建自动切换组"""
        group = QGroupBox("自动切换")
        layout = QVBoxLayout(group)
        
        # 启用自动切换
        self.auto_switch_checkbox = QCheckBox("启用主题自动切换")
        self.auto_switch_checkbox.stateChanged.connect(self.on_auto_switch_changed)
        layout.addWidget(self.auto_switch_checkbox)
        
        # 切换模式
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("切换模式:"))
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["根据时间", "跟随系统"])
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        mode_layout.addWidget(self.mode_combo)
        
        mode_layout.addStretch()
        layout.addLayout(mode_layout)
        
        return group
    
    def create_time_schedule_group(self):
        """创建时间计划组"""
        self.time_group = QGroupBox("时间计划")
        layout = QVBoxLayout(self.time_group)
        
        # 浅色模式时间
        light_layout = QHBoxLayout()
        light_layout.addWidget(QLabel("浅色模式开始时间:"))
        
        self.light_time_edit = QTimeEdit()
        self.light_time_edit.setDisplayFormat("HH:mm")
        self.light_time_edit.setTime(QTime(6, 0))
        self.light_time_edit.timeChanged.connect(self.on_time_changed)
        light_layout.addWidget(self.light_time_edit)
        
        light_layout.addStretch()
        layout.addLayout(light_layout)
        
        # 深色模式时间
        dark_layout = QHBoxLayout()
        dark_layout.addWidget(QLabel("深色模式开始时间:"))
        
        self.dark_time_edit = QTimeEdit()
        self.dark_time_edit.setDisplayFormat("HH:mm")
        self.dark_time_edit.setTime(QTime(18, 0))
        self.dark_time_edit.timeChanged.connect(self.on_time_changed)
        dark_layout.addWidget(self.dark_time_edit)
        
        dark_layout.addStretch()
        layout.addLayout(dark_layout)
        
        return self.time_group
    
    def create_appearance_group(self):
        """创建外观设置组"""
        group = QGroupBox("外观设置")
        layout = QVBoxLayout(group)
        
        # 字体大小
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("字体大小:"))
        
        self.font_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.font_size_slider.setMinimum(12)
        self.font_size_slider.setMaximum(20)
        self.font_size_slider.setValue(14)
        font_layout.addWidget(self.font_size_slider)
        
        self.font_size_label = QLabel("14px")
        self.font_size_slider.valueChanged.connect(lambda v: self.font_size_label.setText(f"{v}px"))
        font_layout.addWidget(self.font_size_label)
        
        layout.addLayout(font_layout)
        
        # 动画效果
        self.animation_checkbox = QCheckBox("启用动画效果")
        self.animation_checkbox.setChecked(True)
        layout.addWidget(self.animation_checkbox)
        
        # 紧凑模式
        self.compact_checkbox = QCheckBox("紧凑模式")
        layout.addWidget(self.compact_checkbox)
        
        return group
    
    def create_import_export_group(self):
        """创建导入导出组"""
        group = QGroupBox("配置管理")
        layout = QVBoxLayout(group)
        
        buttons_layout = QHBoxLayout()
        
        # 导出配置
        export_btn = QPushButton("导出主题配置")
        export_btn.clicked.connect(self.export_settings)
        buttons_layout.addWidget(export_btn)
        
        # 导入配置
        import_btn = QPushButton("导入主题配置")
        import_btn.clicked.connect(self.import_settings)
        buttons_layout.addWidget(import_btn)
        
        # 重置配置
        reset_btn = QPushButton("重置为默认")
        reset_btn.clicked.connect(self.reset_settings)
        buttons_layout.addWidget(reset_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)
        
        return group
    
    def connect_signals(self):
        """连接信号"""
        # 连接主题管理器信号 (如果存在)
        try:
            if hasattr(theme_manager, 'theme_changed'):
                signal = getattr(theme_manager, 'theme_changed', None)
                if signal and hasattr(signal, 'connect'):
                    signal.connect(self.on_theme_changed)
        except:
            pass
        
        try:
            if hasattr(theme_manager, 'auto_switch_toggled'):
                signal = getattr(theme_manager, 'auto_switch_toggled', None)
                if signal and hasattr(signal, 'connect'):
                    signal.connect(self.on_auto_switch_toggled)
        except:
            pass
    
    def load_current_settings(self):
        """加载当前设置"""
        if hasattr(theme_manager, 'settings'):
            settings = theme_manager.settings
            
            # 更新自动切换状态
            self.auto_switch_checkbox.setChecked(settings.get('auto_switch_enabled', False))
            
            # 更新模式选择
            mode = settings.get('auto_switch_mode', 'time')
            self.mode_combo.setCurrentText("根据时间" if mode == 'time' else "跟随系统")
            
            # 更新时间设置
            light_time = settings.get('light_start_time', '06:00')
            dark_time = settings.get('dark_start_time', '18:00')
            
            try:
                hour, minute = map(int, light_time.split(':'))
                self.light_time_edit.setTime(QTime(hour, minute))
            except:
                pass
            
            try:
                hour, minute = map(int, dark_time.split(':'))
                self.dark_time_edit.setTime(QTime(hour, minute))
            except:
                pass
        
        # 更新当前主题显示
        self.update_current_theme_display()
        
        # 更新时间组的可见性
        self.update_time_group_visibility()
    
    def update_current_theme_display(self):
        """更新当前主题显示"""
        if hasattr(theme_manager, 'get_current_theme'):
            theme_name, variant = theme_manager.get_current_theme()
            themes = theme_manager.get_available_themes()
            theme_info = themes.get(theme_name, {})
            
            variant_text = "浅色" if variant == 'light' else "深色"
            text = f"当前主题: {theme_info.get('name', theme_name)} - {variant_text}"
            
            if 'description' in theme_info:
                text += f"\n{theme_info['description']}"
            
            self.current_theme_label.setText(text)
    
    def update_time_group_visibility(self):
        """更新时间组的可见性"""
        is_time_mode = self.mode_combo.currentText() == "根据时间"
        is_auto_enabled = self.auto_switch_checkbox.isChecked()
        self.time_group.setVisible(is_time_mode and is_auto_enabled)
    
    def select_theme(self, theme_name: str, variant: str):
        """选择主题"""
        if hasattr(theme_manager, 'set_theme'):
            theme_manager.set_theme(theme_name, variant)
        self.theme_changed.emit(theme_name, variant)
    
    def toggle_variant(self):
        """切换深色/浅色变体"""
        if hasattr(theme_manager, 'toggle_variant'):
            theme_manager.toggle_variant()
    
    def on_auto_switch_changed(self, checked):
        """自动切换状态改变"""
        if hasattr(theme_manager, 'set_auto_switch'):
            mode = 'time' if self.mode_combo.currentText() == "根据时间" else 'system'
            theme_manager.set_auto_switch(checked, mode)
        
        self.update_time_group_visibility()
    
    def on_mode_changed(self, mode_text):
        """切换模式改变"""
        if hasattr(theme_manager, 'set_auto_switch') and self.auto_switch_checkbox.isChecked():
            mode = 'time' if mode_text == "根据时间" else 'system'
            theme_manager.set_auto_switch(True, mode)
        
        self.update_time_group_visibility()
    
    def on_time_changed(self):
        """时间改变"""
        if hasattr(theme_manager, 'set_time_schedule'):
            light_time = self.light_time_edit.time().toString("HH:mm")
            dark_time = self.dark_time_edit.time().toString("HH:mm")
            theme_manager.set_time_schedule(light_time, dark_time)
    
    def on_theme_changed(self, theme_name: str, variant: str):
        """主题改变回调"""
        self.update_current_theme_display()
    
    def on_auto_switch_toggled(self, enabled: bool):
        """自动切换状态改变回调"""
        self.auto_switch_checkbox.setChecked(enabled)
        self.update_time_group_visibility()
    
    def export_settings(self):
        """导出设置"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出主题配置", "theme_config.json", "JSON Files (*.json)"
        )
        
        if file_path and hasattr(theme_manager, 'export_theme_settings'):
            if theme_manager.export_theme_settings(file_path):
                QMessageBox.information(self, "成功", "主题配置已导出成功！")
            else:
                QMessageBox.warning(self, "错误", "导出主题配置失败！")
    
    def import_settings(self):
        """导入设置"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入主题配置", "", "JSON Files (*.json)"
        )
        
        if file_path and hasattr(theme_manager, 'import_theme_settings'):
            if theme_manager.import_theme_settings(file_path):
                QMessageBox.information(self, "成功", "主题配置已导入成功！")
                self.load_current_settings()  # 重新加载设置
            else:
                QMessageBox.warning(self, "错误", "导入主题配置失败！")
    
    def reset_settings(self):
        """重置设置"""
        reply = QMessageBox.question(
            self, "确认重置", "确定要重置所有主题设置为默认值吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 这里可以实现重置逻辑
            if hasattr(theme_manager, 'settings') and hasattr(theme_manager, 'default_settings'):
                theme_manager.settings = theme_manager.default_settings.copy()
                theme_manager.save_settings()
                theme_manager.initialize_theme()
                self.load_current_settings()
                QMessageBox.information(self, "成功", "设置已重置为默认值！")
