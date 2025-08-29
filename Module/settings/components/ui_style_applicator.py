"""
UI组件样式应用工具
自动为界面组件应用统一的样式类名
"""

from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QLineEdit, QTextEdit, QComboBox, QCheckBox, QRadioButton, QGroupBox, QTabWidget
from PyQt6.QtCore import QObject

class UIStyleApplicator:
    """UI样式应用器，负责为UI组件应用统一样式"""
    
    @staticmethod
    def apply_component_styles(widget: QWidget):
        """递归应用组件样式"""
        if not widget:
            return
        
        # 应用当前组件的样式
        UIStyleApplicator._apply_single_widget_style(widget)
        
        # 递归处理子组件
        for child in widget.findChildren(QWidget):
            UIStyleApplicator._apply_single_widget_style(child)
    
    @staticmethod
    def _apply_single_widget_style(widget: QWidget):
        """为单个组件应用样式"""
        if not widget:
            return
        
        # 获取当前类名
        class_names = []
        current_classes = widget.property("class") or ""
        if current_classes:
            class_names = current_classes.split()
        
        # 根据组件类型添加基础样式类
        widget_type = type(widget).__name__
        
        # 按钮类型
        if isinstance(widget, QPushButton):
            object_name = widget.objectName()
            
            # 检查是否已有特定样式类
            if not any(cls in class_names for cls in ['primary', 'secondary', 'danger', 'card-button', 'sidebar-button']):
                # 根据objectName自动判断样式
                if 'card' in object_name.lower():
                    class_names.append('card-button')
                elif 'sidebar' in object_name.lower():
                    class_names.append('sidebar-button')
                elif 'primary' in object_name.lower() or 'main' in object_name.lower():
                    class_names.append('primary')
                elif 'secondary' in object_name.lower():
                    class_names.append('secondary')
                elif 'danger' in object_name.lower() or 'delete' in object_name.lower():
                    class_names.append('danger')
                else:
                    # 默认按钮样式
                    class_names.append('btn')
        
        # 标签类型
        elif isinstance(widget, QLabel):
            object_name = widget.objectName()
            
            if not any(cls in class_names for cls in ['title', 'subtitle', 'section-title', 'caption']):
                if object_name == 'title' or 'title' in object_name.lower():
                    class_names.append('title')
                elif 'subtitle' in object_name.lower():
                    class_names.append('subtitle')
                elif 'section' in object_name.lower() or 'header' in object_name.lower():
                    class_names.append('section-title')
                elif 'caption' in object_name.lower() or 'hint' in object_name.lower():
                    class_names.append('caption')
        
        # 应用样式类
        if class_names:
            widget.setProperty("class", " ".join(class_names))
    
    @staticmethod
    def apply_card_button_style(button: QPushButton, title: str = "", description: str = ""):
        """应用卡片按钮样式"""
        if not isinstance(button, QPushButton):
            return
        
        # 添加卡片按钮样式类
        class_names = (button.property("class") or "").split()
        if 'card-button' not in class_names:
            class_names.append('card-button')
            button.setProperty("class", " ".join(class_names))
        
        # 设置按钮文本
        if title and description:
            button.setText(f"{title}\n{description}")
        elif title:
            button.setText(title)
    
    @staticmethod
    def apply_sidebar_button_style(button: QPushButton, is_active: bool = False):
        """应用侧边栏按钮样式"""
        if not isinstance(button, QPushButton):
            return
        
        # 添加侧边栏按钮样式类
        class_names = (button.property("class") or "").split()
        if 'sidebar-button' not in class_names:
            class_names.append('sidebar-button')
        
        # 处理激活状态
        if is_active:
            if 'active' not in class_names:
                class_names.append('active')
        else:
            if 'active' in class_names:
                class_names.remove('active')
        
        button.setProperty("class", " ".join(class_names))
    
    @staticmethod
    def apply_title_style(label: QLabel, level: str = "title"):
        """应用标题样式"""
        if not isinstance(label, QLabel):
            return
        
        # 设置标题级别样式类
        valid_levels = ['title', 'subtitle', 'section-title', 'caption']
        if level not in valid_levels:
            level = 'title'
        
        class_names = (label.property("class") or "").split()
        
        # 移除其他标题级别样式
        for lvl in valid_levels:
            if lvl in class_names:
                class_names.remove(lvl)
        
        # 添加新的标题级别
        class_names.append(level)
        
        label.setProperty("class", " ".join(class_names))
        label.setObjectName(level)
    
    @staticmethod
    def apply_primary_button_style(button: QPushButton):
        """应用主要按钮样式"""
        if not isinstance(button, QPushButton):
            return
        
        class_names = (button.property("class") or "").split()
        
        # 移除其他按钮样式
        for style in ['secondary', 'danger', 'card-button', 'sidebar-button']:
            if style in class_names:
                class_names.remove(style)
        
        # 添加主要按钮样式
        if 'primary' not in class_names:
            class_names.append('primary')
        
        button.setProperty("class", " ".join(class_names))
    
    @staticmethod
    def apply_secondary_button_style(button: QPushButton):
        """应用次要按钮样式"""
        if not isinstance(button, QPushButton):
            return
        
        class_names = (button.property("class") or "").split()
        
        # 移除其他按钮样式
        for style in ['primary', 'danger', 'card-button', 'sidebar-button']:
            if style in class_names:
                class_names.remove(style)
        
        # 添加次要按钮样式
        if 'secondary' not in class_names:
            class_names.append('secondary')
        
        button.setProperty("class", " ".join(class_names))
    
    @staticmethod
    def apply_danger_button_style(button: QPushButton):
        """应用危险按钮样式"""
        if not isinstance(button, QPushButton):
            return
        
        class_names = (button.property("class") or "").split()
        
        # 移除其他按钮样式
        for style in ['primary', 'secondary', 'card-button', 'sidebar-button']:
            if style in class_names:
                class_names.remove(style)
        
        # 添加危险按钮样式
        if 'danger' not in class_names:
            class_names.append('danger')
        
        button.setProperty("class", " ".join(class_names))
    
    @staticmethod
    def refresh_widget_styles(widget: QWidget):
        """刷新组件样式，强制重新应用样式表"""
        if not widget:
            return
        
        # 强制样式更新
        widget.style().unpolish(widget)
        widget.style().polish(widget)
        widget.update()
        
        # 递归刷新子组件
        for child in widget.findChildren(QWidget):
            child.style().unpolish(child)
            child.style().polish(child)
            child.update()


