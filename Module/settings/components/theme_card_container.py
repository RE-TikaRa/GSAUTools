"""
主题卡片响应式容器
为设置页面提供自适应的主题选择布局
"""

from PyQt6.QtWidgets import QWidget, QScrollArea, QVBoxLayout, QHBoxLayout, QGridLayout, QSizePolicy
from PyQt6.QtCore import Qt, QSize

class ResponsiveThemeContainer(QWidget):
    """响应式主题卡片容器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.theme_widgets = []
        self.min_card_width = 180
        self.card_height = 120
        self.spacing = 15
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        self.setObjectName("responsiveThemeContainer")
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setObjectName("themeScrollArea")
        
        # 内容容器
        self.content_widget = QWidget()
        self.content_widget.setObjectName("themeContentWidget")
        self.scroll_area.setWidget(self.content_widget)
        
        # 使用网格布局作为基础
        self.grid_layout = QGridLayout(self.content_widget)
        self.grid_layout.setSpacing(self.spacing)
        self.grid_layout.setContentsMargins(10, 10, 10, 10)
        
        main_layout.addWidget(self.scroll_area)
    
    def add_theme_widget(self, widget):
        """添加主题组件"""
        self.theme_widgets.append(widget)
        widget.setParent(self.content_widget)
        widget.setMinimumSize(self.min_card_width, self.card_height)
        widget.setMaximumHeight(self.card_height)
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.relayout()
    
    def clear_themes(self):
        """清空所有主题组件"""
        for widget in self.theme_widgets:
            widget.setParent(None)
        self.theme_widgets.clear()
        self.relayout()
    
    def relayout(self):
        """重新布局主题组件"""
        # 清除现有布局
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)
        
        if not self.theme_widgets:
            return
        
        # 计算列数
        available_width = self.scroll_area.viewport().width() - 20  # 减去边距
        if available_width <= 0:
            available_width = 600  # 默认宽度
        
        columns = max(1, (available_width + self.spacing) // (self.min_card_width + self.spacing))
        columns = min(columns, 6)  # 最大6列
        
        # 重新排列组件
        for i, widget in enumerate(self.theme_widgets):
            row = i // columns
            col = i % columns
            self.grid_layout.addWidget(widget, row, col)
        
        # 添加拉伸以保持紧凑布局
        self.grid_layout.setRowStretch(self.grid_layout.rowCount(), 1)
    
    def resizeEvent(self, event):
        """窗口大小改变时重新布局"""
        super().resizeEvent(event)
        # 延迟重新布局以避免频繁调用
        if hasattr(self, '_relayout_timer'):
            self._relayout_timer.stop()
        
        from PyQt6.QtCore import QTimer
        self._relayout_timer = QTimer()
        self._relayout_timer.setSingleShot(True)
        self._relayout_timer.timeout.connect(self.relayout)
        self._relayout_timer.start(100)  # 100ms延迟
    
    def sizeHint(self):
        """返回建议大小"""
        if not self.theme_widgets:
            return QSize(400, 200)
        
        # 计算基于内容的建议大小
        columns = min(6, len(self.theme_widgets))
        rows = (len(self.theme_widgets) + columns - 1) // columns
        
        width = columns * self.min_card_width + (columns - 1) * self.spacing + 20
        height = rows * self.card_height + (rows - 1) * self.spacing + 20
        height = min(height, 400)  # 限制最大高度
        
        return QSize(width, height)


class ThemeCardWidget(QWidget):
    """统一的主题卡片组件"""
    
    def __init__(self, theme_name, variant, theme_info, parent=None):
        super().__init__(parent)
        self.theme_name = theme_name
        self.variant = variant
        self.theme_info = theme_info
        self.selected = False
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        self.setObjectName("themeCard")
        self.setFixedSize(180, 120)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # 主题名称
        from PyQt6.QtWidgets import QLabel
        name_label = QLabel(f"{self.theme_info.get('name', self.theme_name)}")
        name_label.setObjectName("themeCardName")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)
        
        # 变体标签
        variant_text = "浅色模式" if self.variant == 'light' else "深色模式"
        variant_label = QLabel(variant_text)
        variant_label.setObjectName("themeCardVariant")
        variant_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(variant_label)
        
        # 颜色预览区域
        self.create_color_preview(layout)
        
        # 设置样式属性
        self.setProperty("selected", False)
        self.setProperty("themeName", self.theme_name)
        self.setProperty("themeVariant", self.variant)
    
    def create_color_preview(self, layout):
        """创建颜色预览"""
        from PyQt6.QtWidgets import QFrame, QHBoxLayout
        
        preview_frame = QFrame()
        preview_frame.setObjectName("colorPreviewFrame")
        preview_frame.setFixedHeight(30)
        
        colors_layout = QHBoxLayout(preview_frame)
        colors_layout.setContentsMargins(0, 0, 0, 0)
        colors_layout.setSpacing(2)
        
        # 根据主题获取颜色
        colors = self.get_theme_colors()
        
        for color in colors:
            color_widget = QWidget()
            color_widget.setObjectName("colorSwatch")
            color_widget.setFixedSize(20, 20)
            color_widget.setProperty("color", color)
            color_widget.setStyleSheet(f"background-color: {color}; border-radius: 10px; border: 1px solid rgba(0,0,0,0.1);")
            colors_layout.addWidget(color_widget)
        
        layout.addWidget(preview_frame)
    
    def get_theme_colors(self):
        """获取主题颜色"""
        color_schemes = {
            'morandi': {
                'light': ['#F7F5F3', '#A69C94', '#8B7E74', '#4A453F'],
                'dark': ['#2B2622', '#A69C94', '#E6DDD6', '#C7BEB5']
            },
            'modern': {
                'light': ['#FFFFFF', '#3B82F6', '#2563EB', '#1E293B'],
                'dark': ['#0F172A', '#60A5FA', '#3B82F6', '#F1F5F9']
            },
            'contrast': {
                'light': ['#FFFFFF', '#000000', '#0000FF', '#FF0000'],
                'dark': ['#000000', '#FFFFFF', '#00FFFF', '#FF0000']
            },
            'ocean': {
                'light': ['#F0F9FF', '#0EA5E9', '#0284C7', '#0C4A6E'],
                'dark': ['#082F49', '#0EA5E9', '#38BDF8', '#E0F2FE']
            }
        }
        
        return color_schemes.get(self.theme_name, {}).get(self.variant, ['#CCCCCC', '#888888', '#444444', '#000000'])
    
    def set_selected(self, selected):
        """设置选中状态"""
        self.selected = selected
        self.setProperty("selected", selected)
        self.style().polish(self)  # 强制刷新样式
    
    def mousePressEvent(self, event):
        """鼠标点击事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
    
    # 添加点击信号
    from PyQt6.QtCore import pyqtSignal
    clicked = pyqtSignal()
