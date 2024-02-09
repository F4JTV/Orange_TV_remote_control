#!/usr/bin/python3
# -*- coding: UTF-8 -*-
""" Orange TV Remote Control """
import sys
import configparser

from PyQt5.QtNetwork import QNetworkRequest, QNetworkReply, QNetworkAccessManager
from PyQt5.QtCore import QUrl, QFile, QIODevice, QTextStream, QSize, Qt
from PyQt5.QtGui import QPixmap, QCloseEvent, QIcon
from PyQt5.QtWidgets import (QApplication, QSplashScreen, QMessageBox, QMainWindow,
                             QWidget, QVBoxLayout, QPushButton, QGridLayout, QHBoxLayout)

VERSION = "v0.1"
APP_TITLE = f"Orange TV Remote Control {VERSION}"
BTN_CODE = {"ON/OFF": "116", "0": "512", "1": "513", "2": "514",
            "3": "515", "4": "516", "5": "517", "6": "518",
            "7": "519", "8": "520", "9": "521", "CH+": "402",
            "CH-": "403", "VOL+": "115", "VOL-": "114", "MUTE": "113",
            "UP": "103", "DOWN": "108", "LEFT": "105", "RIGHT": "106",
            "OK": "352", "BACK": "158", "MENU": "139", "PLAY/PAUSE": "164",
            "FBWD": "168", "FFWD": "159", "REC": "167", "VOD": "393"}
WIDTH = 350
HEIGHT = 1000
BTN_SIZE = QSize(70, 70)
DECODER_IP = "192.168.1.23"


