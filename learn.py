import sys
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout, QPushButton, QMessageBox, QWidget, QInputDialog
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from pykakasi import kakasi
import time
import pandas as pd
import os
import json
import functools
import math


class WeightWord:
    def __init__(self, o, w, t):
        self.o = o
        self.w = w
        self.t = t


class LearningWindow(QWidget):
    now_idx = 0

    def __init__(self, callback):
        super(LearningWindow, self).__init__()
        self.callback = callback
        self.resize(800, 600)
        self.setWindowTitle('Pronunciation Practice')
        self.windowLayout()

        self.checkUpdate()
        self.checkToday()
        self.getJsonData()
        self.getStart()

    def getExpValue(self, x, den):
        return math.exp(-(x - 1) / den)

    def addKanji(self, id):
        kanji = self.pd.loc[id]["word"]
        self.kanji.setText(kanji)
        if type(self.pd.loc[id]["note"]) != type("") or self.pd.loc[id]["note"] == "nan":
            self.note.setText("NOTE:\n" + "")
        else:
            self.note.setText(
                "NOTE:\n" + self.pd.loc[id]["note"].replace("[enter]", "\n"))

    def setTabValue(self, idx, attr, value):
        self.pd.loc[idx, attr] = value

    def endLearning(self):
        for key in self.repeat.keys():
            # 根据重复增加权重
            # sum = 0.0
            # add = 0
            # for x in range(1, int(self.repeat[key]) + 1):
            #     sum += self.getExpValue(x, 5)
            #     if sum >= 1:
            #         add += 1
            #         sum = 0.0
            # self.pd.loc[int(key), "weight"] = min(
            #     100, int(self.pd.loc[int(key)]["weight"]) + add)

            # 根据时间增加权重并改变 day 值
            v = float(self.pd.loc[int(key)]["accum"])
            day = int(self.pd.loc[int(key)]["day"])
            if day == -1:
                day = 1
            else:
                day += 1
            v += self.getExpValue(day, 20)
            if v >= 1:
                v = 0.0
                self.pd.loc[int(key), "weight"] = min(
                    100, int(self.pd.loc[int(key)]["weight"]) + 5)
            self.pd.loc[int(key), "day"] = day
            self.pd.loc[int(key), "accum"] = v

    def getNewWord(self):
        idx = self.queue[0]
        self.queue.remove(idx)

        if len(self.queue) < 1:
            self.backToMain(1)
            self.endLearning()
            self.saveToFile()
            return

        idx = int(self.queue[0])
        self.now_idx = idx
        self.hira.setText(self.pd.loc[idx]["pro"])
        self.kanji.setText("")
        self.left.setText("number of the rest words: " + str(len(self.queue)))
        self.note.setText("NOTE:\n")
        # print(self.queue)

    def saveToFile(self):
        # 保存 pro.csv 和 today.json 文件
        self.pd.to_csv("data/pro.csv", index=False)
        data = {"time": time.strftime(
            "%d", time.localtime()), "words": self.getStrFromList(self.queue), "repeat": self.repeat}
        self.writeJson(json.dumps(data))

    def recognized(self):
        idx = int(self.queue[0])
        if self.kanji.text() == "":
            self.addKanji(idx)
        else:
            # print(self.repeat[str(idx)])
            if self.repeat[str(idx)] == 0:
                self.setTabValue(idx, "weight", max(
                    0, int(self.pd.loc[idx]["weight"]) - 5))
            # print(" ----------- change ----------- ")
            # print(self.pd.loc[idx])
            self.saveToFile()
            self.getNewWord()

    def disRecognized(self):
        if len(self.queue) == 0:
            self.backToMain(2)
            return
        idx = int(self.queue[0])
        if self.kanji.text() == "":
            self.addKanji(idx)
        else:
            self.repeat[str(idx)] = str(int(self.repeat[str(idx)]) + 1)
            self.queue.insert(min(6, len(self.queue)), str(idx))
            self.queue.insert(min(12, len(self.queue)), str(idx))
            # print(" ----------- change ----------- ")
            # print("repeat = " + self.repeat[str(idx)])
            self.saveToFile()
            self.getNewWord()

    def getStart(self):
        self.pd = pd.read_csv("data/pro.csv", header=0, encoding="utf-8")
        self.hira.setText(self.pd.loc[int(self.queue[0])]["pro"])
        self.now_idx = int(self.queue[0])
        self.kanji.setText("")
        self.left.setText("number of the rest words: " + str(len(self.queue)))

    def getJsonData(self):
        org = open("data/today.json", "r").read()
        data = json.loads(org)
        self.queue = data["words"].split(",")
        self.repeat = data["repeat"]
        # print(self.queue)

    def writeJson(self, str):
        fp = open("data/today.json", "w")
        fp.write(str)
        fp.close()

    def checkToday(self):
        # 检查 today.json 文件是否存在，不存在新建
        if not os.path.exists("data/today.json"):
            self.writeJson('{"time" : "-1", "words": "", "repeat", ""}')
        org = open("data/today.json", "r").read()
        data = json.loads(org)
        today = time.strftime("%d", time.localtime())
        if today != data["time"]:
            print("updating today's words...")
            self.getTodayWords()

    def getStrFromList(self, my_list):
        str = ""
        for i in range(0, len(my_list)):
            if not i == 0:
                str += ","
            str += my_list[i]
        return str

    def myCmp(self, x, y):
        if x.w > y.w:
            return -1
        elif x.w == y.w and x.o < y.o:
            return -1
        return 1

    def getTodayWords(self):
        c = pd.read_csv("data/pro.csv", header=0, encoding='utf-8')
        words = []
        for idx in range(0, len(c)):
            words.append(WeightWord(
                idx, c.loc[idx]["weight"], int(c.loc[idx]["day"])))
        words = sorted(words, key=functools.cmp_to_key(
            lambda a, b: self.myCmp(a, b)))
        new_count = 0
        old_count = 0
        res = []
        for word in words:
            if word.t == -1 and new_count < 200:
                res.append(word.o)
                new_count += 1
            elif word.t != -1 and old_count < 400:
                res.append(word.o)
                old_count += 1
        words_str = ""
        repeat_json = {}
        for i in range(0, len(res)):
            if not i == 0:
                words_str += ","
            words_str += str(res[i])
            repeat_json[str(res[i])] = 0
        data = {"time": time.strftime(
            "%d", time.localtime()), "words": words_str, "repeat": repeat_json}
        self.writeJson(json.dumps(data))

    def checkUpdate(self):
        print("—————————————— check update ——————————————")
        words = self.getOriginWordsList()

        # 检查 csv 文件是否存在，不存在则创建
        if not os.path.exists("data/pro.csv"):
            fp = open("data/pro.csv", "w")
            fp.write("word,pro,weight,day,accum,note\n")
            fp.close()

        csv = pd.read_csv("data/pro.csv", header=0, encoding='utf-8')
        if len(csv) < len(words):
            print("update...")
            kakasi = self.setKakasi()
            for idx in range(len(csv), len(words)):
                csv.loc[len(csv)] = {"word": words[idx], "pro": kakasi.do(words[idx]),
                                     "weight": 50, "day": -1, "accum": 0.0, "note": "nan"}
            csv.to_csv("data/pro.csv", index=False)
            print("pro update finish.")
        else:
            print("has been updated")

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

    def backToMain(self, status):
        self.saveToFile()
        self.callback(status)
        self.close()

    def addNotes(self, event):
        # print(self.now_idx)
        temp = self.pd.loc[self.now_idx]["note"]
        now_note = ""
        if type(temp) != type(""):
            now_note = ""
        else:
            now_note = temp
        value, ok = QInputDialog.getMultiLineText(
            self, "Add notes", "Input your notes", now_note.replace("[enter]", "\n"))
        if ok:
            self.note.setText("NOTE:\n" + value)
            value = value.replace("\n\r", "[enter]").replace(
                "\n", "[enter]").replace("\r", "[enter]")
            self.pd.loc[self.now_idx, "note"] = value

    def windowLayout(self):
        self.hira = QLabel("さくら")
        self.hira.setAlignment(Qt.AlignCenter)
        self.hira.setStyleSheet("font-family: sans-serif; font-size: 40px;")
        self.kanji = QLabel("桜")
        self.kanji.setAlignment(Qt.AlignCenter)
        self.kanji.setStyleSheet(
            "font-family: sans-serif; font-size: 25px; color: #555;")
        self.left = QLabel("xxx")
        self.left.setAlignment(Qt.AlignCenter)
        self.left.setStyleSheet(
            "font-family: sans-serif; font-size: 15px; color: #777;")
        # self.input_info = QLabel("Notes:")
        self.note = QLabel("Note:\n")
        self.note.setStyleSheet(
            "font-family: sans-serif; font-size: 14px; color: #555; line-height: 24px;")

        ybtn = QPushButton("Yeap", self)
        nbtn = QPushButton("Oops", self)
        qbtn = QPushButton("Quit", self)
        qbtn.clicked.connect(self.backToMain, 0)
        ybtn.clicked.connect(self.recognized)
        nbtn.clicked.connect(self.disRecognized)
        ybtn.setStyleSheet("width: 100px;")
        nbtn.setStyleSheet("width: 100px;")
        qbtn.setStyleSheet("width: 80px;")
        add_note = QPushButton("Add Notes", self)
        add_note.setStyleSheet("width: 80px;")
        add_note.clicked.connect(self.addNotes)

        hbox = QHBoxLayout()
        hbox.addStretch()
        hbox.addWidget(ybtn)
        hbox.addWidget(nbtn)
        hbox.addStretch()

        h_input = QHBoxLayout()
        h_input.addSpacing(165)
        h_input.addWidget(self.note)
        h_input.addSpacing(150)

        add_box = QHBoxLayout()
        add_box.addSpacing(162)
        add_box.addWidget(add_note)
        add_box.addSpacing(20)
        add_box.addWidget(qbtn)
        add_box.addStretch()

        vbox = QVBoxLayout()
        vbox.addStretch()
        vbox.addWidget(self.hira)
        vbox.addWidget(self.kanji)
        vbox.addSpacing(30)
        vbox.addLayout(hbox)
        vbox.addWidget(self.left)
        # vbox.addWidget(self.input_info)
        vbox.addSpacing(30)
        vbox.addLayout(h_input)
        vbox.addLayout(add_box)
        vbox.addStretch()

        self.setLayout(vbox)

        # QWidget.setTabOrder(nbtn, ybtn)
        QWidget.setTabOrder(ybtn, nbtn)
        qbtn.setFocusPolicy(Qt.NoFocus)
        add_note.setFocusPolicy(Qt.NoFocus)
        # self.input_box.setFocusPolicy(Qt.NoFocus)

        print("finish layout")
