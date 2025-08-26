from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QLabel, QStackedWidget, QButtonGroup, QSplitter, QSizePolicy)
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QIcon
from PyQt6.QtSvgWidgets import QSvgWidget
import qtawesome as qta
import os
import sys

from .components import SidebarButton, CardButton, SubMenu, FlowLayout
from Module.MEA.ExamGUI_PyQt import ExamGUI

class MainWindow(QMainWindow):
    """主窗口类"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GUI DEMO")
        self.resize(800, 600)
        self._init_ui()
        self._init_signals()

    def _init_ui(self):
        """初始化UI"""
        # 创建主布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self._setup_sidebar()
        self._setup_content()
        
        # 添加侧边栏和内容区到主布局
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_stack)

        # 设置初始状态
        self.sidebar_expanded = True
        self.current_page = 0
        self.dashboard_btn.setChecked(True)
        self.features_btn.setChecked(False)
        self.content_stack.setCurrentIndex(0)

    def _setup_sidebar(self):
        """设置侧边栏"""
        self.sidebar = QWidget()
        self.sidebar.setFixedWidth(200)
        self.sidebar.setStyleSheet("""
            QWidget {
                background-color: #6b6966;
                color: #f3efea;
            }
            QPushButton {
                text-align: left;
                padding: 5px 10px;
                border: none;
                background-color: transparent;
                color: #f3efea;
            }
            QPushButton:hover {
                background-color: #7f7d7a;
            }
            QPushButton:checked {
                background-color: #bda9a2;
                color: #2f2d2b;
            }
        """)

        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # 折叠按钮
        self.toggle_button = SidebarButton(icon_name='fa5s.bars')
        self.toggle_button.clicked.connect(self.toggle_sidebar)
        sidebar_layout.addWidget(self.toggle_button)

        # 主菜单按钮
        self.dashboard_btn = SidebarButton("主页", 'fa5s.home')
        self.features_btn = SidebarButton("功能", 'fa5s.th-list')

        # 功能卡片定义
        self.card_defs = [
            ("MOOCExamAnalyzer", 'fa5s.chart-bar'),
            ("功能 2", 'fa5s.table'),
            ("功能 3", 'fa5s.chart-pie'),
            ("功能 4", 'fa5s.cubes'),
        ]

        # 子菜单
        self.features_submenu = SubMenu()
        self.submenu_buttons = []
        for label_text, icon_name in self.card_defs:
            sb = self.features_submenu.addButton(label_text, icon_name)
            self.submenu_buttons.append(sb)

        # 设置和关于按钮
        self.settings_btn = SidebarButton("设置", 'fa5s.cog')
        self.about_btn = SidebarButton("关于", 'fa5s.info-circle')

        # 添加所有按钮到侧边栏
        sidebar_layout.addWidget(self.dashboard_btn)
        sidebar_layout.addWidget(self.features_btn)
        sidebar_layout.addWidget(self.features_submenu)
        sidebar_layout.addWidget(self.settings_btn)
        sidebar_layout.addWidget(self.about_btn)
        sidebar_layout.addStretch()

    def _setup_content(self):
        """设置内容区"""
        self.content_stack = QStackedWidget()
        
        # 仪表盘页面
        self.dashboard_page = self._create_dashboard_page()
        
        # 功能页面
        self.features_page = self._create_features_page()
        
        # 功能详情页面
        self.feature_pages = self._create_feature_pages()
        
        # 设置和关于页面
        self.settings_page = self._create_settings_page()
        self.about_page = self._create_about_page()

        # 添加所有页面到堆栈
        self.content_stack.addWidget(self.dashboard_page)
        self.content_stack.addWidget(self.features_page)
        for page in self.feature_pages:
            self.content_stack.addWidget(page)
        self.content_stack.addWidget(self.settings_page)
        self.content_stack.addWidget(self.about_page)

    def _init_signals(self):
        """初始化信号连接"""
        # 设置按钮和页面的映射关系
        self.menu_buttons = [self.dashboard_btn, self.features_btn, 
                           self.settings_btn, self.about_btn]
        
        # 主按钮映射到主页面索引
        self.button_page_map = {
            self.dashboard_btn: 0,
            self.features_btn: 1,
            self.settings_btn: 2 + len(self.feature_pages),
            self.about_btn: 3 + len(self.feature_pages)
        }

        # 反向映射
        self.page_button_map = {v: k for k, v in self.button_page_map.items()}

        # 创建按钮组
        self.submenu_btngroup = QButtonGroup(self)
        self.submenu_btngroup.setExclusive(True)
        self.cards_btngroup = QButtonGroup(self)
        self.cards_btngroup.setExclusive(True)

        # 添加按钮到按钮组
        for i, sb in enumerate(self.submenu_buttons):
            self.submenu_btngroup.addButton(sb, i)
        for i, card in enumerate(self.feature_cards):
            self.cards_btngroup.addButton(card, i)
            card.clicked.connect(lambda checked, i=i: self.feature_card_clicked(i))

        # 连接信号
        self.submenu_btngroup.idClicked.connect(self.on_submenu_id_clicked)
        self.cards_btngroup.idClicked.connect(self.on_card_id_clicked)
        
        for button in self.menu_buttons:
            if button == self.features_btn:
                button.clicked.connect(self.toggle_features_menu)
            if button in self.button_page_map:
                page_index = self.button_page_map[button]
                button.clicked.connect(lambda checked, idx=page_index: self.switch_page(idx))

    def _create_dashboard_page(self):
        """创建仪表盘页面"""
        page = QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QVBoxLayout(page)
        layout.addStretch()

        logo_widget = QSvgWidget("img/LOGO.svg")
        logo_widget.setFixedSize(400, 235)
        layout.addWidget(logo_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        self.logo_widget = logo_widget  # 保存引用以便调整大小

        layout.addStretch()
        return page

    def _create_features_page(self):
        """创建功能页面"""
        page = QWidget()
        page.setStyleSheet("background-color: #f5f7fa;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        header = QLabel("功能 - 卡片式二级菜单")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # 创建功能卡片
        self.feature_cards = []
        cards_container = QWidget()
        flow = FlowLayout()
        cards_container.setLayout(flow)

        for label_text, icon_name in self.card_defs:
            pix = qta.icon(icon_name).pixmap(64, 64)
            btn = CardButton(label_text, pix)
            btn.setAccessibleName(label_text)
            btn.setToolTip(label_text)
            self.feature_cards.append(btn)
            flow.addWidget(btn)

        cards_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        cards_container.setMinimumHeight(220)
        layout.addWidget(cards_container)
        layout.addStretch()

        return page

    def _create_feature_pages(self):
        """创建功能详情页面"""
        pages = []
        for i, (label_text, icon_name) in enumerate(self.card_defs):
            if i == 0:
                try:
                    page = ExamGUI()
                except Exception as e:
                    print(f"Failed to embed ExamGUI: {e}")
                    page = self._create_placeholder_page(f"{label_text} (Exam GUI 加载失败)")
            else:
                page = self._create_placeholder_page(f"{label_text} 页面")
            pages.append(page)
        return pages

    def _create_placeholder_page(self, title):
        """创建占位页面"""
        page = QWidget()
        page.setStyleSheet("background-color: white;")
        layout = QVBoxLayout(page)
        layout.addStretch()
        label = QLabel(title)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        layout.addStretch()
        return page

    def _create_settings_page(self):
        """创建设置页面"""
        return self._create_placeholder_page("设置页面")

    def _create_about_page(self):
        """创建关于页面"""
        return self._create_placeholder_page("关于页面")

    # 事件处理方法
    def switch_page(self, page_index):
        """切换页面"""
        if self.current_page == page_index:
            return
            
        self.current_page = page_index
        self.content_stack.setCurrentIndex(page_index)
        
        for button in self.menu_buttons:
            button.setChecked(button == self.page_button_map.get(page_index))

        features_index = self.button_page_map.get(self.features_btn)
        if page_index == features_index:
            if self.sidebar_expanded and not self.features_submenu.isVisible():
                self.expand_submenu()
        else:
            if self.features_submenu.isVisible():
                self.collapse_submenu()

    def on_submenu_id_clicked(self, id):
        """子菜单按钮点击处理"""
        try:
            self.cards_btngroup.blockSignals(True)
            btn = self.cards_btngroup.button(id)
            if btn:
                btn.setChecked(True)
            self.features_btn.setChecked(True)
            page_index = 2 + id
            self.switch_page(page_index)
        finally:
            self.cards_btngroup.blockSignals(False)

    def on_card_id_clicked(self, id):
        """卡片点击处理"""
        try:
            self.submenu_btngroup.blockSignals(True)
            sb = self.submenu_btngroup.button(id)
            if sb:
                sb.setChecked(True)
            self.features_btn.setChecked(True)
            page_index = 2 + id
            self.switch_page(page_index)
        finally:
            self.submenu_btngroup.blockSignals(False)

    def feature_card_clicked(self, idx):
        """功能卡片点击处理"""
        if idx < len(self.submenu_buttons):
            self.handle_submenu_button_click(self.submenu_buttons[idx])

    def handle_submenu_button_click(self, clicked_button):
        """子菜单按钮点击处理"""
        try:
            idx = self.submenu_buttons.index(clicked_button)
        except ValueError:
            return

        btn = self.submenu_btngroup.button(idx)
        if btn:
            btn.setChecked(True)
        self.features_btn.setChecked(True)
        
        self.cards_btngroup.blockSignals(True)
        try:
            for i, c in enumerate(self.feature_cards):
                c.setChecked(i == idx)
        finally:
            self.cards_btngroup.blockSignals(False)

    def toggle_features_menu(self):
        """切换功能菜单显示状态"""
        if hasattr(self, 'submenu_animation') and self.submenu_animation.state() == QPropertyAnimation.State.Running:
            return
            
        is_features_checked = self.features_btn.isChecked()
        
        if is_features_checked and not self.features_submenu.isVisible():
            for button in self.menu_buttons:
                if button != self.features_btn:
                    button.setChecked(False)
            self.expand_submenu()
            self.switch_page(self.button_page_map[self.features_btn])
        elif not is_features_checked and self.features_submenu.isVisible():
            self.collapse_submenu()
            
            if self.current_page in self.page_button_map:
                mapped_btn = self.page_button_map[self.current_page]
                if mapped_btn != self.features_btn:
                    mapped_btn.setChecked(True)

    def toggle_sidebar(self):
        """切换侧边栏显示状态"""
        if (hasattr(self, 'animation') and self.animation.state() == QPropertyAnimation.State.Running) or \
           (hasattr(self, 'submenu_animation') and self.submenu_animation.state() == QPropertyAnimation.State.Running):
            return

        if self.sidebar_expanded and self.features_submenu.isVisible():
            self.features_btn.setChecked(False)
            self.collapse_submenu()

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
        """展开子菜单"""
        if not self.sidebar_expanded:
            return
            
        self.features_submenu.setVisible(True)
        self.features_submenu.setMaximumHeight(0)
        
        required_height = self.features_submenu._layout.sizeHint().height()
        
        self.submenu_animation = QPropertyAnimation(self.features_submenu, b"maximumHeight")
        self.submenu_animation.setStartValue(0)
        self.submenu_animation.setEndValue(required_height)
        self.submenu_animation.setDuration(150)
        self.submenu_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.submenu_animation.start()

    def collapse_submenu(self):
        """收起子菜单"""
        if self.features_submenu.isVisible():
            current_height = self.features_submenu.height()
            self.submenu_animation = QPropertyAnimation(self.features_submenu, b"maximumHeight")
            self.submenu_animation.setStartValue(current_height)
            self.submenu_animation.setEndValue(0)
            self.submenu_animation.setDuration(150)
            self.submenu_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            self.submenu_animation.finished.connect(lambda: self.features_submenu.setVisible(False))
            self.submenu_animation.start()
            
            for btn in self.submenu_buttons:
                btn.setChecked(False)

    def update_button_text(self, expanded):
        """更新按钮文本"""
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
        """窗口大小改变事件处理"""
        new_width = int(self.width() * 0.4)
        new_height = int(new_width * (100 / 170))
        self.logo_widget.setFixedSize(new_width, new_height)
        super().resizeEvent(event)
