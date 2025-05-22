from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtCore import QUrl, Qt, QMimeData
from PyQt5.QtGui import QImage, QImageReader, QTextImageFormat, QFont, QColor, QTextCharFormat, QTextCursor
import os
import tempfile
import uuid


class RichTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_default_format()
        self.setAcceptDrops(True)

    def init_default_format(self):
        font = QFont("微软雅黑", 16)
        self.setFont(font)
        self.setTextColor(QColor("black"))

        cursor = self.textCursor()
        fmt = QTextCharFormat()
        fmt.setFont(font)
        fmt.setForeground(QColor("black"))
        cursor.select(QTextCursor.Document)
        cursor.mergeCharFormat(fmt)
        self.setTextCursor(cursor)


    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if url.toLocalFile().lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    event.acceptProposedAction()
                    return
        super().dragEnterEvent(event)

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.exists(file_path):
                self.insert_image(file_path)
        event.acceptProposedAction()

    def insertFromMimeData(self, source: QMimeData):
        if source.hasImage():
            image = source.imageData()
            if isinstance(image, QImage):
                image = image.scaled(800, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                temp_file_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4().hex}.jpg")
                image.save(temp_file_path, "JPEG", quality=80)

                image_format = QTextImageFormat()
                image_format.setName(temp_file_path)
                self.textCursor().insertImage(image_format)
            return
        super().insertFromMimeData(source)

    def insert_image(self, file_path: str):
        image = QImage(file_path)
        if image.isNull():
            return
        if image.sizeInBytes() > 3 * 1024 * 1024:
            image = image.scaled(800, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        temp_file_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4().hex}.jpg")
        image.save(temp_file_path, "JPEG", quality=80)

        image_format = QTextImageFormat()
        image_format.setName(temp_file_path)
        self.textCursor().insertImage(image_format)
