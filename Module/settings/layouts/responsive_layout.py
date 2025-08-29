"""
响应式FlowLayout改进版本
为功能页面和设置页面提供真正的自适应布局
"""

from PyQt6.QtWidgets import QLayout, QWidget, QSizePolicy
from PyQt6.QtCore import QSize, QRect, QPoint, Qt

class ResponsiveFlowLayout(QLayout):
    """响应式流式布局组件"""
    
    def __init__(self, parent=None, margin=0, spacing=12, max_columns=6):
        super().__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self._spacing = spacing
        self.itemList = []
        self.max_columns = max_columns
        self.min_item_width = 160  # 最小项目宽度
        self.item_height = 120     # 项目高度

    def __del__(self):
        while self.itemList:
            item = self.takeAt(0)

    def addItem(self, item):
        self.itemList.append(item)

    def addWidget(self, widget):
        """添加widget到布局"""
        # 确保widget有正确的父对象
        try:
            parent_widget = self.parent()
            if parent_widget and isinstance(parent_widget, QWidget):
                if widget.parent() != parent_widget:
                    widget.setParent(parent_widget)
        except:
            pass
        
        # 设置widget的基本属性
        widget.setMinimumSize(self.min_item_width, self.item_height)
        widget.setMaximumSize(300, self.item_height)  # 设置最大宽度限制
        widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        
        super().addWidget(widget)

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
        """根据宽度计算高度"""
        if not self.itemList:
            return 0
        
        # 计算可用宽度
        available_width = width - self.contentsMargins().left() - self.contentsMargins().right()
        
        # 计算动态列数
        dynamic_columns = max(1, min(self.max_columns, 
                                   (available_width + self._spacing) // (self.min_item_width + self._spacing)))
        
        # 计算行数
        rows = (len(self.itemList) + dynamic_columns - 1) // dynamic_columns
        
        # 计算总高度
        total_height = rows * self.item_height + (rows - 1) * self._spacing
        total_height += self.contentsMargins().top() + self.contentsMargins().bottom()
        
        return total_height

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        """返回布局的建议大小"""
        margins = self.contentsMargins()
        
        if not self.itemList:
            return QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        
        # 计算建议的宽度（按最大列数）
        suggested_width = (self.min_item_width + self._spacing) * self.max_columns - self._spacing
        suggested_width += margins.left() + margins.right()
        
        # 计算对应的高度
        suggested_height = self.heightForWidth(suggested_width)
        
        return QSize(suggested_width, suggested_height)

    def minimumSize(self):
        """返回最小尺寸"""
        margins = self.contentsMargins()
        
        if not self.itemList:
            return QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        
        # 最小宽度：一列的宽度
        min_width = self.min_item_width + margins.left() + margins.right()
        
        # 对应的高度
        min_height = self.heightForWidth(min_width)
        
        return QSize(min_width, min_height)

    def doLayout(self, rect, testOnly):
        """执行布局计算 - 响应式布局算法"""
        if not self.itemList:
            return 0
            
        # 计算可用宽度和动态列数
        available_width = rect.width() - self.contentsMargins().left() - self.contentsMargins().right()
        
        # 根据可用宽度计算实际列数
        dynamic_columns = max(1, min(self.max_columns, 
                                   (available_width + self._spacing) // (self.min_item_width + self._spacing)))
        
        # 计算每个项目的实际宽度（平均分配剩余空间）
        item_width = (available_width - (dynamic_columns - 1) * self._spacing) // dynamic_columns
        item_width = max(item_width, self.min_item_width)  # 确保不小于最小宽度
        
        x = rect.x() + self.contentsMargins().left()
        y = rect.y() + self.contentsMargins().top()
        col = 0
        
        for i, item in enumerate(self.itemList):
            widget = item.widget()
            
            # 使用统一的尺寸
            actual_size = QSize(item_width, self.item_height)
            
            # 检查是否需要换行
            if col >= dynamic_columns:
                col = 0
                x = rect.x() + self.contentsMargins().left()
                y += self.item_height + self._spacing

            if not testOnly:
                new_rect = QRect(QPoint(x, y), actual_size)
                item.setGeometry(new_rect)
                
                # 确保widget使用正确的大小
                if widget:
                    widget.setFixedSize(actual_size)

            x += item_width + self._spacing
            col += 1

        # 返回布局的总高度
        if self.itemList:
            rows = (len(self.itemList) + dynamic_columns - 1) // dynamic_columns
            total_height = rows * self.item_height + (rows - 1) * self._spacing
            total_height += self.contentsMargins().top() + self.contentsMargins().bottom()
            return total_height
        return 0


def patch_flow_layout(components_module):
    """修补FlowLayout以支持响应式布局"""
    try:
        # 备份原始FlowLayout
        if hasattr(components_module, 'FlowLayout'):
            components_module.OriginalFlowLayout = components_module.FlowLayout
        
        # 替换为响应式版本
        components_module.FlowLayout = ResponsiveFlowLayout
        print("✅ FlowLayout已升级为响应式版本")
        return True
    except Exception as e:
        print(f"❌ FlowLayout升级失败: {e}")
        return False
