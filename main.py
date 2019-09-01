import sys
from PyQt5.QtWidgets import QApplication
from start import MainWindow
from learn import LearningWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    print("APP start")
    start_window = MainWindow()
    start_window.show()
    print("main window start")
    sys.exit(app.exec_())