def apply_theme_to_widget(widget: QWidget):
    """
    快捷函数：为组件应用主题样式
    这是一个便捷的入口函数，可以直接调用
    """
    UIStyleApplicator.apply_component_styles(widget)
    UIStyleApplicator.refresh_widget_styles(widget)


def setup_button_styles(widget: QWidget):
    """
    快捷函数：设置按钮样式
    根据按钮的objectName自动应用合适的样式
    """
    # 查找所有按钮并应用样式
    buttons = widget.findChildren(QPushButton)
    
    for button in buttons:
        object_name = button.objectName().lower()
        text = button.text().lower()
        
        # 根据名称和文本内容判断按钮类型
        if any(keyword in object_name or keyword in text for keyword in ['confirm', 'ok', 'save', 'submit', 'apply']):
            UIStyleApplicator.apply_primary_button_style(button)
        elif any(keyword in object_name or keyword in text for keyword in ['cancel', 'close', 'back']):
            UIStyleApplicator.apply_secondary_button_style(button)
        elif any(keyword in object_name or keyword in text for keyword in ['delete', 'remove', 'danger']):
            UIStyleApplicator.apply_danger_button_style(button)
        elif 'card' in object_name:
            UIStyleApplicator.apply_card_button_style(button)
        elif 'sidebar' in object_name:
            UIStyleApplicator.apply_sidebar_button_style(button)
    
    # 刷新样式
    UIStyleApplicator.refresh_widget_styles(widget)


def setup_title_styles(widget: QWidget):
    """
    快捷函数：设置标题样式
    根据QLabel的objectName自动应用合适的标题级别
    """
    labels = widget.findChildren(QLabel)
    
    for label in labels:
        object_name = label.objectName().lower()
        
        if object_name == 'title' or 'title' in object_name:
            UIStyleApplicator.apply_title_style(label, 'title')
        elif 'subtitle' in object_name:
            UIStyleApplicator.apply_title_style(label, 'subtitle')
        elif 'section' in object_name or 'header' in object_name:
            UIStyleApplicator.apply_title_style(label, 'section-title')
        elif 'caption' in object_name or 'hint' in object_name:
            UIStyleApplicator.apply_title_style(label, 'caption')
    
    # 刷新样式
    UIStyleApplicator.refresh_widget_styles(widget)
