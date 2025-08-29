"""
基础设置页面
提供简单的设置界面
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class SettingsPage(QWidget):
    """基础设置页面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settingsPage")
        self._init_ui()
        
    def _init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 页面标题
        title = QLabel("设置")
        title.setObjectName("pageTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #2D3748;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(title)
        
        # 提示信息
        info = QLabel("请使用高级设置页面进行详细配置")
        info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #718096;
                padding: 20px;
            }
        """)
        layout.addWidget(info)
        
        layout.addStretch()
