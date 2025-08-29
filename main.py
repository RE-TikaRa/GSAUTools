import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTranslator, QLocale, QStandardPaths
import os
import json
os.environ["QT_API"] = "pyqt6"
from Module.MainGUI import MainWindow

# 导入主题管理器
try:
    from Module.settings.managers.theme_manager import theme_manager
    USE_NEW_THEME_SYSTEM = True
except ImportError:
    USE_NEW_THEME_SYSTEM = False
    print("主题管理器导入失败，使用传统主题系统")

def load_saved_theme():
    """加载保存的主题设置"""
    if USE_NEW_THEME_SYSTEM:
        # 使用新的主题管理器
        try:
            return theme_manager.get_current_stylesheet()
        except Exception as e:
            print(f"新主题系统加载失败: {e}")
    
    # 传统主题系统（备用）
    try:
        if os.path.exists("settings.json"):
            with open("settings.json", 'r', encoding='utf-8') as f:
                settings = json.load(f)
                theme = settings.get("theme", "dark")
                
                # 主题文件映射
                theme_files = {
                    "morandi": "Style/global_stylesheet.qss",
                    "blue": "Style/style1.qss", 
                    "green": "Style/style2.qss",
                    "dark": "Style/style3.qss"
                }
                
                theme_file = theme_files.get(theme, "Style/style3.qss")
                if os.path.exists(theme_file):
                    with open(theme_file, "r", encoding="utf-8") as f:
                        return f.read()
    except Exception as e:
        print(f"加载主题设置失败: {e}")
    
    # 默认返回深色主题
    try:
        with open("Style/style3.qss", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return ""

def main():
    app = QApplication(sys.argv)

    # 初始化主题管理器
    if USE_NEW_THEME_SYSTEM:
        try:
            theme_manager.initialize_theme()
        except Exception as e:
            print(f"主题管理器初始化失败: {e}")
    
    # 加载主题样式
    stylesheet = load_saved_theme()
    if stylesheet:
        app.setStyleSheet(stylesheet)

    # 加载本地化翻译
    translator = QTranslator()
    locale = QLocale.system().name()
    translation_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    if translator.load(f"qtbase_{locale}", translation_path):
        app.installTranslator(translator)

    window = MainWindow()
    window.show()
    
    # 如果使用新主题系统，连接主题变化信号
    if USE_NEW_THEME_SYSTEM and hasattr(theme_manager, 'theme_changed'):
        try:
            signal = getattr(theme_manager, 'theme_changed', None)
            if signal and hasattr(signal, 'connect'):
                signal.connect(lambda theme, variant: app.setStyleSheet(theme_manager.get_current_stylesheet()))
        except Exception as e:
            print(f"连接主题信号失败: {e}")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
