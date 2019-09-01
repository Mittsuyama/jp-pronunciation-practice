import sys
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from pykakasi import kakasi
import time
import pandas as pd
import os


class WeightWord:
    def __init__(self, o, w, t):
        self.o = o
        self.w = w
        self.t = t


class LearningWindow(QWidget):
    def __init__(self, callback):
        super(LearningWindow, self).__init__()
        self.callback = callback
        self.resize(600, 400)
        self.setWindowTitle('Pronunciation Practice')
        self.windowLayout()

        self.checkUpdate()

    def checkUpdate(self):
        print("—————————————— check update ——————————————")
        words = self.getOriginWordsList()
        if not os.path.exists("data/pro.csv"):
            fp = open("data/pro.csv", "w")
            fp.write("word,pro,weight,day,accum\n")
            fp.close()
        csv = pd.read_csv("data/pro.csv", header=0, encoding='utf-8')
        print(csv)
        if len(csv) < len(words):
            print("update...")
            kakasi = self.setKakasi()
            for idx in range(len(csv), len(words)):
                csv.loc[len(csv)] = {"word": words[idx], "pro": kakasi.do(words[idx]),
                                     "weight": 50, "day": -1, "accum": 0.0}
            csv.to_csv("data/pro.csv", index=False)
            print("pro update finish.")

    def setKakasi(self):
        k = kakasi()
        k.setMode("K", "H")
        k.setMode("J", "H")
        return k.getConverter()

    def dealEnter(self, str):
        return str.replace("\n", "").replace("\r", "")

    def getOriginWordsList(self):
        lines = open("data/words.txt").readlines()
        words = []
        for line in lines:
            words += self.dealEnter(line).split("、")
        return words

    def backToMain(self):
        self.callback()
        self.hide()

    def windowLayout(self):
        hira = QLabel("さくら")
        hira.setAlignment(Qt.AlignCenter)
        hira.setStyleSheet("font-size: 30px")
        kanji = QLabel("桜")
        kanji.setAlignment(Qt.AlignCenter)
        kanji.setStyleSheet("font-size: 30px")

        ybtn = QPushButton("yes(1)", self)
        nbtn = QPushButton("no(2)", self)
        qbtn = QPushButton("quit", self)
        qbtn.clicked.connect(self.backToMain)

        hbox = QHBoxLayout()
        hbox.addStretch()
        hbox.addWidget(ybtn)
        hbox.addWidget(nbtn)
        hbox.addWidget(qbtn)
        hbox.addStretch()

        vbox = QVBoxLayout()
        vbox.addStretch()
        vbox.addWidget(hira)
        vbox.addWidget(kanji)
        vbox.addLayout(hbox)
        vbox.addStretch()

        self.setLayout(vbox)
