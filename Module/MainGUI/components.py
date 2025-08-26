from PyQt6.QtWidgets import (QPushButton, QWidget, QVBoxLayout, 
                           QLayout, QWidgetItem, QButtonGroup, QLabel, QSizePolicy)
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QRect, QPoint
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtSvgWidgets import QSvgWidget
import qtawesome as qta

class SidebarButton(QPushButton):
    """侧边栏按钮组件"""
    def __init__(self, text="", icon_name=None, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        if icon_name:
            self.setIcon(QIcon(qta.icon(icon_name).pixmap(20, 20)))
        self.setFixedHeight(40)
        self.setIconSize(QSize(20, 20))

class CardButton(QPushButton):
    """卡片式按钮组件，用于功能展示"""
    def __init__(self, text="", icon_pixmap=None, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setFixedSize(160, 120)

        # 样式设置
        self.setStyleSheet('''
            QPushButton {
                background: white;
                border-radius: 8px;
                border: 1px solid #e6eaee;
                padding: 0px;
                color: #333333;
            }
            QPushButton:checked {
                border: 1px solid #bda9a2;
                background: #bda9a2;
                color: #2f2d2b;
            }
            QPushButton:hover {
                background: #f6f6f6;
            }
            QPushButton:checked QLabel { color: #2f2d2b; }
        ''')

        # 内容布局
        container = QWidget(self)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(10, 15, 10, 10)
        container_layout.setSpacing(8)

        # 图标标签
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(64, 64)
        self.icon_label.setStyleSheet("background: transparent; border: none;")
        if icon_pixmap:
            scaled_pixmap = icon_pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, 
                                             Qt.TransformationMode.SmoothTransformation)
            self.icon_label.setPixmap(scaled_pixmap)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 文本标签
        self.text_label = QLabel(text)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.text_label.font()
        font.setPointSize(9)
        self.text_label.setFont(font)

        # 添加到容器
        container_layout.addWidget(self.icon_label, 0, Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self.text_label, 0, Qt.AlignmentFlag.AlignCenter)

        container.setStyleSheet("background: transparent;")
        container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        container.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container, 0, Qt.AlignmentFlag.AlignCenter)

    def setIconPixmap(self, pixmap):
        """设置按钮图标"""
        self.icon_label.setPixmap(pixmap)

class SubMenu(QWidget):
    """子菜单组件"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self.setVisible(False)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

    def addButton(self, text, icon_name=None):
        """添加子菜单按钮"""
        btn = QPushButton(text)
        btn.setFixedHeight(30)
        btn.setCheckable(True)
        if icon_name:
            btn.setIcon(QIcon(qta.icon(icon_name).pixmap(16, 16)))
            btn.setIconSize(QSize(16, 16))
        btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding-left: 25px;
                background: transparent;
                color: #f3efea;
                border: none;
            }
            QPushButton:hover { background-color: rgba(255,255,255,0.06); }
            QPushButton:checked { background-color: #bda9a2; color: #2f2d2b; }
        """)
        self._layout.addWidget(btn)
        return btn

class FlowLayout(QLayout):
    """流式布局组件"""
    def __init__(self, parent=None, margin=0, spacing=12, max_columns=3):
        super().__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self._spacing = spacing
        self.itemList = []
        self.max_columns = max_columns

    def __del__(self):
        while self.itemList:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def addWidget(self, widget):
        self.addItem(QWidgetItem(widget))

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x() + self.contentsMargins().left()
        y = rect.y() + self.contentsMargins().top()
        lineHeight = 0
        spaceX = self._spacing
        spaceY = self._spacing
        col = 0
        max_right = rect.right() - self.contentsMargins().right()

        for item in self.itemList:
            s = item.sizeHint()
            w = s.width()
            h = s.height()

            if col >= self.max_columns or (x + w > max_right and col > 0):
                x = rect.x() + self.contentsMargins().left()
                y = y + lineHeight + spaceY
                lineHeight = 0
                col = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), s))

            x = x + w + spaceX
            lineHeight = max(lineHeight, h)
            col += 1

        return y + lineHeight - rect.y() + self.contentsMargins().bottom()
