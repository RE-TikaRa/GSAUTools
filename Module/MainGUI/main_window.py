from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                           QStackedWidget, QButtonGroup, QSplitter, QSizePolicy, QScrollArea)
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QIcon
from PyQt6.QtSvgWidgets import QSvgWidget
import qtawesome as qta
import os
import sys

from .components import SidebarButton, CardButton, SubMenu, FlowLayout
from Module.MEA.ExamGUI_PyQt import ExamGUI

# 导入主题管理器
try:
    from Module.settings.managers.theme_manager import theme_manager
    THEME_MANAGER_AVAILABLE = True
except ImportError:
    THEME_MANAGER_AVAILABLE = False
    print("主题管理器不可用")

# 优先尝试导入新的统一设置页面
try:
    from Module.settings.pages.unified_settings_page import UnifiedSettingsPage as SettingsPage
    print("使用统一风格设置页面")
except ImportError:
    try:
        from Module.settings.pages.advanced_settings_page import AdvancedSettingsPage as SettingsPage
        print("使用增强版设置页面")
    except ImportError:
        try:
            from Module.settings.pages.simple_settings_page import SimpleSettingsPage as SettingsPage
            print("使用简单设置页面")
        except ImportError:
            # 创建一个最基本的设置页面作为备用
            from PyQt6.QtWidgets import QLabel
            class SettingsPage(QWidget):
                def __init__(self):
                    super().__init__()
                    layout = QVBoxLayout(self)
                    layout.addWidget(QLabel("设置页面暂时不可用"))
            print("使用备用设置页面")

# 导入样式应用器
try:
    from Module.settings.components.ui_style_applicator import apply_theme_to_widget, setup_button_styles, setup_title_styles
    STYLE_APPLICATOR_AVAILABLE = True
except ImportError:
    STYLE_APPLICATOR_AVAILABLE = False
    print("样式应用器不可用")

