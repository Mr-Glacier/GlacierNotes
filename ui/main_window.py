from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTreeWidget, QTreeWidgetItem, QTextEdit, QPushButton, QInputDialog,
    QMessageBox, QLabel, QFrame, QScrollArea, QToolBar, QFontComboBox, QComboBox, QColorDialog, QLineEdit,
    QGraphicsDropShadowEffect, QFileDialog, QShortcut
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QTextCharFormat, QFontDatabase, QTextCursor, QIcon, QColor, QImage, QTextBlockFormat, \
    QKeySequence
from PyQt5.QtWidgets import QAction, QToolButton
from models.category_model import CategoryModel
from models.note_model import NoteModel
from utils.rich_text_edit import RichTextEdit


class MainWindow(QMainWindow):
    def __init__(self, db):
        super().__init__()
        # 1.设置界面尺寸以及图标
        self.font_size_combo = None
        self.font_combo = None
        self.setWindowTitle("GlacierNotes")
        self.setWindowIcon(QIcon("./public/ico_notes.png"))
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
        self.title_edit = None
        self.format_toolbar = None

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
        left_layout.setContentsMargins(10, 5, 5, 5)
        left_layout.setSpacing(10)

        # TODO [左侧区域]-按钮区域
        # 按钮样式设置
        button_style = """
        QPushButton {
            background-color: #3B82F6; /* 清澈蓝 */
            border: none;
            color: white;
            padding: 6px 12px;
            text-align: center;
            font-size: 14px;
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
            btn.setFixedSize(*(120, 40))
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(15)
            shadow.setColor(QColor(0, 0, 0, 130))  # 黑色带透明度
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
        # end 左侧分类笔记列表区域
        # end 左侧区域全部结束

        # TODO [右侧区域]
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(5, 5, 10, 5)
        right_layout.setSpacing(15)

        # 统一样式常量
        STYLE = {
            "primary_color": "#4CAF50",
            "hover_color": "#45a049",
            "border_color": "#ddd",
            "focus_color": "#dbeafe",
            "placeholder_color": "#aaa",
            "bg_color": "#ffffff"
        }

        # 标题区域
        self.title_edit = QLineEdit()
        self.title_edit.setMaximumHeight(50)
        self.title_edit.setPlaceholderText("输入笔记标题...")
        self.title_edit.setStyleSheet(f"""
            QLineEdit {{
                border: 2px solid {STYLE['border_color']};
                border-radius: 6px;
                padding: 10px;
                font-size: 16pt;
                background-color: white;
            }}
            QLineEdit:focus {{
                border-color: {STYLE['focus_color']};
                outline: 0;
                box-shadow: 0 0 0 2px rgba(138, 180, 248, 0.3);
            }}
            QLineEdit::placeholder {{
                color: {STYLE['placeholder_color']};
            }}
        """)
        right_layout.addWidget(self.title_edit)
        # end 标题区域

        self.format_toolbar = QToolBar("文本格式")
        self.format_toolbar.setStyleSheet("""
                    QToolBar {
                        background: transparent;
                        padding: 5px;
                        spacing: 5px;
                    }
                    QToolButton {
                        padding: 3px;
                    }
                """)

        # 字体选择
        self.font_combo = QFontComboBox()
        self.font_combo.currentFontChanged.connect(self.set_text_font)
        self.format_toolbar.addWidget(self.font_combo)

        # 字号选择
        self.font_size_combo = QComboBox()
        self.font_size_combo.setEditable(True)
        self.font_size_combo.addItems([
            "8", "9", "10", "11", "12", "14", "16", "18",
            "20", "22", "24", "26", "28", "36", "48", "72"
        ])
        self.font_size_combo.setCurrentText("20")
        self.font_size_combo.setFixedWidth(70)
        self.font_size_combo.currentTextChanged.connect(self.set_text_size)
        self.format_toolbar.addWidget(self.font_size_combo)

        # 添加分割线
        self.format_toolbar.addSeparator()

        # 格式按钮
        self.bold_action = QAction(QIcon.fromTheme("format-text-bold"), "加粗", self)
        self.bold_action.setCheckable(True)
        self.bold_action.setShortcut("Ctrl+B")
        self.bold_action.triggered.connect(self.set_text_bold)
        self.format_toolbar.addAction(self.bold_action)

        self.italic_action = QAction(QIcon.fromTheme("format-text-italic"), "斜体", self)
        self.italic_action.setCheckable(True)
        self.italic_action.setShortcut("Ctrl+I")
        self.italic_action.triggered.connect(self.set_text_italic)
        self.format_toolbar.addAction(self.italic_action)

        self.underline_action = QAction(QIcon.fromTheme("format-text-underline"), "下划线", self)
        self.underline_action.setCheckable(True)
        self.underline_action.setShortcut("Ctrl+U")
        self.underline_action.triggered.connect(self.set_text_underline)
        self.format_toolbar.addAction(self.underline_action)

        self.color_action = QAction(QIcon.fromTheme("format-text-color"), "颜色", self)
        self.color_action.setShortcut("Ctrl+O")
        self.color_action.triggered.connect(self.set_text_color)
        self.format_toolbar.addAction(self.color_action)

        self.code_action = QAction(QIcon.fromTheme("code-context"), "插入代码", self)
        self.code_action.setShortcut("Ctrl+P")
        self.code_action.triggered.connect(self.insert_code_block_with_line_numbers)
        self.format_toolbar.addAction(self.code_action)

        # 添加分割线
        self.format_toolbar.addSeparator()

        # 添加清除格式按钮
        self.clear_format_action = QAction("清除格式", self)
        self.clear_format_action.triggered.connect(lambda: self.clear_text_format(True))
        self.format_toolbar.addAction(self.clear_format_action)

        right_layout.addWidget(self.format_toolbar)

        # 内容编辑区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("background: transparent;")

        self.content_edit = RichTextEdit()
        self.content_edit.setPlaceholderText("输入笔记内容...")
        self.content_edit.setStyleSheet(f"""
                    QTextEdit {{
                        border: 2px solid {STYLE['border_color']};
                        border-radius: 4px;
                        padding: 15px;
                        line-height: 1.6;
                        background-color: white;
                    }}
                    QTextEdit:focus {{
                        border-color: {STYLE['focus_color']};
                    }}
                """)
        scroll_area.setWidget(self.content_edit)
        right_layout.addWidget(scroll_area, 1)

        # 底部按钮区域
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setAlignment(Qt.AlignRight)

        btn_save = QPushButton("保存笔记")
        btn_save.setFixedSize(120, 40)
        btn_save.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {STYLE['primary_color']};
                        color: white;
                        border: none;
                        border-radius: 4px;
                        font-size: 14px;
                        padding: 8px 16px;
                    }}
                    QPushButton:hover {{
                        background-color: {STYLE['hover_color']};
                    }}
                """)
        btn_save.clicked.connect(self.save_note)
        # 添加快捷键 Ctrl+S 用于保存
        save_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_note)
        button_layout.addWidget(btn_save)

        right_layout.addWidget(button_container)

        # 主布局
        main_splitter.addWidget(left_panel)
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([300, 900])
        self.setCentralWidget(main_splitter)

        # 状态栏
        status_font = QFont()
        status_font.setPointSize(10)
        self.statusBar().setFont(status_font)
        self.statusBar().showMessage("就绪")

    def set_text_bold(self):
        """设置粗体字体"""
        cursor = self.content_edit.textCursor()
        is_bold = cursor.charFormat().font().bold()

        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Normal if is_bold else QFont.Bold)

        self.apply_format_to_selection_or_input(fmt)
        self.bold_action.setChecked(not is_bold)

    def set_text_italic(self):
        """设置斜体字体"""
        cursor = self.content_edit.textCursor()
        is_italic = cursor.charFormat().fontItalic()

        fmt = QTextCharFormat()
        fmt.setFontItalic(not is_italic)

        self.apply_format_to_selection_or_input(fmt)
        self.italic_action.setChecked(not is_italic)

    def set_text_underline(self):
        """设置下划线"""
        cursor = self.content_edit.textCursor()
        is_underline = cursor.charFormat().fontUnderline()

        fmt = QTextCharFormat()
        fmt.setFontUnderline(not is_underline)

        self.apply_format_to_selection_or_input(fmt)
        self.underline_action.setChecked(not is_underline)

    def set_text_color(self):
        """字体颜色"""
        color = QColorDialog.getColor()
        if color.isValid():
            fmt = QTextCharFormat()
            fmt.setForeground(color)
            self.apply_format_to_selection_or_input(fmt)

    def set_text_font(self, font):
        """设置字体样式（保留当前字号）"""
        cursor = self.content_edit.textCursor()
        current_size = cursor.charFormat().fontPointSize()
        if current_size <= 0:
            current_size = 20  # 默认字号

        fmt = QTextCharFormat()
        fmt.setFont(font)
        fmt.setFontPointSize(current_size)  # 保留字号
        self.apply_format_to_selection_or_input(fmt)

    def set_text_size(self, size_str):
        """设置字号"""
        try:
            size = float(size_str)
            size = max(6, min(144, size))  # 限制在6-144px之间
        except ValueError:
            return
        fmt = QTextCharFormat()
        fmt.setFontPointSize(size)
        self.apply_format_to_selection_or_input(fmt)

    def apply_format_to_selection_or_input(self, fmt: QTextCharFormat):
        """统一格式方法"""
        cursor = self.content_edit.textCursor()
        if cursor.hasSelection():
            cursor.mergeCharFormat(fmt)
        else:
            self.content_edit.mergeCurrentCharFormat(fmt)

    def sync_format_button_state(self):
        """同步工具栏按钮状态"""
        fmt = self.content_edit.currentCharFormat()
        self.bold_action.setChecked(fmt.font().bold())
        self.italic_action.setChecked(fmt.fontItalic())
        self.underline_action.setChecked(fmt.fontUnderline())

        # 同步字体、字号下拉框选中项
        self.font_combo.setCurrentFont(fmt.font())
        self.font_size_combo.setCurrentText(str(int(fmt.fontPointSize())) if fmt.fontPointSize() > 0 else "20")

    def clear_text_format(self, clear_all=False):
        """清除格式
        :param clear_all: 是否清除所有格式(包括段落格式)
        """
        cursor = self.content_edit.textCursor()
        if not cursor.hasSelection():
            return

        fmt = QTextCharFormat()
        fmt.setFontWeight(QFont.Normal)
        fmt.setFontItalic(False)
        fmt.setFontUnderline(False)
        fmt.setFontPointSize(20)
        fmt.setFont(QFont("微软雅黑"))  # 设置默认字体
        fmt.setForeground(QColor("black"))

        if clear_all:
            block_fmt = QTextBlockFormat()
            block_fmt.setAlignment(Qt.AlignLeft)
            cursor.mergeBlockFormat(block_fmt)

        cursor.mergeCharFormat(fmt)

    def insert_code_block_with_line_numbers(self):
        """简单插入带行号的代码块"""
        from PyQt5.QtWidgets import QInputDialog
        from PyQt5.QtGui import QTextCursor

        # 获取代码输入
        text, ok = QInputDialog.getMultiLineText(
            self, "插入代码", "请输入代码:", ""
        )
        if not ok or not text.strip():
            return

        lines = text.strip().split('\n')
        line_number_width = len(str(len(lines))) * 2  # 动态计算行号宽度

        # 生成带行号的HTML
        html_lines = []
        for i, line in enumerate(lines, 1):
            # 转义HTML特殊字符
            escaped_line = (line.replace("&", "&amp;")
                            .replace("<", "&lt;")
                            .replace(">", "&gt;")
                            .replace('"', "&quot;"))

            html_lines.append(
                f'<tr>'
                f'<td style="color: #316dfb; text-align: right; padding-right: 8px; width: 5ch; font-family: monospace; white-space: nowrap;">{i}</td>'
                f'<td style="font-family: monospace; white-space: pre-wrap; max-width: 80ch; overflow-x: auto;background-color: #f0f0f0;">{escaped_line}</td>'
                f'</tr>'
            )

        # 简单的HTML结构
        html = f"""
        <div style="background-color: #f6f7fb; border: 2px solid #cacaca; font-family: monospace; font-size: 13px;">
            <table style="border-collapse: collapse; width: 100%; table-layout: fixed;">
                {"".join(html_lines)}
            </table>
        </div>
        """

        # 确保self是QTextEdit对象
        if hasattr(self, 'textCursor'):
            # 插入到编辑器
            cursor = self.textCursor()
            cursor.insertHtml(html)
            # 移动光标到插入内容之后
            self.setTextCursor(cursor)
        else:
            # 如果是其他组件调用，需要获取编辑器引用
            editor = self.findChild(QTextEdit)
            if editor:
                cursor = editor.textCursor()
                cursor.insertHtml(html)
                editor.setTextCursor(cursor)

    def add_category(self):
        """增加分类"""
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
        """新增笔记"""
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

    def load_categories(self):
        """加载分类和笔记"""
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

    def on_tree_item_clicked(self, item):
        """处理列表点击事件"""
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
                self.title_edit.setText(note['title'])
                self.content_edit.setHtml(note['content'])
                self.statusBar().showMessage(f"正在编辑: {note['title']}", 3000)

    def select_note_by_id(self, note_id):
        def search_items(parent):
            for i in range(parent.childCount()):
                item = parent.child(i)
                data = item.data(0, Qt.UserRole)
                if data and data[0] == 'note' and data[1] == note_id:
                    self.tree_widget.setCurrentItem(item)
                    self.on_tree_item_clicked(item)
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
        """保存笔记，支持新建和更新，保留HTML格式"""
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
                self.load_categories()
                self.select_note_by_id(self.current_note_id)

            self.statusBar().showMessage(message, 3000)

        except Exception as e:
            error_msg = f"保存笔记失败: {str(e)}"
            print(f"[save_note] {error_msg}")
            QMessageBox.critical(self, "错误", error_msg)
