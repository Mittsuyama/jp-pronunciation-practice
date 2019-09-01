import sys
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from learn import LearningWindow


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(600, 400)
        self.setWindowTitle('Pronunciation Practice')
        self.windowLayout()
        self.show()

    def startLearning(self):
        print("start learning")
        self.learn = LearningWindow(self.endLearng)
        self.learn.show()
        self.hide()

    def endLearng(self):
        print("end learning")
        self.show()

    def windowLayout(self):
        wel = QLabel("WELCOME TO")
        wel.setAlignment(Qt.AlignCenter)
        wel.setStyleSheet("font-size: 20px;")
        title = QLabel("Japanese Pronunciation Practice")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 30px;")

        btbox = QHBoxLayout()
        btn_start = QPushButton("START")
        btn_history = QPushButton("HISTORY")
        btbox.addSpacing(30)
        btbox.addWidget(btn_start)
        btbox.addSpacing(30)
        btbox.addWidget(btn_history)
        btbox.addSpacing(30)
        btn_start.clicked.connect(self.startLearning)

        vbox = QVBoxLayout()
        vbox.addStretch()
        vbox.addWidget(wel)
        vbox.addWidget(title)
        vbox.addSpacing(30)
        vbox.addLayout(btbox)
        vbox.addStretch()

        hbox = QHBoxLayout()
        hbox.addStretch()
        hbox.addLayout(vbox)
        hbox.addLayout(btbox)
        hbox.addStretch()

        self.setLayout(hbox)
