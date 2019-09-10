__author__ = "Ken"
__version__ = "1.0"

import sys
from PyQt5.QtWidgets import QApplication, QDesktopWidget, QMainWindow, QAction, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsPixmapItem, QMessageBox, QFileDialog, QMenu
from PyQt5.QtGui import QIcon, QPixmap, QBrush
from PyQt5.QtCore import Qt

APP_WIDTH = 888
APP_HEIGHT = APP_WIDTH * .618
STATION_WIDTH = 168
STATION_HEIGHT = STATION_WIDTH * .618
ICON_WIDTH = 36
ICON_HEIGHT = 36


class RMQAction(QAction):

    def __init__(self, name, icon, statusTip, act, parent):

        super().__init__(
            QIcon(icon),
            name,
            parent
        )

        self.setStatusTip(statusTip)
        self.triggered.connect(act)


class RMStationQGraphicsItem(QGraphicsRectItem):

    def __init__(self, x, y, width=STATION_WIDTH, height=STATION_HEIGHT):

        super().__init__(x - width / 2, y - height / 2, width, height)

        # 背景黑色
        self.setBrush(QBrush(Qt.black))

        # station icon
        QGraphicsPixmapItem(
            QPixmap("./source/station.png").scaled(ICON_WIDTH, ICON_HEIGHT),
            self
        ).setPos(x - width / 2 + 8, y - ICON_HEIGHT / 2)


class RMQGraphicsScene(QGraphicsScene):

    def __init__(self, parent):

        super().__init__(parent)

        self.backgroundItem = None
        self.focusPosition = None
        self.drawContextMenu(parent)

    def changeBackground(self, newBackground):

        # 如果已设置背景 item，先移除
        if self.backgroundItem:

            self.removeItem(self.backgroundItem)

        # 设置新的背景并把 backgroundItem 指向它
        self.backgroundItem = self.addPixmap(QPixmap(newBackground))

        # resize
        self.setSceneRect(self.backgroundItem.boundingRect())

        # 默认首先展示此 scene 的 view 是主视图
        self.views()[0].resetScale()

    def drawContextMenu(self, parent):

        self.contextMenu = QMenu(parent)

        createStationAction = RMQAction(
            "新增站台",
            "./source/station.png",
            "新增站台（矩形）",
            self.createStation,
            parent
        )
        self.contextMenu.addAction(createStationAction)

        createCAPAction = RMQAction(
            "新增 CAP",
            "./source/cap.png",
            "新增 CAP（点）",
            self.createCAP,
            parent
        )
        self.contextMenu.addAction(createCAPAction)

        createRailAction = RMQAction(
            "新增轨道",
            "./source/rail.png",
            "新增轨道（线）",
            self.createRail,
            parent
        )
        self.contextMenu.addAction(createRailAction)

    def createStation(self):

        self.addItem(
            RMStationQGraphicsItem(
                self.focusPosition.x(),
                self.focusPosition.y()
            )
        )

    def createCAP(self):

        # TODO
        print("createCAP")

    def createRail(self):

        # TODO
        print("createRail")

    def contextMenuEvent(self, event):

        self.focusPosition = event.scenePos()
        self.contextMenu.popup(event.screenPos())


class RMQGraphicsView(QGraphicsView):

    def __init__(self, scene, parent):

        super().__init__(scene, parent)

        self.lastestScale = 1
        self.scaleFromOrigin = 1

        SBOff = Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        self.setVerticalScrollBarPolicy(SBOff)
        self.setHorizontalScrollBarPolicy(SBOff)

        # 取消默认的黑框
        self.setStyleSheet("border: 0")

        # 设置 dragMode 为拖动
        self.setDragMode(QGraphicsView.ScrollHandDrag)

        # 设置 cursor
        self.viewport().setCursor(Qt.CrossCursor)

    def resetScale(self):

        self.resetTransform()
        self.scaleFromOrigin = 1
        self.lastestScale = 1

    def wheelEvent(self, event):

        # 重载鼠标滚轮函数

        # 滚轮向上
        if event.angleDelta().y() > 0:

            # 简单的平滑放大算法
            self.lastestScale = (self.lastestScale + .088) / self.lastestScale

        # 滚轮向下
        else:

            # 简单的平滑缩小算法
            self.lastestScale = (self.lastestScale - .088) / self.lastestScale

        # 计算相对于原尺寸，当前的缩放比例
        self.scaleFromOrigin *= self.lastestScale

        # 若企图缩小至比原尺寸还小，reset
        if self.scaleFromOrigin < 1:

            self.resetScale()

        # 其它情况，正常执行
        else:

            self.scale(self.lastestScale, self.lastestScale)

    def mouseReleaseEvent(self, event):

        # 重载鼠标释放函数

        # 调用超类的处理，防止不可追踪的 BUG
        super().mouseReleaseEvent(event)

        # 左键
        if event.button() == 1:

            # 拖拽完成后恢复 crossCursor
            self.viewport().setCursor(Qt.CrossCursor)


class RMApp(QMainWindow):

    def __init__(self):

        super().__init__()

        # 绘图 scene
        self.graphicsScene = RMQGraphicsScene(self)

        # 绘图 view
        self.graphicsView = RMQGraphicsView(self.graphicsScene, self)

        # 标题栏
        self.setWindowIcon(QIcon("./source/logo.png"))
        self.setWindowTitle("RouteMapTool v%s" % __version__)

        # 窗体固定尺寸与居中
        self.setMinimumSize(APP_WIDTH, APP_HEIGHT)
        self.center()

        # 菜单栏
        self.drawMenuBar()

        # 给 RMApp 实例（QMainWindow） 设置 centralWidget 为 QGraphicsView 实例（QWidget）
        self.setCentralWidget(self.graphicsView)

        # 状态栏
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

        insertAction = RMQAction(
            "插入背景",
            "./source/insert.png",
            "选择背景文件用作参考",
            self.insert,
            self
        )
        fileMenu.addAction(insertAction)

        quitAction = RMQAction(
            "退出",
            "./source/quit.png",
            "关闭此应用",
            # MainWindow 的内置 close 事件，事件 slot 已被重载
            self.close,
            self
        )
        fileMenu.addAction(quitAction)

    # init end

    def insert(self):

        backgrounds = QFileDialog.getOpenFileName(
            self,
            "选择背景图片",
            "./",
            "All files (*);;Image Files (*.png *.jpg)",
            "Image Files (*.png *.jpg)"
        )

        if backgrounds[0]:

            self.graphicsScene.changeBackground(backgrounds[0])

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
