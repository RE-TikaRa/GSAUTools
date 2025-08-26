import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QPushButton, 
                           QVBoxLayout, QHBoxLayout, QLabel, QStackedWidget,
                           QSizePolicy, QFrame, QGraphicsDropShadowEffect, QToolButton,
                           QLayout, QWidgetItem, QGridLayout, QButtonGroup, QTreeWidget, QTreeWidgetItem, QSplitter)
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QRect, QPoint, pyqtSlot, QTranslator, QLocale, QLibraryInfo, QStandardPaths
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtSvgWidgets import QSvgWidget
import os
os.environ['QT_API'] = 'pyqt6'
import qtawesome as qta
import subprocess
from Module.MEA.ExamGUI_PyQt import ExamGUI

class SidebarButton(QPushButton):
    def __init__(self, text="", icon_name=None, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        if icon_name:
            self.setIcon(QIcon(qta.icon(icon_name).pixmap(20, 20)))
        self.setFixedHeight(40)
        self.setIconSize(QSize(20, 20))


class CardButton(QPushButton):
    """Custom card button with centered icon and text below."""
    def __init__(self, text="", icon_pixmap=None, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        # 不要在获得焦点时显示焦点环（防止点击后出现不同颜色圈）
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setFixedSize(160, 120)

        # 使用与侧边栏一致的选中视觉（背景 + 文本色）以便二级菜单与卡片视觉统一
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
                color: #2f2d2b; /* 与侧边栏选中颜色一致 */
            }
            QPushButton:hover {
                background: #f6f6f6;
            }
            /* 当按钮被选中，内部的 QLabel 也继承颜色 */
            QPushButton:checked QLabel { color: #2f2d2b; }
        ''')

        # 创建一个容器widget来放置内容
        container = QWidget(self)
        container_layout = QVBoxLayout(container)
        # 设置合适的边距，顶部稍大以平衡视觉效果
        container_layout.setContentsMargins(10, 15, 10, 10)
        container_layout.setSpacing(8)

        # 创建图标容器（背景设为透明，避免在按钮背景变化时出现白色/其他颜色环）
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(64, 64)  # 固定大小以确保居中
        # 确保图标标签背景透明
        self.icon_label.setStyleSheet("background: transparent; border: none;")
        if icon_pixmap:
            scaled_pixmap = icon_pixmap.scaled(48, 48, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.icon_label.setPixmap(scaled_pixmap)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 创建文字标签
        self.text_label = QLabel(text)
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = self.text_label.font()
        font.setPointSize(9)
        self.text_label.setFont(font)
        # 文本颜色由父按钮的样式控制，这里不在 QLabel 上硬编码颜色，便于 checked 状态继承

        # 将图标和文字添加到容器布局中，并强制居中对齐
        container_layout.addWidget(self.icon_label, 0, Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(self.text_label, 0, Qt.AlignmentFlag.AlignCenter)

        # 设置容器背景透明并设置大小策略以确保居中
        container.setStyleSheet("background: transparent;")
        container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        container.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        # 创建主布局并添加容器
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container, 0, Qt.AlignmentFlag.AlignCenter)

    def setIconPixmap(self, pixmap):
        self.icon_label.setPixmap(pixmap)

class SubMenu(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self.setVisible(False)
        # 设置尺寸策略以允许动画
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)

    def addButton(self, text, icon_name=None):
        btn = QPushButton(text)
        btn.setFixedHeight(30)
        btn.setCheckable(True)
        if icon_name:
            btn.setIcon(QIcon(qta.icon(icon_name).pixmap(16, 16)))
            btn.setIconSize(QSize(16, 16))
        # 设置左对齐和 padding 以便图标缩进
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
    """FlowLayout: places child widgets in rows and wraps them when necessary.
    This implementation constrains to at most 3 columns per row by default."""
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

            # if exceed width or reached max columns, wrap
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


class MainWindow(QMainWindow):
    def launch_exam(self):
        # 使用当前解释器启动模块化的 Exam GUI
        exe = sys.executable
        # prefer the GUI module implemented in a separate file
        script = os.path.join(os.path.dirname(__file__), 'Module', 'MEA', 'ExamGUI_PyQt.py')
        try:
            subprocess.Popen([exe, script], cwd=os.path.dirname(__file__))
        except Exception as e:
            print(f"Failed to launch Exam GUI module: {e}")
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GUI DEMO")
        self.resize(800, 600)

        # 创建主布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建侧边栏
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("""
            QWidget {
                /* Morandi muted sidebar */
                background-color: #6b6966; /* muted gray-brown */
                color: #f3efea; /* soft ivory text */
            }
            QPushButton {
                text-align: left;
                padding: 5px 10px;
                border: none;
                background-color: transparent;
                color: #f3efea;
            }
            QPushButton:hover {
                background-color: #7f7d7a; /* slightly lighter muted */
            }
            QPushButton:checked {
                background-color: #bda9a2; /* muted dusty rose */
                color: #2f2d2b;
            }
        """)

        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # 创建折叠按钮
        self.toggle_button = QPushButton()
        self.toggle_button.setIcon(QIcon(qta.icon('fa5s.bars').pixmap(20, 20)))
        self.toggle_button.setFixedHeight(40)
        self.toggle_button.setIconSize(QSize(20, 20))
        self.toggle_button.clicked.connect(self.toggle_sidebar)
        sidebar_layout.addWidget(self.toggle_button)

        # 创建主菜单按钮
        self.dashboard_btn = SidebarButton("主页", 'fa5s.home')

        # 创建带有子菜单的按钮
        self.features_btn = SidebarButton("功能", 'fa5s.th-list')

        # 定义功能项（统一数据源，侧边栏与卡片使用相同内容）
        self.card_defs = [
            ("MOOCExamAnalyzer", 'fa5s.chart-bar'),
            ("功能 2", 'fa5s.table'),
            ("功能 3", 'fa5s.chart-pie'),
            ("功能 4", 'fa5s.cubes'),
        ]

        # 子菜单容器与按钮列表
        self.features_submenu = SubMenu()
        self.submenu_buttons = []
        # 创建子菜单按钮并添加到列表（基于 self.card_defs）
        # 这些按钮会被加入到 self.submenu_buttons，之后再加入 QButtonGroup
        for i, (label_text, icon_name) in enumerate(self.card_defs):
            try:
                sb = self.features_submenu.addButton(label_text, icon_name)
            except Exception:
                sb = self.features_submenu.addButton(label_text)
            # 不直接绑定 clicked 到处理器，使用 QButtonGroup 的 idClicked 来统一处理，
            # 避免信号循环与重复页面切换。仅保留按钮引用。
            self.submenu_buttons.append(sb)

    # 创建子菜单按钮并添加到列表（稍后加入 QButtonGroup）
    # (之前因缩进问题临时移除，这里已恢复)

        # 设置和关于页面按钮
        self.settings_btn = SidebarButton("设置", 'fa5s.cog')
        self.about_btn = SidebarButton("关于", 'fa5s.info-circle')

        # 添加按钮到侧边栏
        sidebar_layout.addWidget(self.dashboard_btn)
        sidebar_layout.addWidget(self.features_btn)
        sidebar_layout.addWidget(self.features_submenu)
        sidebar_layout.addWidget(self.settings_btn)
        sidebar_layout.addWidget(self.about_btn)
        sidebar_layout.addStretch()

        # 创建主内容区
        self.content_stack = QStackedWidget()

        # 添加页面到堆栈
        self.dashboard_page = QWidget()
        self.dashboard_page.setStyleSheet("background-color: white;")
        dashboard_layout = QVBoxLayout(self.dashboard_page)
        # 垂直居中显示
        dashboard_layout.addStretch()

        # 使用 QSvgWidget 添加 LOGO 到主页界面最中间
        self.logo_widget = QSvgWidget("img/LOGO.svg")
        self.logo_widget.setFixedSize(400, 235)  # 初始大小为 50% 的比例 (800x600 的 50%)
        dashboard_layout.addWidget(self.logo_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        dashboard_layout.addStretch()

        # 功能页面：在点击功能时展示的卡片式二级菜单
        self.features_page = QWidget()
        # 使用浅灰背景以便白色卡片可见
        self.features_page.setStyleSheet("background-color: #f5f7fa;")
        features_layout = QVBoxLayout(self.features_page)
        features_layout.setContentsMargins(12, 12, 12, 12)
        features_layout.setSpacing(12)
        features_layout.addStretch()

    # 为每个功能创建独立页面（详情页），并保存到列表中
    # 特殊处理：将功能 1 嵌入为 ExamGUI 页面
        self.feature_pages = []
        for i, (label_text, icon_name) in enumerate(self.card_defs):
            if i == 0:
                try:
                    # 局部导入以避免启动时相关 GUI 库缺失导致整个主程序失败
                    from Module.MEA.ExamGUI_PyQt import ExamGUI
                    page = ExamGUI()
                except Exception as e:
                    # 退回到占位页面并在控制台打印错误，便于调试
                    print(f"Failed to embed ExamGUI: {e}")
                    page = QWidget()
                    page.setStyleSheet("background-color: white;")
                    playout = QVBoxLayout(page)
                    playout.addStretch()
                    title = QLabel(f"{label_text} 页面 (Exam GUI 加载失败)")
                    title.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    playout.addWidget(title)
                    playout.addStretch()
                self.feature_pages.append(page)
            else:
                page = QWidget()
                page.setStyleSheet("background-color: white;")
                playout = QVBoxLayout(page)
                playout.addStretch()
                title = QLabel(f"{label_text} 页面")
                title.setAlignment(Qt.AlignmentFlag.AlignCenter)
                playout.addWidget(title)
                playout.addStretch()
                self.feature_pages.append(page)
        features_header = QLabel("功能 - 卡片式二级菜单")
        features_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        features_layout.addWidget(features_header)

        self.feature_cards = []

        # 使用 QGridLayout 进行布局
        cards_container = QWidget()
        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cards_container.setLayout(grid)

        # 创建按钮组以便排他性和同步
        self.submenu_btngroup = QButtonGroup(self)
        self.submenu_btngroup.setExclusive(True)
        self.cards_btngroup = QButtonGroup(self)
        self.cards_btngroup.setExclusive(True)

        # QToolButton 已在文件顶部导入
        for i, (label_text, icon_name) in enumerate(self.card_defs):
            # 创建更大的图标以确保清晰度
            pix = qta.icon(icon_name).pixmap(64, 64)
            btn = CardButton(label_text, pix)

            # accessibility
            btn.setAccessibleName(label_text)
            btn.setToolTip(label_text)

            # 阴影效果
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(10)
            shadow.setOffset(0, 3)
            btn.setGraphicsEffect(shadow)

            # 将卡片加入按钮组（用于排他选择与同步）
            self.cards_btngroup.addButton(btn, i)
            self.feature_cards.append(btn)
            row, col = divmod(i, 3)
            grid.addWidget(btn, row, col)

        # 将子菜单按钮加入按钮组并绑定 ID（现在 submenu_buttons 已经创建）
        for i, sb in enumerate(self.submenu_buttons):
            self.submenu_btngroup.addButton(sb, i)

        # 连接按钮组信号以实现双向同步
        self.submenu_btngroup.idClicked.connect(self.on_submenu_id_clicked)
        self.cards_btngroup.idClicked.connect(self.on_card_id_clicked)

        # 将卡片的点击动作也明确连接到内部方法，确保子菜单同步时不会触发额外的 clicked 信号
        for idx, card in enumerate(self.feature_cards):
            card.clicked.connect(lambda checked, i=idx: self.feature_card_clicked(i))

        # cards_container.setLayout(grid) # 当布局在构造时指定父控件时，无需再次设置
        # 使容器可扩展，并确保有足够高度以显示卡片
        from PyQt6.QtWidgets import QSizePolicy as _SP
        cards_container.setSizePolicy(_SP.Policy.Expanding, _SP.Policy.Expanding)
        cards_container.setMinimumHeight(220)
        features_layout.addWidget(cards_container)
        features_layout.addStretch()

        self.settings_page = QWidget()
        self.settings_page.setStyleSheet("background-color: white;")
        settings_layout = QVBoxLayout(self.settings_page)
        settings_layout.addStretch()
        settings_label = QLabel("设置页面")
        settings_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        settings_layout.addWidget(settings_label)
        settings_layout.addStretch()

        self.about_page = QWidget()
        self.about_page.setStyleSheet("background-color: white;")
        about_layout = QVBoxLayout(self.about_page)
        about_layout.addStretch()
        about_label = QLabel("关于页面")
        about_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_layout.addWidget(about_label)
        about_layout.addStretch()

        # 页面添加顺序： 仪表盘, 功能(卡片目录), 每个功能的详情页..., 设置, 关于
        self.content_stack.addWidget(self.dashboard_page)
        self.content_stack.addWidget(self.features_page)
        # 追加每个功能的详情页
        for page in self.feature_pages:
            self.content_stack.addWidget(page)
        self.content_stack.addWidget(self.settings_page)
        self.content_stack.addWidget(self.about_page)

        # 初始化状态管理
        self.menu_buttons = [self.dashboard_btn, self.features_btn, self.settings_btn, self.about_btn]

        # 设置按钮和页面的映射关系（包含功能页）
        # 主按钮映射到主页面索引
        self.button_page_map = {
            self.dashboard_btn: 0,
            self.features_btn: 1,
            self.settings_btn: 2 + len(self.feature_pages),
            self.about_btn: 3 + len(self.feature_pages)
        }

        # 反向映射，用于从页面索引找到对应的按钮
        self.page_button_map = {v: k for k, v in self.button_page_map.items()}

        # 连接按钮信号
        for button in self.menu_buttons:
            if button == self.features_btn:
                button.clicked.connect(self.toggle_features_menu)
                # 点击功能按钮也切换到功能页面（展开时）
            if button in self.button_page_map:
                page_index = self.button_page_map[button]
                button.clicked.connect(lambda checked, idx=page_index: self.switch_page(idx))

        # 添加侧边栏和内容区到主布局
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_stack)

        # 设置初始状态
        self.sidebar_expanded = True
        self.current_page = 0
        self.dashboard_btn.setChecked(True)
        self.features_btn.setChecked(False)
        self.content_stack.setCurrentIndex(0)

    def switch_page(self, page_index):
        # 如果已经在当前页面，不做任何操作
        if self.current_page == page_index:
            return
            
        # 更新页面
        self.current_page = page_index
        self.content_stack.setCurrentIndex(page_index)
        # 更新按钮状态（统一处理所有主菜单按钮）
        for button in self.menu_buttons:
            button.setChecked(button == self.page_button_map.get(page_index))

        # 功能页特性：如果切换到功能页且侧边栏展开，则展开子菜单；
        # 如果切换到非功能页并且子菜单正在展开，则收起子菜单。
        features_index = self.button_page_map.get(self.features_btn)
        if page_index == features_index:
            if self.sidebar_expanded:
                # 只有在侧边栏展开时才显示子菜单
                if not self.features_submenu.isVisible():
                    self.expand_submenu()
        else:
            if self.features_submenu.isVisible():
                self.collapse_submenu()

    def on_submenu_id_clicked(self, id):
        # 当子菜单按钮被点击时，选中对应的卡片（阻塞卡组信号以防循环）
        try:
            # 阻塞卡片组信号
            self.cards_btngroup.blockSignals(True)
            btn = self.cards_btngroup.button(id)
            if btn:
                btn.setChecked(True)
            # 确保功能主按钮为选中
            self.features_btn.setChecked(True)
            # 切换到对应的功能详情页面（features 目录页后面）
            page_index = 2 + id
            self.switch_page(page_index)
        finally:
            self.cards_btngroup.blockSignals(False)

    def on_card_id_clicked(self, id):
        # 当卡片被点击时，选中对应的子菜单按钮（阻塞子菜单组信号以防循环）
        try:
            self.submenu_btngroup.blockSignals(True)
            sb = self.submenu_btngroup.button(id)
            if sb:
                sb.setChecked(True)
            # 确保功能主按钮为选中
            self.features_btn.setChecked(True)
            # 切换到对应的功能详情页面（功能页后面的详情页）
            page_index = 2 + id
            self.switch_page(page_index)
        finally:
            self.submenu_btngroup.blockSignals(False)

    def handle_submenu_button_click(self, clicked_button):
        # 该函数现在保留为按需调用的工具函数。
        # 建议使用 QButtonGroup 的 idClicked 回调进行同步（见 on_submenu_id_clicked / on_card_id_clicked）。
        try:
            idx = self.submenu_buttons.index(clicked_button)
        except ValueError:
            return

        # 使用按钮组进行排他性控制（会触发 idClicked -> on_submenu_id_clicked）
        btn = self.submenu_btngroup.button(idx)
        if btn:
            btn.setChecked(True)
        # 确保功能主按钮为选中
        self.features_btn.setChecked(True)
        # 同步卡片状态（不触发卡片组的 idClicked 回调）
        self.cards_btngroup.blockSignals(True)
        try:
            for i, c in enumerate(self.feature_cards):
                c.setChecked(i == idx)
        finally:
            self.cards_btngroup.blockSignals(False)

    def toggle_features_menu(self):
        if hasattr(self, 'submenu_animation') and self.submenu_animation.state() == QPropertyAnimation.State.Running:
            return
            
        is_features_checked = self.features_btn.isChecked()
        
        # 如果功能按钮被选中，展开子菜单并切换到功能页面
        if is_features_checked and not self.features_submenu.isVisible():
            # 取消其他主菜单按钮的选中状态
            for button in self.menu_buttons:
                if button != self.features_btn:
                    button.setChecked(False)
                    
            self.expand_submenu()
            # 切换到功能页
            self.switch_page(self.button_page_map[self.features_btn])
        # 如果功能按钮被取消选中，收起子菜单
        elif not is_features_checked and self.features_submenu.isVisible():
            self.collapse_submenu()
            
            # 收起子菜单后，恢复当前页面对应按钮的选中状态（但不要把功能按钮强制重新选中）
            if self.current_page in self.page_button_map:
                mapped_btn = self.page_button_map[self.current_page]
                if mapped_btn != self.features_btn:
                    mapped_btn.setChecked(True)

        # 显示子菜单（如果需要）
        if self.features_btn.isChecked() and self.sidebar_expanded:
            # 取消其他按钮的选中状态
            for button in self.menu_buttons:
                if button != self.features_btn:
                    button.setChecked(False)
                    
            self.features_submenu.setVisible(True)
            self.features_submenu.setMaximumHeight(0)
            
            # 计算实际需要的高度
            required_height = self.features_submenu._layout.sizeHint().height()
            
            # 创建高度动画
            self.submenu_animation = QPropertyAnimation(self.features_submenu, b"maximumHeight")
            self.submenu_animation.setStartValue(0)
            self.submenu_animation.setEndValue(required_height)
            self.submenu_animation.setDuration(150)
            self.submenu_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.submenu_animation.start()
        else:
            self.collapse_submenu()

    def feature_card_clicked(self, idx):
        # 点击卡片时选中对应的子菜单按钮并同步状态
        if idx < len(self.submenu_buttons):
            btn = self.submenu_buttons[idx]
            # 触发侧边栏子菜单按钮逻辑
            self.handle_submenu_button_click(btn)

    def toggle_sidebar(self):
        # 如果任何动画正在运行，直接返回
        if (hasattr(self, 'animation') and self.animation.state() == QPropertyAnimation.State.Running) or \
           (hasattr(self, 'submenu_animation') and self.submenu_animation.state() == QPropertyAnimation.State.Running):
            return

        # 如果要折叠侧边栏，先确保子菜单已关闭（同时进行收起动画，然后继续折叠侧边栏）
        if self.sidebar_expanded and self.features_submenu.isVisible():
            # 取消功能按钮选中状态但不要阻止侧边栏折叠动画
            self.features_btn.setChecked(False)
            self.collapse_submenu()

        # 创建动画
        self.animation = QPropertyAnimation(self.sidebar, b"minimumWidth")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        if self.sidebar_expanded:
            self.animation.setStartValue(200)
            self.animation.setEndValue(50)
            self.animation.finished.connect(lambda: self.update_button_text(False))
        else:
            self.animation.setStartValue(50)
            self.animation.setEndValue(200)
            self.animation.finished.connect(lambda: self.update_button_text(True))

        self.animation.start()
        self.sidebar_expanded = not self.sidebar_expanded

    def expand_submenu(self):
        if not self.sidebar_expanded:
            return
            
        self.features_submenu.setVisible(True)
        self.features_submenu.setMaximumHeight(0)
        
        # 计算实际需要的高度
        required_height = self.features_submenu._layout.sizeHint().height()
        
        # 创建展开动画
        self.submenu_animation = QPropertyAnimation(self.features_submenu, b"maximumHeight")
        self.submenu_animation.setStartValue(0)
        self.submenu_animation.setEndValue(required_height)
        self.submenu_animation.setDuration(150)
        self.submenu_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.submenu_animation.start()

    def collapse_submenu(self):
        if self.features_submenu.isVisible():
            current_height = self.features_submenu.height()
            self.submenu_animation = QPropertyAnimation(self.features_submenu, b"maximumHeight")
            self.submenu_animation.setStartValue(current_height)
            self.submenu_animation.setEndValue(0)
            self.submenu_animation.setDuration(150)
            self.submenu_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.submenu_animation.finished.connect(lambda: self.features_submenu.setVisible(False))
            self.submenu_animation.start()
            
            # 重置所有子菜单按钮的状态
            for btn in self.submenu_buttons:
                btn.setChecked(False)

    def update_button_text(self, expanded):
        if expanded:
            self.dashboard_btn.setText("仪表盘")
            self.features_btn.setText("功能")
            self.settings_btn.setText("设置")
            self.about_btn.setText("关于")
        else:
            self.dashboard_btn.setText("")
            self.features_btn.setText("")
            self.settings_btn.setText("")
            self.about_btn.setText("")
            if self.features_submenu.isVisible():
                self.features_submenu.hide()

    def resizeEvent(self, event):
        # 根据窗口大小动态调整 LOGO 的大小
        new_width = int(self.width() * 0.4)  # 调整为宽度的 40%
        new_height = int(new_width * (100 / 170))  # 锁定比例为 170:100
        self.logo_widget.setFixedSize(new_width, new_height)
        super().resizeEvent(event)

class SettingsGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Settings')
        self.resize(900, 700)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)

        # 添加分割器
        splitter = QSplitter(self)
        layout.addWidget(splitter)

        # 左侧菜单
        self.menu = QTreeWidget()
        self.menu.setHeaderHidden(True)
        splitter.addWidget(self.menu)

        # 添加菜单项
        settings_item = QTreeWidgetItem(self.menu, ['设置'])
        language_item = QTreeWidgetItem(settings_item, ['语言设置'])
        other_item = QTreeWidgetItem(settings_item, ['其他设置'])
        self.menu.expandAll()

        # 右侧页面
        self.pages = QStackedWidget()
        splitter.addWidget(self.pages)

        # 添加语言设置页面
        self.language_page = QWidget()
        language_layout = QVBoxLayout(self.language_page)
        language_label = QLabel('语言设置')
        language_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        language_layout.addWidget(language_label)
        self.pages.addWidget(self.language_page)

        # 添加其他设置页面
        self.other_page = QWidget()
        other_layout = QVBoxLayout(self.other_page)
        other_label = QLabel('其他设置')
        other_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        other_layout.addWidget(other_label)
        self.pages.addWidget(self.other_page)

        # 菜单点击事件
        self.menu.currentItemChanged.connect(self.change_page)

    def change_page(self, current, previous):
        if current.text(0) == '语言设置':
            self.pages.setCurrentWidget(self.language_page)
        elif current.text(0) == '其他设置':
            self.pages.setCurrentWidget(self.other_page)

class MainSettingsGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Main Settings')
        self.resize(900, 700)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)

        # 添加分割器
        splitter = QSplitter(self)
        layout.addWidget(splitter)

        # 左侧菜单
        self.menu = QTreeWidget()
        self.menu.setHeaderHidden(True)
        splitter.addWidget(self.menu)

        # 添加菜单项
        general_item = QTreeWidgetItem(self.menu, ['常规设置'])
        language_item = QTreeWidgetItem(self.menu, ['语言设置'])
        theme_item = QTreeWidgetItem(self.menu, ['主题设置'])
        self.menu.expandAll()

        # 右侧页面
        self.pages = QStackedWidget()
        splitter.addWidget(self.pages)

        # 添加常规设置页面
        self.general_page = QWidget()
        general_layout = QVBoxLayout(self.general_page)
        general_label = QLabel('常规设置')
        general_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        general_layout.addWidget(general_label)
        self.pages.addWidget(self.general_page)

        # 添加语言设置页面
        self.language_page = QWidget()
        language_layout = QVBoxLayout(self.language_page)
        language_label = QLabel('语言设置')
        language_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        language_layout.addWidget(language_label)
        self.pages.addWidget(self.language_page)

        # 添加主题设置页面
        self.theme_page = QWidget()
        theme_layout = QVBoxLayout(self.theme_page)
        theme_label = QLabel('主题设置')
        theme_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        theme_layout.addWidget(theme_label)
        self.pages.addWidget(self.theme_page)

        # 菜单点击事件
        self.menu.currentItemChanged.connect(self.change_page)

    def change_page(self, current, previous):
        if current.text(0) == '常规设置':
            self.pages.setCurrentWidget(self.general_page)
        elif current.text(0) == '语言设置':
            self.pages.setCurrentWidget(self.language_page)
        elif current.text(0) == '主题设置':
            self.pages.setCurrentWidget(self.theme_page)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 加载全局样式表
    with open('Style/global_stylesheet.qss', 'r', encoding='utf-8') as f:
        app.setStyleSheet(f.read())

    # 加载本地化翻译
    translator = QTranslator()
    locale = QLocale.system().name()  # 获取系统语言环境
    translation_path = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    if translator.load(f'qtbase_{locale}', translation_path):
        app.installTranslator(translator)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())
