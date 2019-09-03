__author__ = "Ken"
__version__ = "1.0"

import sys
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QMainWindow, QAction, QGraphicsView, QGraphicsScene, QMessageBox, QFileDialog
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt

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


class RMQGraphicsView(QGraphicsView):

    def __init__(self, scene, parent):

        super().__init__(scene, parent)

        SBOff = Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        self.setVerticalScrollBarPolicy(SBOff)
        self.setHorizontalScrollBarPolicy(SBOff)

        # 取消默认的黑框
        self.setStyleSheet("border: 0")

    def wheelEvent(self, event):

        # 重载鼠标滚轮函数

        scaleDelta = event.angleDelta().y()

        if scaleDelta > 0:

            self.scale(1.0636, 1.0636)

        else:

            self.scale(0.9364, 0.9364)


class RMApp(QMainWindow):

    def __init__(self):

        super().__init__()

        self.init()

    def init(self):

        # 几何 scene
        self.graphicsScene = QGraphicsScene(self)

        # 几何 view
        self.graphicsView = RMQGraphicsView(self.graphicsScene, self)

        # 背景 item
        self.backgroundItem = None

        self.setWindowIcon(QIcon("./source/logo.png"))
        self.setWindowTitle("RouteMapTool v%s" % __version__)

        self.setFixedSize(APP_WIDTH, APP_HEIGHT)

        self.center()

        self.drawMenuBar()

        self.drawGraphicsBase()

        self.statusBar()

        self.show()

    # init start

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

        # 给 RMApp 实例（QMainWindow） 设置 centralWidget 为 QGraphicsView 实例（QWidget）
        self.setCentralWidget(self.graphicsView)

        self.backgroundItem = self.graphicsScene.addPixmap(
            QPixmap(DEFAULT_BACKGROUND)
        )

    # init end

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
