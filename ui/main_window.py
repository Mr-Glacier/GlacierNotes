from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTreeWidget, QTreeWidgetItem, QTextEdit, QPushButton, QInputDialog,
    QMessageBox, QLabel, QFrame, QScrollArea, QToolBar, QFontComboBox, QComboBox, QColorDialog, QLineEdit,
    QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QTextCharFormat, QFontDatabase, QTextCursor, QIcon, QColor
from PyQt5.QtWidgets import QAction, QToolButton
from models.category_model import CategoryModel
from models.note_model import NoteModel


class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        # 1.设置界面尺寸以及图标
        self.setWindowTitle("GlacierNotes")
        self.setWindowIcon(QIcon("./public/notes.ico"))
        self.resize(1200, 800)

        # 2.初始化字体设置
        self.init_fonts()

        # 3.相关数据链接
        self.db = db
        self.category_model = CategoryModel(db)
        self.note_model = NoteModel(db)

        self.current_category_id = None
        self.current_note_id = None
        self.tree_widget = None

        # 4.设置界面UI
        self.setup_ui()
        # 5.加载笔记分类
        self.load_categories()

    def init_fonts(self):
        """设置系统中基本的字体样式"""
        # 设置基础字体
        font = QFont()
        font.setFamily("Microsoft YaHei" if "Microsoft YaHei" in QFontDatabase().families() else "Arial")
        font.setPointSize(10)
        self.setFont(font)

    def setup_ui(self):
        """系统中主要 UI 设计"""
        main_splitter = QSplitter(Qt.Horizontal)

        # [左侧区域]
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)
        left_layout.setSpacing(10)

        # [左侧区域]-按钮区域
        # 按钮样式设置
        button_style = """
        QPushButton {
            background-color: #3B82F6; /* 清澈蓝 */
            border: none;
            color: white;
            padding: 10px 24px;
            text-align: center;
            font-size: 16px;
            margin: 4px 2px;
            border-radius: 8px;
            font-weight:  500;
            font-family: "Microsoft YaHei", "Arial", sans-serif; /* 首选微软雅黑，其次Arial */
        }

        QPushButton:hover {
            background-color: #2563EB; /* 稍微深一点的蓝，增强悬停反馈 */
        }

        QPushButton:pressed {
            background-color: #1D4ED8; /* 按下时更深的蓝，提升交互感知 */
        }

        QPushButton:disabled {
            background-color: #93C5FD; /* 浅蓝表示不可点击状态 */
            color: #E2E8F0;
        }
        """
        # 操作按钮区
        btn_layout = QHBoxLayout()
        btn_add_category = QPushButton("+分类")
        btn_add_note = QPushButton("+笔记")
        btn_delete = QPushButton("DELETE")
        # 给所有按钮添加阴影效果
        buttons = [btn_add_category, btn_add_note, btn_delete]
        for btn in buttons:
            btn.setStyleSheet(button_style)
            # 设置按钮大小
            btn.setFixedSize(*(130, 50))
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(15)
            shadow.setColor(QColor(0, 0, 0, 160))  # 黑色带透明度
            shadow.setOffset(3, 3)
            btn.setGraphicsEffect(shadow)

        btn_add_category.clicked.connect(self.add_category)
        btn_add_note.clicked.connect(self.add_note)
        btn_delete.clicked.connect(self.delete_item)

        btn_layout.addWidget(btn_add_category)
        btn_layout.addWidget(btn_add_note)
        btn_layout.addWidget(btn_delete)
        left_layout.addLayout(btn_layout)
        # end 左侧按钮区

        # [左侧区域]-分类笔记列表区域
        # [左侧区域]-分类笔记列表区域

        # 标签字体设置
        category_label = QLabel("📘 笔记列表")
        category_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #333;
            padding: 5px 0;
        """)
        # TreeWidget 设置
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)  # 隐藏标题栏
        self.tree_widget.setFont(QFont("Microsoft YaHei", 10))  # 使用现代字体

        # 设置样式（QSS）- 更现代、美观
        self.tree_widget.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #ccc;
                border-radius: 6px;
                background-color: #f9f9f9;
                padding: 5px;
                outline: 0px; /* 去掉虚线框 */
            }

            QTreeWidget::item {
                padding-left: 8px;
                padding-right: 8px;
                height: 30px;
                border-radius: 4px;
            }

            QTreeWidget::item:selected {
                background-color: #bfdbfe; /* 浅蓝背景 */
                color: #1e40af; /* 深蓝色文字 */
                font-weight: bold;
            }

            QTreeWidget::item:hover {
                background-color: #dbeafe;
                color: #1e3a8a;
            }

            QScrollBar:vertical {
                border-radius: 4px;
                background: #f1f1f1;
                width: 10px;
            }

            QScrollBar::handle:vertical {
                background: #d1d5db;
                min-height: 20px;
                border-radius: 4px;
            }

            QScrollBar::add-line, QScrollBar::sub-line {
                background: none;
            }

            QScrollBar::add-page, QScrollBar::sub-page {
                background: none;
            }
        """)

        # 连接点击事件
        self.tree_widget.itemClicked.connect(self.on_tree_item_clicked)

        # 将组件加入布局
        left_layout.addWidget(category_label)
        left_layout.addWidget(self.tree_widget)

        # 右侧编辑区域
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(15)

        # 创建格式工具栏
        self.format_toolbar = QToolBar("文本格式")
        self.addToolBar(Qt.TopToolBarArea, self.format_toolbar)

        # 字体选择框
        self.font_combo = QFontComboBox()
        self.font_combo.currentFontChanged.connect(self.set_text_font)
        self.format_toolbar.addWidget(self.font_combo)

        # 字号选择框
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems(
            ["8", "9", "10", "11", "12", "14", "16", "18", "20", "22", "24", "26", "28", "36", "48", "72"])
        self.font_size_combo.setCurrentText("16")
        self.font_size_combo.currentTextChanged.connect(self.set_text_size)
        self.format_toolbar.addWidget(self.font_size_combo)

        # 加粗按钮
        self.bold_action = QAction("加粗", self)
        self.bold_action.setCheckable(True)
        self.bold_action.setShortcut("Ctrl+B")
        self.bold_action.triggered.connect(self.set_text_bold)
        self.format_toolbar.addAction(self.bold_action)

        # 斜体按钮
        self.italic_action = QAction("斜体", self)
        self.italic_action.setCheckable(True)
        self.italic_action.setShortcut("Ctrl+I")
        self.italic_action.triggered.connect(self.set_text_italic)
        self.format_toolbar.addAction(self.italic_action)

        # 下划线按钮
        self.underline_action = QAction("下划线", self)
        self.underline_action.setCheckable(True)
        self.underline_action.setShortcut("Ctrl+U")
        self.underline_action.triggered.connect(self.set_text_underline)
        self.format_toolbar.addAction(self.underline_action)

        # 颜色按钮
        self.color_action = QAction("颜色", self)
        self.color_action.triggered.connect(self.set_text_color)
        self.format_toolbar.addAction(self.color_action)

        # 标题编辑区域 - 使用 QLineEdit
        title_label = QLabel("<b>标题</b>")
        title_label_font = QFont()
        title_label_font.setPointSize(16)
        title_label.setFont(title_label_font)
        right_layout.addWidget(title_label)

        self.title_edit = QLineEdit()  # 使用 QLineEdit 而不是 QTextEdit
        self.title_edit.setMaximumHeight(40)
        self.title_edit.setPlaceholderText("输入笔记标题...")
        title_font = QFont()
        title_font.setPointSize(18)
        self.title_edit.setFont(title_font)
        self.title_edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        right_layout.addWidget(self.title_edit)

        # 内容编辑区域
        content_label = QLabel("<b>内容</b>")
        content_label.setFont(title_label_font)
        right_layout.addWidget(content_label)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        self.content_edit = QTextEdit()
        self.content_edit.setPlaceholderText("输入笔记内容...")
        content_font = QFont()
        content_font.setPointSize(16)
        self.content_edit.setFont(content_font)
        self.content_edit.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 15px;
            }
        """)
        scroll_area.setWidget(self.content_edit)
        right_layout.addWidget(scroll_area, 1)

        # 保存按钮
        btn_save = QPushButton("保存笔记")
        btn_save.setFixedSize(120, 40)
        btn_save.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        btn_save.clicked.connect(self.save_note)
        right_layout.addWidget(btn_save, 0, Qt.AlignRight)

        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([300, 900])
        self.setCentralWidget(main_splitter)

        # 状态栏字体
        status_font = QFont()
        status_font.setPointSize(10)
        self.statusBar().setFont(status_font)
        self.statusBar().showMessage("就绪")
        self.clear_format_action = QAction("清除格式", self)
        self.clear_format_action.triggered.connect(self.clear_text_format)
        self.format_toolbar.addAction(self.clear_format_action)

    # 添加清除格式方法
    def clear_text_format(self):
        fmt = QTextCharFormat()
        cursor = self.content_edit.textCursor()
        cursor.mergeCharFormat(fmt)
        self.content_edit.setCurrentCharFormat(fmt)
        self.update_format_toolbar()

    # 文本格式设置方法
    def set_text_bold(self):
        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Bold if self.bold_action.isChecked() else QFont.Normal)
        self.merge_format_on_word_or_selection(fmt)

    def set_text_italic(self):
        fmt = QTextCharFormat()
        fmt.setFontItalic(self.italic_action.isChecked())
        self.merge_format_on_word_or_selection(fmt)

    def set_text_underline(self):
        fmt = QTextCharFormat()
        fmt.setFontUnderline(self.underline_action.isChecked())
        self.merge_format_on_word_or_selection(fmt)

    def set_text_font(self, font):
        fmt = QTextCharFormat()
        fmt.setFontFamily(font.family())
        self.merge_format_on_word_or_selection(fmt)

    def set_text_size(self, size):
        fmt = QTextCharFormat()
        fmt.setFontPointSize(float(size))
        self.merge_format_on_word_or_selection(fmt)

    def set_text_color(self):
        color = QColorDialog.getColor(self.content_edit.textColor(), self)
        if color.isValid():
            fmt = QTextCharFormat()
            fmt.setForeground(color)
            self.merge_format_on_word_or_selection(fmt)

    def merge_format_on_word_or_selection(self, format):
        """改进的格式合并方法，确保不会意外改变整个文档格式"""
        cursor = self.content_edit.textCursor()

        # 如果没有选择文本，获取当前光标位置的单词
        if not cursor.hasSelection():
            cursor.select(QTextCursor.WordUnderCursor)

        # 合并格式
        cursor.mergeCharFormat(format)

        # 更新当前格式
        self.content_edit.setCurrentCharFormat(format)

        # 更新工具栏状态
        self.update_format_toolbar()

    def load_categories(self):
        try:
            self.tree_widget.clear()
            categories = self.category_model.get_all()

            for category in categories:
                category_item = QTreeWidgetItem(self.tree_widget)
                category_item.setText(0, category['name'])
                category_item.setData(0, Qt.UserRole, ('category', category['id']))
                notes = self.note_model.get_by_category(category['id'])
                for note in notes:
                    note_item = QTreeWidgetItem(category_item)
                    note_item.setText(0, note['title'])
                    note_item.setData(0, Qt.UserRole, ('note', note['id']))
                category_item.setExpanded(True)
        except Exception as e:
            print(f"[load_categories] 加载分类失败: {e}")
            QMessageBox.critical(self, "错误", "加载分类和笔记失败，请检查数据库连接")

    def on_tree_item_clicked(self, item, column):
        item_data = item.data(0, Qt.UserRole)
        if not item_data:
            return

        item_type, item_id = item_data

        if item_type == 'category':
            self.current_category_id = item_id
            self.current_note_id = None
            self.title_edit.clear()
            self.content_edit.clear()
            self.statusBar().showMessage(f"已选择分类: {item.text(0)}", 3000)
        elif item_type == 'note':
            self.current_note_id = item_id
            note = self.note_model.get_by_id(item_id)
            if note:
                self.current_category_id = note['category_id']
                self.title_edit.setText(note['title'])  # 改为 setText()
                self.content_edit.setPlainText(note['content'])
                self.statusBar().showMessage(f"正在编辑: {note['title']}", 3000)

    def add_category(self):
        name, ok = QInputDialog.getText(self, "添加分类", "分类名称:")
        if ok and name.strip():
            try:
                self.category_model.add(name.strip())
                self.load_categories()
                self.statusBar().showMessage("分类添加成功", 3000)
            except Exception as e:
                print(f"[add_category] 添加失败: {e}")
                QMessageBox.critical(self, "错误", "添加分类失败，请检查数据库")

    def add_note(self):
        current_item = self.tree_widget.currentItem()
        if not current_item or current_item.data(0, Qt.UserRole)[0] != 'category':
            QMessageBox.warning(self, "提示", "请先选择一个分类以添加笔记")
            return

        category_id = current_item.data(0, Qt.UserRole)[1]
        title, ok = QInputDialog.getText(self, "添加笔记", "笔记标题:")
        if ok and title.strip():
            try:
                note_id = self.note_model.add(category_id, title.strip())
                self.load_categories()
                self.select_note_by_id(note_id)
                self.title_edit.setText("")  # 清空标题编辑框
                self.content_edit.setPlainText("")  # 清空内容编辑框
                self.statusBar().showMessage("笔记添加成功", 3000)
            except Exception as e:
                print(f"[add_note] 添加失败: {e}")
                QMessageBox.critical(self, "错误", "添加笔记失败")

    def select_note_by_id(self, note_id):
        def search_items(parent):
            for i in range(parent.childCount()):
                item = parent.child(i)
                data = item.data(0, Qt.UserRole)
                if data and data[0] == 'note' and data[1] == note_id:
                    self.tree_widget.setCurrentItem(item)
                    self.on_tree_item_clicked(item, 0)
                    return True
                if search_items(item):
                    return True
            return False

        for i in range(self.tree_widget.topLevelItemCount()):
            if search_items(self.tree_widget.topLevelItem(i)):
                break

    def delete_item(self):
        """删除操作"""
        current_item = self.tree_widget.currentItem()
        if not current_item:
            return

        item_data = current_item.data(0, Qt.UserRole)
        if not item_data:
            return

        item_type, item_id = item_data

        try:
            if item_type == 'category':
                reply = QMessageBox.question(
                    self, '确认删除',
                    f"确定要删除分类 '{current_item.text(0)}' 及其所有笔记吗?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.category_model.delete(item_id)
                    self.load_categories()
                    self.title_edit.clear()
                    self.content_edit.clear()
                    self.statusBar().showMessage("分类已删除", 3000)
            elif item_type == 'note':
                reply = QMessageBox.question(
                    self, '确认删除',
                    f"确定要删除笔记 '{current_item.text(0)}' 吗?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.note_model.delete(item_id)
                    self.load_categories()
                    if self.current_note_id == item_id:
                        self.title_edit.clear()
                        self.content_edit.clear()
                        self.current_note_id = None
                    self.statusBar().showMessage("笔记已删除", 3000)
        except Exception as e:
            print(f"[delete_item] 删除失败: {e}")
            QMessageBox.critical(self, "错误", "删除失败")

    def save_note(self):
        """保存笔记，支持新建和更新，保留文本格式"""
        # 获取标题和内容
        title = self.title_edit.text().strip()  # 使用text()而不是toPlainText()
        content = self.content_edit.toHtml() if self.content_edit.toHtml().strip() else self.content_edit.toPlainText().strip()

        # 验证标题
        if not title:
            QMessageBox.warning(self, "提示", "笔记标题不能为空")
            return

        try:
            # 新建笔记的情况
            if not self.current_note_id:
                if not self.current_category_id:
                    QMessageBox.warning(self, "提示", "请先选择一个分类以保存笔记")
                    return

                # 添加新笔记
                note_id = self.note_model.add(self.current_category_id, title)
                self.note_model.update(note_id, content=content)
                self.current_note_id = note_id
                message = "笔记已创建并保存"

                # 更新UI
                self.load_categories()
                self.select_note_by_id(note_id)
            else:
                # 更新现有笔记
                self.note_model.update(self.current_note_id, title=title, content=content)
                message = "笔记已更新"

                # 更新树形控件中的标题
                self.update_note_title_in_tree(self.current_note_id, title)

            self.statusBar().showMessage(message, 3000)

        except Exception as e:
            error_msg = f"保存笔记失败: {str(e)}"
            print(f"[save_note] {error_msg}")
            QMessageBox.critical(self, "错误", error_msg)

    def load_note_content(self, note_id):
        """加载笔记内容，正确处理富文本格式"""
        note = self.db.get_note(note_id)
        if note:
            self.title_edit.setPlainText(note['title'])

            # 先获取内容
            content = note['content']

            # 检查是否是HTML格式（富文本）
            if content.strip().startswith('<!DOCTYPE') or '<html>' in content.lower():
                self.content_edit.setHtml(content)
            else:
                # 如果是纯文本，使用setPlainText
                self.content_edit.setPlainText(content)

            # 重置格式工具栏状态
            self.update_format_toolbar()

    def update_format_toolbar(self):
        """更新格式工具栏状态以匹配当前光标位置的格式"""
        cursor = self.content_edit.textCursor()
        format = cursor.charFormat()

        # 更新字体选择框
        self.font_combo.setCurrentFont(format.font())

        # 更新字号选择框
        font_size = format.fontPointSize()
        if font_size > 0:
            self.font_size_combo.setCurrentText(str(int(font_size)))
        else:
            self.font_size_combo.setCurrentText("16")  # 默认值

        # 更新加粗、斜体、下划线按钮状态
        self.bold_action.setChecked(format.fontWeight() == QFont.Bold)
        self.italic_action.setChecked(format.fontItalic())
        self.underline_action.setChecked(format.fontUnderline())