class MainWindow(QMainWindow):
    """ Main Window """

    # noinspection PyUnresolvedReferences
    def __init__(self, d_ip):
        super().__init__(parent=None)

        # Main Window config
        self.setFixedSize(WIDTH, HEIGHT)
        self.setWindowFlags(Qt.WindowCloseButtonHint |
                            Qt.WindowMinimizeButtonHint)
        self.setWindowTitle(APP_TITLE)
        self.setWindowIcon(QIcon("./images/icon.png"))

        self.decoder_ip = d_ip
        self.net_acc_man = None

        # ### Main Layout
        self.central_widget = QWidget(self)

        self.main_layout = QVBoxLayout(self.central_widget)
        self.central_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.central_widget)

        self.power_btn = QPushButton("On/Off")
        self.main_layout.addWidget(self.power_btn, 1, Qt.AlignmentFlag.AlignCenter)

        self.arrow_layout = QGridLayout()
        self.up_arrow = QPushButton("Up")
        self.left_arrow = QPushButton("Left")
        self.right_arrow = QPushButton("Right")
        self.down_arrow = QPushButton("Down")
        self.ok_btn = QPushButton("Ok")
        self.arrow_layout.addWidget(self.up_arrow, 0, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)
        self.arrow_layout.addWidget(self.left_arrow, 1, 0, Qt.AlignmentFlag.AlignCenter)
        self.arrow_layout.addWidget(self.ok_btn, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.arrow_layout.addWidget(self.right_arrow, 1, 2, Qt.AlignmentFlag.AlignCenter)
        self.arrow_layout.addWidget(self.down_arrow, 2, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addLayout(self.arrow_layout, 1)

        self.back_menu_layout = QHBoxLayout()
        self.main_layout.addLayout(self.back_menu_layout, 1)
        self.back_btn = QPushButton("Back")
        self.menu_btn = QPushButton("Menu")
        self.back_menu_layout.addWidget(self.back_btn, 1, Qt.AlignmentFlag.AlignCenter)
        self.back_menu_layout.addWidget(self.menu_btn, 1, Qt.AlignmentFlag.AlignCenter)

        self.vol_channel_layout = QHBoxLayout()
        self.main_layout.addLayout(self.vol_channel_layout, 1)
        self.vol_layout = QVBoxLayout()
        self.channel_layout = QVBoxLayout()
        self.vol_channel_layout.addLayout(self.vol_layout, 1)
        self.vol_channel_layout.addLayout(self.channel_layout, 1)

        self.vol_up_btn = QPushButton("Vol +")
        self.vol_down_btn = QPushButton("Vol -")
        self.vol_layout.addWidget(self.vol_up_btn, 1, Qt.AlignmentFlag.AlignCenter)
        self.vol_layout.addWidget(self.vol_down_btn, 1, Qt.AlignmentFlag.AlignCenter)

        self.channel_up_btn = QPushButton("Ch +")
        self.channel_down_btn = QPushButton("Ch -")
        self.channel_layout.addWidget(self.channel_up_btn, 1, Qt.AlignmentFlag.AlignCenter)
        self.channel_layout.addWidget(self.channel_down_btn, 1, Qt.AlignmentFlag.AlignCenter)

        self.btn_layout = QGridLayout()
        self.main_layout.addLayout(self.btn_layout, 1)
        self.btn_1 = QPushButton("1")
        self.btn_2 = QPushButton("2")
        self.btn_3 = QPushButton("3")
        self.btn_4 = QPushButton("4")
        self.btn_5 = QPushButton("5")
        self.btn_6 = QPushButton("6")
        self.btn_7 = QPushButton("7")
        self.btn_8 = QPushButton("8")
        self.btn_9 = QPushButton("9")
        self.btn_0 = QPushButton("0")
        self.btn_layout.addWidget(self.btn_1, 0, 0, Qt.AlignmentFlag.AlignCenter)
        self.btn_layout.addWidget(self.btn_2, 0, 1, Qt.AlignmentFlag.AlignCenter)
        self.btn_layout.addWidget(self.btn_3, 0, 2, Qt.AlignmentFlag.AlignCenter)
        self.btn_layout.addWidget(self.btn_4, 1, 0, Qt.AlignmentFlag.AlignCenter)
        self.btn_layout.addWidget(self.btn_5, 1, 1, Qt.AlignmentFlag.AlignCenter)
        self.btn_layout.addWidget(self.btn_6, 1, 2, Qt.AlignmentFlag.AlignCenter)
        self.btn_layout.addWidget(self.btn_7, 2, 0, Qt.AlignmentFlag.AlignCenter)
        self.btn_layout.addWidget(self.btn_8, 2, 1, Qt.AlignmentFlag.AlignCenter)
        self.btn_layout.addWidget(self.btn_9, 2, 2, Qt.AlignmentFlag.AlignCenter)
        self.btn_layout.addWidget(self.btn_0, 3, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)

        self.ctl_btn_layout = QHBoxLayout()
        self.main_layout.addLayout(self.ctl_btn_layout, 1)
        self.fbwd_btn = QPushButton("<<")
        self.play_pause_btn = QPushButton(">||")
        self.ffwd_btn = QPushButton(">>")
        self.record_btn = QPushButton("Record")
        self.ctl_btn_layout.addWidget(self.fbwd_btn, 1, Qt.AlignmentFlag.AlignCenter)
        self.ctl_btn_layout.addWidget(self.play_pause_btn, 1, Qt.AlignmentFlag.AlignCenter)
        self.ctl_btn_layout.addWidget(self.ffwd_btn, 1, Qt.AlignmentFlag.AlignCenter)
        self.ctl_btn_layout.addWidget(self.record_btn, 1, Qt.AlignmentFlag.AlignCenter)

        for button in [self.power_btn, self.up_arrow, self.left_arrow,
                       self.right_arrow, self.down_arrow, self.back_btn,
                       self.menu_btn, self.vol_up_btn, self.vol_down_btn,
                       self.channel_up_btn, self.channel_down_btn,
                       self.btn_1, self.btn_2, self.btn_3, self.btn_4,
                       self.btn_5, self.btn_6, self.btn_7, self.btn_8,
                       self.btn_9, self.btn_0, self.ffwd_btn, self.fbwd_btn,
                       self.record_btn, self.play_pause_btn, self.ok_btn]:
            self.config_btn_style(button)

        self.power_btn.clicked.connect(lambda: self.do_request(BTN_CODE["ON/OFF"]))
        self.up_arrow.clicked.connect(lambda: self.do_request(BTN_CODE["UP"]))
        self.left_arrow.clicked.connect(lambda: self.do_request(BTN_CODE["LEFT"]))
        self.ok_btn.clicked.connect(lambda: self.do_request(BTN_CODE["OK"]))
        self.right_arrow.clicked.connect(lambda: self.do_request(BTN_CODE["RIGHT"]))
        self.down_arrow.clicked.connect(lambda: self.do_request(BTN_CODE["DOWN"]))
        self.back_btn.clicked.connect(lambda: self.do_request(BTN_CODE["BACK"]))
        self.menu_btn.clicked.connect(lambda: self.do_request(BTN_CODE["MENU"]))
        self.vol_up_btn.clicked.connect(lambda: self.do_request(BTN_CODE["VOL+"]))
        self.vol_down_btn.clicked.connect(lambda: self.do_request(BTN_CODE["VOL-"]))
        self.channel_up_btn.clicked.connect(lambda: self.do_request(BTN_CODE["CH+"]))
        self.channel_down_btn.clicked.connect(lambda: self.do_request(BTN_CODE["CH-"]))
        self.btn_1.clicked.connect(lambda: self.do_request(BTN_CODE["1"]))
        self.btn_2.clicked.connect(lambda: self.do_request(BTN_CODE["2"]))
        self.btn_3.clicked.connect(lambda: self.do_request(BTN_CODE["3"]))
        self.btn_4.clicked.connect(lambda: self.do_request(BTN_CODE["4"]))
        self.btn_5.clicked.connect(lambda: self.do_request(BTN_CODE["5"]))
        self.btn_6.clicked.connect(lambda: self.do_request(BTN_CODE["6"]))
        self.btn_7.clicked.connect(lambda: self.do_request(BTN_CODE["7"]))
        self.btn_8.clicked.connect(lambda: self.do_request(BTN_CODE["8"]))
        self.btn_9.clicked.connect(lambda: self.do_request(BTN_CODE["9"]))
        self.btn_0.clicked.connect(lambda: self.do_request(BTN_CODE["0"]))
        self.fbwd_btn.clicked.connect(lambda: self.do_request(BTN_CODE["FBWD"]))
        self.ffwd_btn.clicked.connect(lambda: self.do_request(BTN_CODE["FFWD"]))
        self.play_pause_btn.clicked.connect(lambda: self.do_request(BTN_CODE["PLAY/PAUSE"]))
        self.record_btn.clicked.connect(lambda: self.do_request(BTN_CODE["REC"]))

    @staticmethod
    def config_btn_style(btn):
        btn.setObjectName("orange")
        btn.setFixedSize(BTN_SIZE)

    def do_request(self, code):
        url = f"http://{self.decoder_ip}:8080/remoteControl/cmd?operation=01&key={code}&mode=0"
        request = QNetworkRequest(QUrl(url))
        self.net_acc_man = QNetworkAccessManager()
        # noinspection PyUnresolvedReferences
        self.net_acc_man.finished.connect(self.print_response)
        self.net_acc_man.get(request)

    @staticmethod
    def print_response(reply):
        er = reply.error()
        if er == QNetworkReply.NetworkError.NoError:
            bytes_string = reply.readAll()
            print(str(bytes_string, 'utf-8'))
        else:
            print("Error occured: ", er)
            print(reply.errorString())

    def closeEvent(self, event):
        """ Close event """
        dialog = QMessageBox()
        rep = dialog.question(self,
                              "Exit",
                              "Exit the app ?",
                              dialog.Yes | dialog.No)
        if rep == dialog.Yes:
            self.close()
        elif rep == dialog.No:
            QCloseEvent.ignore(event)
            return


if __name__ == "__main__":

    app = QApplication(sys.argv)

    # Config
    config = configparser.ConfigParser()
    config.read("./Orange_TV_RC.cfg")
    decoder_ip = config["DEFAULT"]["decoder_ip_adr"]
    style = config["DEFAULT"]["style"]

    qss_file = QFile()
    if style == "dark":
        qss_file = QFile("./qss/dark_style.qss")
    elif style == "orange":
        qss_file = QFile("./qss/orange_style.qss")
    elif style == "light":
        qss_file = QFile("./qss/light_style.qss")

    qss_file.open(QIODevice.OpenModeFlag.ReadOnly)
    app.setStyleSheet(QTextStream(qss_file).readAll())

    # Splash Screen
    splash = QSplashScreen(QPixmap("./images/splash.png"))
    splash.show()

    app.processEvents()
    window = MainWindow(decoder_ip)
    splash.finish(window)
    window.show()
    sys.exit(app.exec_())
