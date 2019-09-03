__author__ = "Ken"
__version__ = "1.0"

import sys
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QMainWindow, QAction, QGraphicsView, QGraphicsScene, QMessageBox, QFileDialog
from PyQt5.QtGui import QIcon, QPixmap

APP_WIDTH = 888
APP_HEIGHT = APP_WIDTH * .618
DEFAULT_BACKGROUND = "./source/Jordan.jpg"


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

        # 是否已插入背景
        self.inserted = False

        # 几何 scene
        self.graphicsScene = QGraphicsScene(self)

        # 背景 item（仅初始化操作，还不是真正的 item，item 需要 scene 的装载）
        self.backgroundItem = QPixmap(DEFAULT_BACKGROUND)

        self.setWindowIcon(QIcon("./source/logo.png"))
        self.setWindowTitle("RouteMapTool v%s" % __version__)

        self.setFixedSize(APP_WIDTH, APP_HEIGHT)

        self.center()

        self.drawMenuBar()

        self.drawGraphicsBase()

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

    def drawGraphicsBase(self):

        # 给 RMApp 实例（QMainWindow） 设置 centralWidget 为 QGraphicsView 实例（即视图），并展示一个 QGraphicsScene 实例（即场景）
        self.setCentralWidget(QGraphicsView(self.graphicsScene, self))

        # 这时的 backgroundItem 指向真正的 graphicsItem 实例
        self.backgroundItem = self.graphicsScene.addPixmap(self.backgroundItem)

    def insert(self):

        background = QFileDialog.getOpenFileName(
            self,
            "选择背景图片",
            "./",
            "All files (*);;Image Files (*.png *.jpg)",
            "Image Files (*.png *.jpg)"
        )

        if background[0]:

            # 移除当前背景 item
            self.graphicsScene.removeItem(self.backgroundItem)

            # 把 backgroundItem 重新指向新的背景 item 并添加到 graphicsScene
            self.backgroundItem = self.graphicsScene.addPixmap(
                QPixmap(background[0])
            )

            self.inserted = True

    def wheelEvent(self, event):

        # 重载鼠标滚轮函数

        if self.inserted:

            scaleDelta = event.angleDelta().y()

            if scaleDelta > 0:

                print("bigger")

            else:

                print("smaller")

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
