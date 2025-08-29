"""
增强的主题管理器
支持深色/浅色自动切换、时间自动切换、用户自定义混搭等功能
"""

import json
import os
import shutil
from datetime import datetime, time
from typing import Dict, List, Tuple, Optional
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QApplication


class ThemeManager(QObject):
    """增强的主题管理器"""
    
    # 信号
    theme_changed = pyqtSignal(str, str)  # 主题类别, 变体(light/dark)
    auto_switch_toggled = pyqtSignal(bool)  # 自动切换开启/关闭
    
    def __init__(self):
        super().__init__()
        
        # 基础路径设置
        self.themes_dir = "Style/themes"
        
        # 主题定义 - 全部使用简化版
        self.themes = {
            'morandi': {
                'name': '莫兰蒂',
                'description': '温暖优雅的莫兰蒂色调',
                'light': 'Style/themes/morandi/light_simple.qss',
                'dark': 'Style/themes/morandi/dark_simple.qss'
            },
            'modern': {
                'name': '现代',
                'description': '简洁现代的设计风格',
                'light': 'Style/themes/modern/light_simple.qss',
                'dark': 'Style/themes/modern/dark_simple.qss'
            },
            'contrast': {
                'name': '高对比',
                'description': '高对比度，适合视觉障碍用户',
                'light': 'Style/themes/contrast/light_simple.qss',
                'dark': 'Style/themes/contrast/dark_simple.qss'
            },
            'ocean': {
                'name': '海洋',
                'description': '清新的海洋蓝色主题',
                'light': 'Style/themes/ocean/light_simple.qss',
                'dark': 'Style/themes/ocean/dark_simple.qss'
            }
    }
        # 设置文件路径（迁移到 Style 目录下）
        self.settings_dir = 'Style'
        self.settings_file = os.path.join(self.settings_dir, 'theme_settings.json')
        self.legacy_settings_file = 'theme_settings.json'

        # 默认设置
        self.default_settings = {
            'current_theme': 'morandi',
            'current_variant': 'light',
            'auto_switch_enabled': False,
            'auto_switch_mode': 'time',  # 'time' 或 'system'
            'light_start_time': '06:00',
            'dark_start_time': '18:00',
            'mixed_mode': False,
            'mixed_settings': {
                'title_theme': 'morandi',
                'title_variant': 'light',
                'button_theme': 'modern',
                'button_variant': 'light',
                'background_theme': 'ocean',
                'background_variant': 'light'
            }
        }

        # 迁移老路径的设置文件（如存在）并确保目录存在
        self._migrate_settings_file()

        # 加载设置
        self.settings = self.load_settings()

        # 定时器用于时间自动切换
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_time_switch)

        if self.settings['auto_switch_enabled'] and self.settings['auto_switch_mode'] == 'time':
            self.timer.start(60000)  # 每分钟检查一次
    
    def load_settings(self) -> Dict:
        """加载主题设置"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    # 合并默认设置以确保所有字段都存在
                    for key, value in self.default_settings.items():
                        if key not in settings:
                            settings[key] = value
                    return settings
            except Exception as e:
                print(f"加载主题设置失败: {e}")
        
        return self.default_settings.copy()
    
    def save_settings(self):
        """保存主题设置"""
        try:
            # 确保目录存在
            settings_dir = os.path.dirname(self.settings_file)
            if settings_dir:
                os.makedirs(settings_dir, exist_ok=True)
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存主题设置失败: {e}")
    
    def _migrate_settings_file(self):
        """将旧版根目录下的 theme_settings.json 迁移到 Style 目录下"""
        try:
            # 创建目标目录
            if self.settings_dir:
                os.makedirs(self.settings_dir, exist_ok=True)
            # 如果旧文件存在且新文件不存在，执行迁移
            if os.path.exists(self.legacy_settings_file) and not os.path.exists(self.settings_file):
                shutil.move(self.legacy_settings_file, self.settings_file)
                print(f"已迁移主题设置文件至: {self.settings_file}")
        except Exception as e:
            print(f"迁移主题设置文件失败: {e}")
    
    def get_available_themes(self) -> Dict[str, Dict]:
        """获取可用主题列表"""
        return self.themes
    
    def get_current_theme(self) -> Tuple[str, str]:
        """获取当前主题"""
        return self.settings['current_theme'], self.settings['current_variant']
    
    def get_current_stylesheet(self) -> str:
        """获取当前主题的样式表内容"""
        try:
            theme_name, variant = self.get_current_theme()
            
            # 首先尝试读取简化的基础组件样式
            base_components_file = os.path.join("Style", "base_components_simple.qss")
            if not os.path.exists(base_components_file):
                # 回退到原始的基础组件样式
                base_components_file = os.path.join("Style", "base_components.qss")
            
            base_stylesheet = ""
            if os.path.exists(base_components_file):
                with open(base_components_file, 'r', encoding='utf-8') as f:
                    base_stylesheet = f.read()
            
            # 读取主题特定样式 - 直接使用 simple 版本
            theme_file = os.path.join(self.themes_dir, theme_name, f"{variant}_simple.qss")
            theme_stylesheet = ""
            
            if os.path.exists(theme_file):
                with open(theme_file, 'r', encoding='utf-8') as f:
                    theme_stylesheet = f.read()
            else:
                print(f"主题文件不存在: {theme_file}")
                # 备用方案：使用themes字典中的路径
                theme_path = self.themes.get(theme_name, {}).get(variant, '')
                if theme_path and os.path.exists(theme_path):
                    with open(theme_path, 'r', encoding='utf-8') as f:
                        theme_stylesheet = f.read()
            
            # 直接返回主题样式，因为基础样式可能包含不支持的CSS属性
            return theme_stylesheet if theme_stylesheet else base_stylesheet
            
        except Exception as e:
            print(f"获取样式表失败: {e}")
            return ""
    
    def set_theme(self, theme_name: str, variant: Optional[str] = None):
        """设置主题"""
        if theme_name not in self.themes:
            print(f"主题 {theme_name} 不存在")
            return
        
        # 如果没有指定变体，保持当前变体
        if variant is None:
            variant = self.settings['current_variant']
        
        if variant not in ['light', 'dark']:
            print(f"主题变体 {variant} 无效")
            return
        
        # 更新设置
        self.settings['current_theme'] = theme_name
        self.settings['current_variant'] = variant
        self.save_settings()
        
        # 应用主题
        self.apply_theme(theme_name, variant)
        
        # 发送信号
        self.theme_changed.emit(theme_name, variant)
        
        print(f"已切换到主题: {self.themes[theme_name]['name']} - {'浅色' if variant == 'light' else '深色'}")
    
    def apply_theme(self, theme_name: str, variant: str):
        """应用主题"""
        if self.settings['mixed_mode']:
            self.apply_mixed_theme()
        else:
            self.apply_single_theme(theme_name, variant)
    
    def apply_single_theme(self, theme_name: str, variant: str):
        """应用单一主题"""
        try:
            stylesheet = self.get_current_stylesheet()
            
            app = QApplication.instance()
            if app:
                app.setStyleSheet(stylesheet)
                print(f"✅ 主题样式应用成功: {theme_name} - {variant}")
            else:
                print("❌ 无法获取应用程序实例")
                
        except Exception as e:
            print(f"应用主题失败: {e}")
    
    def apply_mixed_theme(self):
        """应用混搭主题"""
        # 这里可以实现复杂的主题混搭逻辑
        # 目前简化为应用当前主题
        current_theme, current_variant = self.get_current_theme()
        self.apply_single_theme(current_theme, current_variant)
    
    def toggle_variant(self):
        """切换深色/浅色变体"""
        current_theme, current_variant = self.get_current_theme()
        new_variant = 'dark' if current_variant == 'light' else 'light'
        self.set_theme(current_theme, new_variant)
    
    def set_auto_switch(self, enabled: bool, mode: str = 'time'):
        """设置自动切换"""
        self.settings['auto_switch_enabled'] = enabled
        self.settings['auto_switch_mode'] = mode
        self.save_settings()
        
        if enabled and mode == 'time':
            self.timer.start(60000)  # 每分钟检查一次
        else:
            self.timer.stop()
        
        self.auto_switch_toggled.emit(enabled)
        print(f"自动切换已{'开启' if enabled else '关闭'}")
    
    def set_time_schedule(self, light_time: str, dark_time: str):
        """设置时间自动切换计划"""
        self.settings['light_start_time'] = light_time
        self.settings['dark_start_time'] = dark_time
        self.save_settings()
        print(f"时间计划已更新: 浅色模式 {light_time}，深色模式 {dark_time}")
    
    def check_time_switch(self):
        """检查是否需要根据时间切换主题"""
        if not self.settings['auto_switch_enabled'] or self.settings['auto_switch_mode'] != 'time':
            return
        
        now = datetime.now().time()
        light_time = time.fromisoformat(self.settings['light_start_time'])
        dark_time = time.fromisoformat(self.settings['dark_start_time'])
        
        current_theme, current_variant = self.get_current_theme()
        
        # 判断应该使用哪个变体
        if light_time <= dark_time:
            # 正常情况：白天在前，晚上在后
            should_be_light = light_time <= now < dark_time
        else:
            # 跨日情况：比如晚上6点到第二天早上6点是深色模式
            should_be_light = not (dark_time <= now < light_time)
        
        target_variant = 'light' if should_be_light else 'dark'
        
        if current_variant != target_variant:
            self.set_theme(current_theme, target_variant)
            print(f"根据时间自动切换到{'浅色' if target_variant == 'light' else '深色'}模式")
    
    def set_mixed_mode(self, enabled: bool):
        """设置混搭模式"""
        self.settings['mixed_mode'] = enabled
        self.save_settings()
        
        if enabled:
            self.apply_mixed_theme()
        else:
            current_theme, current_variant = self.get_current_theme()
            self.apply_single_theme(current_theme, current_variant)
        
        print(f"混搭模式已{'开启' if enabled else '关闭'}")
    
    def update_mixed_settings(self, component: str, theme: str, variant: str):
        """更新混搭设置中的组件主题"""
        if component in self.settings['mixed_settings']:
            self.settings['mixed_settings'][f'{component}_theme'] = theme
            self.settings['mixed_settings'][f'{component}_variant'] = variant
            self.save_settings()
            
            if self.settings['mixed_mode']:
                self.apply_mixed_theme()
    
    def get_theme_info(self, theme_name: str) -> Dict:
        """获取主题信息"""
        return self.themes.get(theme_name, {})
    
    def initialize_theme(self):
        """初始化主题"""
        current_theme, current_variant = self.get_current_theme()
        
        # 如果启用了自动切换，检查是否需要切换
        if self.settings['auto_switch_enabled']:
            if self.settings['auto_switch_mode'] == 'time':
                self.check_time_switch()
            # 这里可以添加系统主题检测逻辑
        else:
            self.apply_theme(current_theme, current_variant)
    
    def export_theme_settings(self, file_path: str):
        """导出主题设置"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            print(f"主题设置已导出到: {file_path}")
            return True
        except Exception as e:
            print(f"导出主题设置失败: {e}")
            return False
    
    def import_theme_settings(self, file_path: str):
        """导入主题设置"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
            
            # 验证设置有效性
            if 'current_theme' in imported_settings and imported_settings['current_theme'] in self.themes:
                self.settings = imported_settings
                self.save_settings()
                self.initialize_theme()
                print(f"主题设置已导入: {file_path}")
                return True
            else:
                print("导入的设置文件格式无效")
                return False
                
        except Exception as e:
            print(f"导入主题设置失败: {e}")
            return False


# 全局主题管理器实例
theme_manager = ThemeManager()
