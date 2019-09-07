import sys
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from learn import LearningWindow
import os
import json
import time


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(800, 600)
        self.setWindowTitle('Pronunciation Practice')
        self.windowLayout()
        self.show()

    def writeJson(self, str):
        fp = open("data/today.json", "w")
        fp.write(str)
        fp.close()

    def checkToday(self):
        # 检查 today.json 文件是否存在，不存在新建
        print("check today.json")
        if not os.path.exists("data/today.json"):
            self.writeJson('{"time" : "-1", "words": "", "repeat": ""}')
        org = open("data/today.json", "r").read()
        # print(org)
        data = json.loads(org)
        today = time.strftime("%d", time.localtime())
        if data["time"] == today and len(data["words"]) < 2:
            print("today has been finished")
            return 1
        return 0

    def startLearning(self):
        print("start learning")
        if not self.checkToday():
            self.learn = LearningWindow(self.endLearng)
            self.learn.show()
            self.learn.setAttribute(Qt.WA_DeleteOnClose)
            self.hide()
        else:
            QMessageBox.about(
                self, "Oops!", "Why not have a rest?\nToday's words have been finished yet.")

    def endLearng(self, status):
        if status == 1:
            QMessageBox.about(
                self, "Oops!", "Congrandualtion!\nToday's words have been finished yet!")
        print("end learning")
        self.show()

    def windowClose(self):
        self.close()

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
        btbox.addSpacing(20)
        btbox.addWidget(btn_start)
        btbox.addSpacing(20)
        btbox.addWidget(btn_history)
        btbox.addSpacing(20)
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
