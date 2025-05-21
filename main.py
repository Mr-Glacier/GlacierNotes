import sys
from PyQt5.QtWidgets import QApplication
from db.database import Database
from ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    db = Database()
    window = MainWindow(db)
    window.show()
    exit_code = app.exec_()
    db.close()
    sys.exit(exit_code)