class MainWindow(QMainWindow):
    """主窗口类"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GUI DEMO")
        self.resize(800, 600)
        self._init_ui()
        self._init_signals()
        self._apply_unified_styles()

    def _apply_unified_styles(self):
        """应用统一的样式系统"""
        # 暂时禁用统一样式系统，避免与主题切换冲突
        print("🔧 统一样式系统已禁用，使用主题管理器")

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
        self.sidebar.setObjectName("sidebar")  # 设置对象名以便样式识别

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

        # 功能卡片定义 - 扩展到更多功能
        self.card_defs = [
            ("MOOC考试解析", 'fa5s.chart-bar'),
            ("数据分析", 'fa5s.table'),
            ("图表生成", 'fa5s.chart-pie'),
            ("文件处理", 'fa5s.file-alt'),
            ("网络工具", 'fa5s.globe'),
            ("系统工具", 'fa5s.cogs'),
            ("文档管理", 'fa5s.folder-open'),
            ("导入导出", 'fa5s.exchange-alt'),
            ("批量处理", 'fa5s.tasks'),
            ("性能监控", 'fa5s.tachometer-alt'),
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
        
        self.dashboard_page = self._create_dashboard_page()
        self.features_page = self._create_features_page()
        self.feature_pages = self._create_feature_pages()
        self.settings_page = self._create_settings_page()
        self.about_page = self._create_about_page()

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
        
        # 连接主题变化信号
        if THEME_MANAGER_AVAILABLE:
            theme_manager.theme_changed.connect(self.update_theme_colors)

    def _create_dashboard_page(self):
        """创建仪表盘页面"""
        page = QWidget()
        page.setObjectName("dashboardPage")  # 设置对象名以便主题识别
        layout = QVBoxLayout(page)
        layout.addStretch()

        logo_widget = QSvgWidget("Img/LOGO.svg")
        logo_widget.setFixedSize(400, 235)
        layout.addWidget(logo_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        self.logo_widget = logo_widget  # 保存引用以便调整大小

        layout.addStretch()
        return page

    def _create_features_page(self):
        """创建功能页面 - 自适应卡片布局"""
        page = QWidget()
        page.setObjectName("featuresPage")  # 设置对象名以便主题识别
        
        # 主布局
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # 页面标题
        header = QLabel("功能中心")
        header.setObjectName("pageHeader")  # 使用主题识别的对象名
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("pageScrollArea")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # 卡片容器
        cards_container = QWidget()
        cards_container.setObjectName("cardsContainer")
        cards_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # 使用FlowLayout来布局卡片，实现自适应
        try:
            # 尝试使用改进的响应式布局
            from Module.settings.layouts.responsive_layout import ResponsiveFlowLayout
            flow = ResponsiveFlowLayout(spacing=20)
            flow.setContentsMargins(20, 20, 20, 20)
            flow.max_columns = 6  # 设置最大列数，会自动根据窗口宽度调整
            print("✅ 使用改进的ResponsiveFlowLayout")
        except ImportError:
            # 备用：使用原始FlowLayout
            from .components import FlowLayout
            flow = FlowLayout(spacing=20)
            flow.setContentsMargins(20, 20, 20, 20)
            flow.max_columns = 6
            print("⚠️ 使用原始FlowLayout")
        cards_container.setLayout(flow)
        
        # 设置滚动区域的内容
        scroll.setWidget(cards_container)

        # 创建卡片
        self.feature_cards = []
        
        for i, (label_text, icon_name) in enumerate(self.card_defs):
            try:
                # 创建 CardButton 时显式指定父对象为 cards_container，防止成为顶级窗口
                btn = CardButton(label_text, parent=cards_container)
                btn.setObjectName(f"featureCard_{i}")  # 设置唯一的对象名
                
                icon = qta.icon(icon_name)
                pixmap = icon.pixmap(48, 48)
                btn.setIcon(QIcon(pixmap))
                
                btn.setAccessibleName(label_text)
                btn.setToolTip(f"点击进入{label_text}功能")
                
                # 设置卡片属性，增强可用性
                btn.setCheckable(True)
                btn.setAutoExclusive(False)  # 允许手动管理选中状态
                
                self.feature_cards.append(btn)
                flow.addWidget(btn)
                
            except Exception as e:
                print(f"创建卡片 {label_text} 失败: {str(e)}")
        
        # 移除硬编码的滚动条样式，使用主题样式
        layout.addWidget(scroll)
        
        return page

    def _create_feature_pages(self):
        """创建功能详情页面"""
        pages = []
        for i, (label_text, icon_name) in enumerate(self.card_defs):
            if i == 0:
                try:
                    # embed ExamGUI as a child widget so it doesn't create its own top-level window
                    page = ExamGUI(parent=self.content_stack)
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
        page.setObjectName("placeholderPage")  # 设置对象名以便主题识别
        layout = QVBoxLayout(page)
        layout.addStretch()
        label = QLabel(title)
        label.setObjectName("placeholderLabel")  # 设置对象名以便主题识别
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        layout.addStretch()
        return page

    def _create_settings_page(self):
        """创建设置页面"""
        return SettingsPage()

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
    
    def update_theme_colors(self):
        """更新主题相关的颜色，解决主题切换时颜色不更新的问题"""
        # 强制刷新所有按钮的样式
        for button in [self.dashboard_btn, self.features_btn, self.settings_btn, self.about_btn]:
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()
        
        # 强制刷新功能卡片的样式
        for card in self.feature_cards:
            card.style().unpolish(card)
            card.style().polish(card)
            card.update()
            # 更新内部文本标签
            if hasattr(card, 'text_label'):
                card.text_label.style().unpolish(card.text_label)
                card.text_label.style().polish(card.text_label)
                card.text_label.update()
        
        # 强制刷新子菜单按钮
        for btn in self.submenu_buttons:
            btn.style().unpolish(btn)
            btn.style().polish(btn)
            btn.update()
        
        # 强制刷新设置页面和其他页面的组件
        # 获取堆叠容器中的所有页面
        stacked_widget = getattr(self, 'content_stack', None)
        if stacked_widget:
            for i in range(stacked_widget.count()):
                page = stacked_widget.widget(i)
                if page:
                    self._refresh_widget_recursively(page)
        
        # 刷新整个窗口
        try:
            style = self.style()
            if style:
                style.unpolish(self)
                style.polish(self)
        except:
            pass
        self.update()
        
    def _refresh_widget_recursively(self, widget):
        """递归刷新widget及其所有子组件的样式"""
        try:
            # 刷新当前widget
            style = widget.style()
            if style:
                style.unpolish(widget)
                style.polish(widget)
            widget.update()
            
            # 递归刷新所有子组件
            for child in widget.findChildren(QWidget):
                if child.parent() == widget:  # 只刷新直接子组件
                    self._refresh_widget_recursively(child)
        except Exception as e:
            print(f"刷新组件样式时出错: {e}")
        self.style().polish(self)
        self.update()
