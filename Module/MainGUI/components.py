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
            self.setIcon(qta.icon(icon_name))
        self.setFixedHeight(40)
        self.setIconSize(QSize(20, 20))
        
        # 移除内联样式，让主题系统完全控制
        # 只保留基本的文本对齐
        self.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding-left: 10px;
            }
        """)
        
        # 设置对象名以便主题识别
        self.setObjectName("SidebarButton")

class CardButton(QPushButton):
    """卡片式按钮组件，用于功能展示"""
    def __init__(self, text: str = "", parent=None):
        # 使用空的 QPushButton 文本，实际显示文本由内部 QLabel 管理
        super().__init__("", parent)
        self.setCheckable(True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setFixedSize(160, 120)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        # 设置对象名以便主题识别
        self.setObjectName("CardButton")

        # 内部垂直布局，用 stretch 居中图标和文字
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addStretch()

        # 图标标签（固定大小，增大为 56x56）
        self.icon_label = QLabel(self)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setFixedSize(56, 56)
        self.icon_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.icon_label.setContentsMargins(0, 0, 0, 0)
        # 设置objectName和基础样式确保背景透明
        self.icon_label.setObjectName("cardButtonIcon")
        self.icon_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
            }
        """)
        layout.addWidget(self.icon_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        # 文本标签（内部管理）
        self.text_label = QLabel(text, self)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setWordWrap(True)
        self.text_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        # 增加顶部间距，避免图标与文字靠得太近
        self.text_label.setContentsMargins(0, 8, 0, 0)
        # 设置objectName确保样式被正确应用
        self.text_label.setObjectName("cardButtonLabel")
        # 设置基础样式，让主题系统能够正确继承和覆盖
        self.text_label.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                color: inherit;
            }
        """)
        font = self.text_label.font()
        font.setPointSize(9)
        self.text_label.setFont(font)
        layout.addWidget(self.text_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        layout.addStretch()

        # 样式现在由主题系统管理，移除内联样式

    def setText(self, text: str):
        """设置内部文本标签的文本"""
        self.text_label.setText(text)

    def setIcon(self, icon):
        """设置图标，支持 QIcon、QPixmap 或具有 pixmap 方法的对象"""
        pixmap = None
        try:
            if isinstance(icon, QIcon):
                pixmap = icon.pixmap(56, 56)
            elif isinstance(icon, QPixmap):
                pixmap = icon
            elif hasattr(icon, 'pixmap'):
                pixmap = icon.pixmap(56, 56)
        except Exception:
            pixmap = None

        if pixmap:
            scaled = pixmap.scaled(56, 56, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.icon_label.setPixmap(scaled)
            self.icon_label.setVisible(True)

    def sizeHint(self):
        return QSize(160, 120)

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
            btn.setIcon(qta.icon(icon_name))
            btn.setIconSize(QSize(16, 16))
        
        # 设置objectName让主题系统能识别
        btn.setObjectName("SubMenuButton")
        
        # 移除内联样式，让主题系统完全控制
        btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding-left: 25px;
            }
        """)
        self._layout.addWidget(btn)
        return btn

class FlowLayout(QLayout):
    """自适应流式布局组件 - 支持响应式设计"""
    def __init__(self, parent=None, margin=0, spacing=12, max_columns=6):
        super().__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self._spacing = spacing
        self.itemList = []
        self.max_columns = max_columns  # 增加默认最大列数
        self.min_item_width = 160  # 最小项目宽度
        self.item_height = 120     # 固定项目高度

    def __del__(self):
        while self.itemList:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def addWidget(self, widget):
        print(f"\n添加widget到FlowLayout: {widget}")
        print(f"- Widget类型: {type(widget)}")
        print(f"- Widget大小: {widget.size()}")
        print(f"- Widget sizeHint: {widget.sizeHint()}")
        print(f"- Widget minimumSize: {widget.minimumSize()}")
        print(f"- Widget maximumSize: {widget.maximumSize()}")
        print(f"- Widget 可见性: {widget.isVisible()}")
        
        # ensure the widget is parented to the layout's parent widget so it is not a top-level window
        try:
            parent_widget = self.parent()
            if parent_widget is not None:
                widget.setParent(parent_widget)
        except Exception:
            pass

        # ensure widget is visible and add to layout
        widget.setVisible(True)
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
        print(f"\n=== FlowLayout 布局计算 ===")
        print(f"布局区域: {rect}")
        print(f"布局模式: {'测试' if testOnly else '实际'}")
        
        x = rect.x() + self.contentsMargins().left()
        y = rect.y() + self.contentsMargins().top()
        lineHeight = 0
        spaceX = self._spacing
        spaceY = self._spacing
        col = 0
        max_right = rect.right() - self.contentsMargins().right()
        
        print(f"初始位置: x={x}, y={y}")
        print(f"间距: 水平={spaceX}, 垂直={spaceY}")
        print(f"最大右边界: {max_right}")
        print(f"项目数量: {len(self.itemList)}")

        for i, item in enumerate(self.itemList):
            widget = item.widget()
            if widget:
                s = widget.size()
                if s.isEmpty():
                    s = widget.sizeHint()
                    if s.isEmpty():
                        s = QSize(160, 120)  # 默认大小
            else:
                s = item.sizeHint()
            
            w = s.width()
            h = s.height()
            
            print(f"\n项目 {i}:")
            print(f"- 建议大小: {s}")
            if widget:
                print(f"- Widget大小: {widget.size()}")
                print(f"- Widget sizeHint: {widget.sizeHint()}")
                print(f"- Widget minimumSize: {widget.minimumSize()}")
            
            if col >= self.max_columns or (x + w > max_right and col > 0):
                x = rect.x() + self.contentsMargins().left()
                y = y + lineHeight + spaceY
                lineHeight = 0
                col = 0
                print(f"- 换行: 新位置 x={x}, y={y}")

            if not testOnly:
                new_rect = QRect(QPoint(x, y), s)
                item.setGeometry(new_rect)
                print(f"- 设置几何: {new_rect}")
                if widget:
                    print(f"- 项目可见性: {widget.isVisible()}")
                    print(f"- 项目已启用: {widget.isEnabled()}")
                    print(f"- 设置后的Widget大小: {widget.size()}")

            x = x + w + spaceX
            lineHeight = max(lineHeight, h)
            col += 1
            print(f"- 下一个位置: x={x}, y={y}, 列={col}")

        final_height = y + lineHeight - rect.y() + self.contentsMargins().bottom()
        print(f"\n最终布局高度: {final_height}")
        print("=== FlowLayout 布局计算结束 ===\n")
        return final_height

    def sizeHint(self):
        """返回布局的建议大小"""
        margins = self.contentsMargins()
        size = QSize()
        col_count = min(len(self.itemList), self.max_columns)
        
        if col_count > 0:
            first_item = self.itemList[0].widget()
            if first_item:
                item_size = first_item.sizeHint()
                if not item_size.isEmpty():
                    total_width = (item_size.width() + self._spacing) * col_count - self._spacing
                    total_height = (item_size.height() + self._spacing) * ((len(self.itemList) + col_count - 1) // col_count) - self._spacing
                    size = QSize(total_width, total_height)
        
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size
