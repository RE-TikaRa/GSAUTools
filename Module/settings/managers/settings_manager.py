"""
设置管理器 - 管理应用程序的配置和设置
"""
import json
import os
from typing import Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication

class SettingsManager(QObject):
    """设置管理器类"""
    
    # 信号
    settings_changed = pyqtSignal(str, object)  # 设置项名称, 新值
    theme_changed = pyqtSignal(str)  # 主题名称
    
    # 主题配置
    THEMES = {
        "morandi": {
            "name": "原始 Morandi 主题",
            "file": "Style/global_stylesheet.qss",
            "description": "温暖的 Morandi 色系，优雅舒适",
            "preview_color": "#D3CBC5"
        },
        "blue": {
            "name": "经典蓝色主题", 
            "file": "Style/style1.qss",
            "description": "清新的蓝色主题，专业简洁",
            "preview_color": "#3182CE"
        },
        "green": {
            "name": "绿色自然主题",
            "file": "Style/style2.qss",
            "description": "自然绿色主题，护眼舒适",
            "preview_color": "#10B981"
        },
        "dark": {
            "name": "现代深色主题",
            "file": "Style/style3.qss",
            "description": "现代深色主题，时尚专业",
            "preview_color": "#68D391"
        }
    }
    
    # 语言配置
    LANGUAGES = {
        "zh_CN": "中文 (简体)",
        "en_US": "English",
        "ja_JP": "日本語"
    }
    
    def __init__(self):
        super().__init__()
        self.settings_file = "settings.json"
        self.default_settings = {
            "theme": "dark",
            "language": "zh_CN",
            "window_size": [800, 600],
            "window_maximized": False,
            "auto_save": True,
            "show_tips": True,
            "log_level": "INFO"
        }
        self.settings = self._load_settings()
        
    def _load_settings(self) -> Dict[str, Any]:
        """加载设置"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                # 合并默认设置，确保所有必要的键都存在
                merged_settings = self.default_settings.copy()
                merged_settings.update(settings)
                return merged_settings
            else:
                return self.default_settings.copy()
        except Exception as e:
            print(f"加载设置失败: {e}")
            return self.default_settings.copy()
    
    def _save_settings(self):
        """保存设置"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存设置失败: {e}")
    
    def get(self, key: str, default=None):
        """获取设置值"""
        return self.settings.get(key, default)
    
    def set(self, key: str, value):
        """设置值"""
        if key in self.settings and self.settings[key] == value:
            return  # 值没有改变
            
        self.settings[key] = value
        self._save_settings()
        self.settings_changed.emit(key, value)
        
        # 特殊处理主题切换
        if key == "theme":
            self.apply_theme(value)
    
    def apply_theme(self, theme_key: str):
        """应用主题"""
        if theme_key not in self.THEMES:
            print(f"未知主题: {theme_key}")
            return False
            
        theme_info = self.THEMES[theme_key]
        style_file = theme_info["file"]
        
        if not os.path.exists(style_file):
            print(f"样式文件不存在: {style_file}")
            return False
            
        try:
            with open(style_file, "r", encoding="utf-8") as f:
                style_content = f.read()
                
            app = QApplication.instance()
            if app:
                app.setStyleSheet(style_content)
                self.theme_changed.emit(theme_key)
                print(f"已应用主题: {theme_info['name']}")
                return True
        except Exception as e:
            print(f"应用主题失败: {e}")
            return False
            
        return False
    
    def get_current_theme_info(self):
        """获取当前主题信息"""
        current_theme = self.get("theme", "dark")
        return self.THEMES.get(current_theme, self.THEMES["dark"])
    
    def get_available_themes(self):
        """获取所有可用主题"""
        return self.THEMES
    
    def get_available_languages(self):
        """获取所有可用语言"""
        return self.LANGUAGES
    
    def reset_to_defaults(self):
        """重置为默认设置"""
        self.settings = self.default_settings.copy()
        self._save_settings()
        # 应用默认主题
        self.apply_theme(self.settings["theme"])
        print("设置已重置为默认值")

# 全局设置管理器实例
settings_manager = SettingsManager()
