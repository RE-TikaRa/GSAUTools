"""
统一风格的设置页面
与主界面风格完全一致的设计
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QComboBox, QCheckBox, QGroupBox, QTimeEdit, QScrollArea, 
                             QFrame, QSizePolicy, QSpacerItem, QGridLayout, QSlider, 
                             QSpinBox, QMessageBox, QFileDialog, QButtonGroup)
from PyQt6.QtCore import Qt, QTime, pyqtSignal, QSize
from PyQt6.QtGui import QPixmap, QPainter, QColor, QFont
import os

try:
    from Module.settings.managers.theme_manager import theme_manager
    THEME_MANAGER_AVAILABLE = True
except ImportError:
    THEME_MANAGER_AVAILABLE = False
    print("主题管理器不可用")


class SettingsCard(QFrame):
    """设置卡片组件，与功能卡片风格一致"""
    
    def __init__(self, title: str, description: str = "", parent=None):
        super().__init__(parent)
        self.setObjectName("SettingsCard")
        self.setFrameStyle(QFrame.Shape.Box)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)  # 增加内边距
        layout.setSpacing(15)  # 增加间距
        
        # 标题
        self.title_label = QLabel(title)
        self.title_label.setObjectName("settingsCardTitle")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setWeight(QFont.Weight.Medium)
        self.title_label.setFont(title_font)
        layout.addWidget(self.title_label)
        
        # 描述（如果提供）
        if description:
            self.desc_label = QLabel(description)
            self.desc_label.setObjectName("settingsCardDescription")
            self.desc_label.setWordWrap(True)
            desc_font = QFont()
            desc_font.setPointSize(11)
            self.desc_label.setFont(desc_font)
            layout.addWidget(self.desc_label)
        
        # 内容区域
        self.content_layout = QVBoxLayout()
        self.content_layout.setSpacing(8)
        layout.addLayout(self.content_layout)
    
    def addWidget(self, widget):
        """添加控件到内容区域"""
        self.content_layout.addWidget(widget)
    
    def addLayout(self, layout):
        """添加布局到内容区域"""
        self.content_layout.addLayout(layout)


class ThemeCardButton(QPushButton):
    """主题卡片按钮，仿照功能卡片的样式"""
    
    clicked_with_theme = pyqtSignal(str, str)  # theme_name, variant
    
    def __init__(self, theme_name: str, variant: str, parent=None):
        super().__init__(parent)
        self.theme_name = theme_name
        self.variant = variant
        self.setCheckable(True)
        self.setObjectName("ThemeCardButton")
        self.setFixedSize(160, 120)  # 与功能卡片保持一致的大小

        # 创建内部布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 添加弹性空间
        layout.addStretch()

        # 主题名称标签
        if THEME_MANAGER_AVAILABLE:
            themes = theme_manager.get_available_themes()
            theme_info = themes.get(theme_name, {})
            theme_display_name = theme_info.get('name', theme_name)
        else:
            theme_display_name = theme_name.title()

        self.name_label = QLabel(theme_display_name)
        self.name_label.setObjectName("themeCardName")
        self.name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_font = QFont()
        name_font.setPointSize(13)  # 稍微增大字体
        name_font.setWeight(QFont.Weight.Medium)
        self.name_label.setFont(name_font)
        layout.addWidget(self.name_label)

        # 变体标签
        variant_text = "浅色" if variant == 'light' else "深色"
        self.variant_label = QLabel(variant_text)
        self.variant_label.setObjectName("themeCardVariant")
        self.variant_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        variant_font = QFont()
        variant_font.setPointSize(11)  # 稍微增大字体
        self.variant_label.setFont(variant_font)
        layout.addWidget(self.variant_label)

        # 添加弹性空间
        layout.addStretch()

        # 连接点击信号
        self.clicked.connect(self._on_clicked)

        # 连接切换信号：选中/未选中动态调整标签颜色（兜底高优先级）
        self.toggled.connect(self._apply_label_colors)
        # 初始化颜色
        self._apply_label_colors(self.isChecked())
    
    def _on_clicked(self):
        """处理点击事件"""
        self.clicked_with_theme.emit(self.theme_name, self.variant)

    def _apply_label_colors(self, checked: bool):
        """根据选中状态，强制设置标签文字颜色，避免 QSS 覆盖异常导致的发白/发灰。
        优先级：代码级样式 > QSS；未选中深色、选中白色，适配四套主题。
        """
        if checked:
            selected_text = "#ffffff"
            self.name_label.setStyleSheet(f"color: {selected_text};")
            self.variant_label.setStyleSheet(f"color: {selected_text};")
        else:
            deep_colors = {
                'morandi': '#2D2722',
                'modern': '#0f172a',
                'ocean': '#0c4a6e',
                'contrast': '#000000',
            }
            deep = deep_colors.get(self.theme_name, '#0f172a')
            self.name_label.setStyleSheet(f"color: {deep};")
            self.variant_label.setStyleSheet(f"color: {deep};")


class UnifiedSettingsPage(QWidget):
    """统一风格的设置页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("UnifiedSettingsPage")
        self._init_ui()
        self._connect_signals()
        self._load_current_settings()
    
    def _init_ui(self):
        """初始化界面"""
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # 页面标题
        title = QLabel("设置")
        title.setObjectName("settingsPageTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setWeight(QFont.Weight.Bold)
        title.setFont(title_font)
        main_layout.addWidget(title)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("settingsScrollArea")
        scroll_area.setFrameStyle(QFrame.Shape.NoFrame)
        
        # 滚动内容容器
        scroll_content = QWidget()
        scroll_content.setObjectName("settingsScrollContent")
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        scroll_layout.setSpacing(20)
        
        # 主题设置卡片
        self._create_theme_settings_card(scroll_layout)
        
        # 界面设置卡片
        self._create_interface_settings_card(scroll_layout)
        
        # 高级设置卡片
        self._create_advanced_settings_card(scroll_layout)
        
        # 添加弹性空间
        scroll_layout.addStretch()
        
        # 设置滚动区域
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
    
    def _create_theme_settings_card(self, parent_layout):
        """创建主题设置卡片"""
        card = SettingsCard("主题设置", "选择您喜欢的界面主题和颜色方案")
        
        # 主题选择区域
        theme_layout = QVBoxLayout()
        
        # 当前主题显示
        current_layout = QHBoxLayout()
        current_label = QLabel("当前主题:")
        current_label.setObjectName("settingsLabel")
        self.current_theme_label = QLabel("莫兰蒂 - 浅色")
        self.current_theme_label.setObjectName("settingsValue")
        current_layout.addWidget(current_label)
        current_layout.addWidget(self.current_theme_label)
        current_layout.addStretch()
        theme_layout.addLayout(current_layout)
        
        # 主题网格 - 使用带滚动的响应式布局
        theme_scroll_area = QScrollArea()
        theme_scroll_area.setObjectName("themeScrollArea")
        theme_scroll_area.setWidgetResizable(True)
        theme_scroll_area.setFrameStyle(QFrame.Shape.NoFrame)
        theme_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        theme_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        theme_scroll_area.setMaximumHeight(300)  # 限制最大高度，超出则显示滚动条
        
        theme_grid_widget = QWidget()
        theme_grid_widget.setObjectName("themeGridContainer")
        
        # 使用流式布局而不是网格布局，避免横向滚动
        from Module.settings.layouts.responsive_layout import ResponsiveFlowLayout
        theme_flow_layout = ResponsiveFlowLayout(theme_grid_widget)
        theme_flow_layout.setSpacing(15)  # 设置间距
        theme_flow_layout.setContentsMargins(10, 10, 10, 10)
        
        # 创建主题按钮组
        self.theme_button_group = QButtonGroup(self)
        self.theme_buttons = []
        
        if THEME_MANAGER_AVAILABLE:
            themes = theme_manager.get_available_themes()
            for theme_name in themes.keys():
                for variant in ['light', 'dark']:
                    btn = ThemeCardButton(theme_name, variant)
                    btn.clicked_with_theme.connect(self._on_theme_selected)
                    self.theme_button_group.addButton(btn)
                    self.theme_buttons.append(btn)
                    theme_flow_layout.addWidget(btn)
        
        # 设置容器大小策略
        theme_grid_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.MinimumExpanding)
        
        # 将主题卡片容器放入滚动区域
        theme_scroll_area.setWidget(theme_grid_widget)
        theme_layout.addWidget(theme_scroll_area)
        
        # 快速切换按钮
        quick_buttons_layout = QHBoxLayout()
        self.toggle_variant_btn = QPushButton("切换浅色/深色")
        self.toggle_variant_btn.setObjectName("settingsButton")
        self.toggle_variant_btn.clicked.connect(self._toggle_variant)
        quick_buttons_layout.addWidget(self.toggle_variant_btn)
        quick_buttons_layout.addStretch()
        theme_layout.addLayout(quick_buttons_layout)
        
        card.addLayout(theme_layout)
        parent_layout.addWidget(card)
    
    def _create_interface_settings_card(self, parent_layout):
        """创建界面设置卡片"""
        card = SettingsCard("界面设置", "调整界面显示和交互行为")
        
        # 自动切换设置
        auto_switch_layout = QHBoxLayout()
        self.auto_switch_checkbox = QCheckBox("启用自动主题切换")
        self.auto_switch_checkbox.setObjectName("settingsCheckBox")
        auto_switch_layout.addWidget(self.auto_switch_checkbox)
        auto_switch_layout.addStretch()
        card.addLayout(auto_switch_layout)
        
        # 时间设置
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel("浅色模式开始时间:"))
        self.light_time_edit = QTimeEdit()
        self.light_time_edit.setObjectName("settingsTimeEdit")
        self.light_time_edit.setTime(QTime(6, 0))
        time_layout.addWidget(self.light_time_edit)
        
        time_layout.addWidget(QLabel("深色模式开始时间:"))
        self.dark_time_edit = QTimeEdit()
        self.dark_time_edit.setObjectName("settingsTimeEdit")
        self.dark_time_edit.setTime(QTime(18, 0))
        time_layout.addWidget(self.dark_time_edit)
        time_layout.addStretch()
        card.addLayout(time_layout)
        
        parent_layout.addWidget(card)
    
    def _create_advanced_settings_card(self, parent_layout):
        """创建高级设置卡片"""
        card = SettingsCard("高级设置", "导入导出配置，重置设置等")
        
        # 导入导出按钮
        import_export_layout = QHBoxLayout()
        
        self.export_btn = QPushButton("导出设置")
        self.export_btn.setObjectName("settingsButton")
        self.export_btn.clicked.connect(self._export_settings)
        import_export_layout.addWidget(self.export_btn)
        
        self.import_btn = QPushButton("导入设置")
        self.import_btn.setObjectName("settingsButton")
        self.import_btn.clicked.connect(self._import_settings)
        import_export_layout.addWidget(self.import_btn)
        
        import_export_layout.addStretch()
        
        self.reset_btn = QPushButton("重置设置")
        self.reset_btn.setObjectName("settingsButtonDanger")
        self.reset_btn.clicked.connect(self._reset_settings)
        import_export_layout.addWidget(self.reset_btn)
        
        card.addLayout(import_export_layout)
        parent_layout.addWidget(card)
    
    def _connect_signals(self):
        """连接信号"""
        if THEME_MANAGER_AVAILABLE:
            # 连接主题变化信号
            theme_manager.theme_changed.connect(self._on_theme_changed)
            
            # 连接自动切换设置
            self.auto_switch_checkbox.stateChanged.connect(self._on_auto_switch_changed)
            self.light_time_edit.timeChanged.connect(self._on_time_changed)
            self.dark_time_edit.timeChanged.connect(self._on_time_changed)
    
    def _load_current_settings(self):
        """加载当前设置"""
        if not THEME_MANAGER_AVAILABLE:
            return
        
        # 获取当前主题
        current_theme, current_variant = theme_manager.get_current_theme()
        self._update_current_theme_display(current_theme, current_variant)
        
        # 设置当前主题按钮为选中状态
        for btn in self.theme_buttons:
            if btn.theme_name == current_theme and btn.variant == current_variant:
                btn.setChecked(True)
                break
        
        # 加载自动切换设置
        settings = theme_manager.settings
        self.auto_switch_checkbox.setChecked(settings.get('auto_switch_enabled', False))
        
        # 加载时间设置
        light_time_str = settings.get('light_start_time', '06:00')
        dark_time_str = settings.get('dark_start_time', '18:00')
        self.light_time_edit.setTime(QTime.fromString(light_time_str, 'hh:mm'))
        self.dark_time_edit.setTime(QTime.fromString(dark_time_str, 'hh:mm'))
    
    def _update_current_theme_display(self, theme_name: str, variant: str):
        """更新当前主题显示"""
        if THEME_MANAGER_AVAILABLE:
            themes = theme_manager.get_available_themes()
            theme_info = themes.get(theme_name, {})
            display_name = theme_info.get('name', theme_name.title())
        else:
            display_name = theme_name.title()
        
        variant_text = "浅色" if variant == 'light' else "深色"
        self.current_theme_label.setText(f"{display_name} - {variant_text}")
    
    def _on_theme_selected(self, theme_name: str, variant: str):
        """主题选择处理"""
        if THEME_MANAGER_AVAILABLE:
            theme_manager.set_theme(theme_name, variant)
    
    def _on_theme_changed(self, theme_name: str, variant: str):
        """主题变化处理"""
        self._update_current_theme_display(theme_name, variant)
        
        # 更新按钮选中状态
        for btn in self.theme_buttons:
            btn.setChecked(btn.theme_name == theme_name and btn.variant == variant)
            # 刷新标签颜色（兜底）
            if hasattr(btn, "_apply_label_colors"):
                btn._apply_label_colors(btn.isChecked())
    
    def _toggle_variant(self):
        """切换浅色/深色变体"""
        if THEME_MANAGER_AVAILABLE:
            theme_manager.toggle_variant()
    
    def _on_auto_switch_changed(self, state):
        """自动切换设置变化"""
        if THEME_MANAGER_AVAILABLE:
            enabled = state == Qt.CheckState.Checked.value
            theme_manager.set_auto_switch(enabled, 'time')
    
    def _on_time_changed(self):
        """时间设置变化"""
        if THEME_MANAGER_AVAILABLE:
            light_time = self.light_time_edit.time().toString('hh:mm')
            dark_time = self.dark_time_edit.time().toString('hh:mm')
            theme_manager.set_time_schedule(light_time, dark_time)
    
    def _export_settings(self):
        """导出设置"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出设置", "theme_settings.json", "JSON files (*.json)"
        )
        if file_path and THEME_MANAGER_AVAILABLE:
            success = theme_manager.export_theme_settings(file_path)
            if success:
                QMessageBox.information(self, "成功", "设置已导出成功！")
            else:
                QMessageBox.warning(self, "错误", "导出设置失败！")
    
    def _import_settings(self):
        """导入设置"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入设置", "", "JSON files (*.json)"
        )
        if file_path and THEME_MANAGER_AVAILABLE:
            success = theme_manager.import_theme_settings(file_path)
            if success:
                QMessageBox.information(self, "成功", "设置已导入成功！")
                self._load_current_settings()  # 重新加载设置
            else:
                QMessageBox.warning(self, "错误", "导入设置失败！")
    
    def _reset_settings(self):
        """重置设置"""
        reply = QMessageBox.question(
            self, "确认重置", "确定要重置所有设置到默认值吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes and THEME_MANAGER_AVAILABLE:
            # 重置到默认设置
            theme_manager.settings = theme_manager.default_settings.copy()
            theme_manager.save_settings()
            theme_manager.initialize_theme()
            self._load_current_settings()
            QMessageBox.information(self, "成功", "设置已重置为默认值！")


# 为了保持兼容性，创建别名
AdvancedSettingsPage = UnifiedSettingsPage
