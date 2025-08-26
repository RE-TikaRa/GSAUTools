import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTranslator, QLocale, QStandardPaths
import os
os.environ["QT_API"] = "pyqt6"
from Module.MainGUI import MainWindow

def main():
    app = QApplication(sys.argv)

    # 加载全局样式表
    with open("Style/global_stylesheet.qss", "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())

    # 加载本地化翻译
    translator = QTranslator()
    locale = QLocale.system().name()
    translation_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    if translator.load(f"qtbase_{locale}", translation_path):
        app.installTranslator(translator)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
