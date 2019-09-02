__author__ = "Ken"
__version__ = "1.0"

import sys
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QMainWindow, QAction, QWidget, QHBoxLayout, QLabel, QMessageBox, QFileDialog
from PyQt5.QtGui import QIcon, QPixmap

APP_WIDTH = 888
APP_HEIGHT = APP_WIDTH * .618


class RMAction(QAction):

    def __init__(self, name, icon, statusTip, act, master):

        super().__init__(
            QIcon(icon),
            name,
            master
        )
        self.setStatusTip(statusTip)
        self.triggered.connect(act)


class RMApp(QMainWindow):

    def __init__(self):

        super().__init__()
        self.init()

    def init(self):

        self.setWindowIcon(QIcon("./source/logo.png"))
        self.setWindowTitle("RouteMapTool v%s" % __version__)

        self.setFixedSize(APP_WIDTH, APP_HEIGHT)

        self.center()

        self.drawMenuBar()

        self.drawLayout()

        self.statusBar()

        self.show()

    def center(self):

        screenGeometry = QDesktopWidget().availableGeometry()
        self.move(
            (screenGeometry.width() - APP_WIDTH) / 2,
            (screenGeometry.height() - APP_HEIGHT) / 2
        )

    def drawMenuBar(self):

        menuBar = self.menuBar()

        fileMenu = menuBar.addMenu("文件")

        insertAction = RMAction(
            "插入背景",
            "./source/insert.png",
            "选择背景文件用作参考",
            self.insert,
            self
        )
        fileMenu.addAction(insertAction)

        quitAction = RMAction(
            "退出",
            "./source/quit.png",
            "关闭此应用",
            # MainWindow 的内置 close 函数，已被重载
            self.close,
            self
        )
        fileMenu.addAction(quitAction)

    def drawLayout(self):

        self.backgroundLabel = QLabel(self)

        # 给 MainWindow 设置 centralWidget
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)

        # 给 centralWidget 设置 layout
        layout = QHBoxLayout(centralWidget)
        layout.addWidget(self.backgroundLabel)
        centralWidget.setLayout(layout)

    def insert(self):

        background = QFileDialog.getOpenFileName(
            self,
            "选择背景图片",
            "./",
            "All files (*);;Image Files (*.png *.jpg)",
            "Image Files (*.png *.jpg)"
        )

        if background[0]:

            self.backgroundLabel.setPixmap(QPixmap(background[0]))

    def closeEvent(self, event):

        # 重载关闭函数

        reply = QMessageBox.question(
            self,
            "提示",
            "关闭前请确保已保存更改。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:

            event.accept()

        elif reply == QMessageBox.No:

            event.ignore()


App = QApplication(sys.argv)
rmApp = RMApp()
sys.exit(App.exec_())
