"""
样式管理器 - 管理应用程序的主题样式
"""
import os
from PyQt6.QtWidgets import QApplication

class StyleManager:
    """样式管理器类"""
    
    STYLES = {
        1: {
            "name": "经典蓝色主题",
            "file": "Style/style1.qss",
            "description": "清新的蓝色主题，适合日常办公"
        },
        2: {
            "name": "绿色自然主题", 
            "file": "Style/style2.qss",
            "description": "自然绿色主题，护眼舒适"
        },
        3: {
            "name": "现代深色主题",
            "file": "Style/style3.qss", 
            "description": "现代深色主题，时尚专业"
        }
    }
    
    def __init__(self):
        self.current_style = 3  # 默认使用第三个样式
        
    def apply_style(self, style_id: int):
        """应用指定的样式"""
        if style_id not in self.STYLES:
            print(f"样式 ID {style_id} 不存在")
            return False
            
        style_info = self.STYLES[style_id]
        style_file = style_info["file"]
        
        if not os.path.exists(style_file):
            print(f"样式文件 {style_file} 不存在")
            return False
            
        try:
            with open(style_file, "r", encoding="utf-8") as f:
                style_content = f.read()
                
            app = QApplication.instance()
            if app:
                app.setStyleSheet(style_content)
                self.current_style = style_id
                print(f"已应用样式: {style_info['name']}")
                return True
        except Exception as e:
            print(f"应用样式失败: {e}")
            return False
            
    def get_current_style(self):
        """获取当前样式信息"""
        return self.STYLES.get(self.current_style, {})
        
    def get_available_styles(self):
        """获取所有可用样式"""
        return self.STYLES
        
    def switch_to_next_style(self):
        """切换到下一个样式"""
        next_style = (self.current_style % len(self.STYLES)) + 1
        return self.apply_style(next_style)

# 全局样式管理器实例
style_manager = StyleManager()
