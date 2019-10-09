__author__ = "Ken"
__version__ = "1.0"

import sys
from utils import RM_path
from PyQt5.QtWidgets import\
    QApplication,\
    QDesktopWidget,\
    QMainWindow,\
    QMenu,\
    QAction,\
    QGraphicsView,\
    QGraphicsScene,\
    QGraphicsRectItem,\
    QGraphicsLineItem, \
    QGraphicsPixmapItem,\
    QGraphicsSimpleTextItem,\
    QMessageBox,\
    QFileDialog,\
    QInputDialog
from PyQt5.QtGui import QIcon, QPixmap, QBrush, QFont
from PyQt5.QtCore import Qt

APP_WIDTH = 888
APP_HEIGHT = APP_WIDTH * .618
STATION_WIDTH = 128
STATION_HEIGHT = STATION_WIDTH * .618
ICON_WIDTH = 24
ICON_HEIGHT = 24

black_brush = QBrush(Qt.black)
white_brush = QBrush(Qt.white)
title_font = QFont("Microsoft YaHei", 10)


class RMQAction(QAction):

    def __init__(self, name, icon, statusTip, act, parent):

        super().__init__(
            QIcon(RM_path(icon)),
            name,
            parent
        )

        self.setStatusTip(statusTip)
        self.triggered.connect(act)


class RMBackgroundQGraphicsItem(QGraphicsPixmapItem):

    def __init__(self, imagePath):

        super().__init__(QPixmap(RM_path(imagePath)))

    def contextMenuEvent(self, event):

        self.scene().focusPosition = event.scenePos()
        self.scene().backgroundContextMenu.popup(event.screenPos())


class RMStationQGraphicsItem(QGraphicsRectItem):

    def __init__(self, x, y, width=STATION_WIDTH, height=STATION_HEIGHT, name=""):

        # 此处的初始化 xy 值是以 item coordinate 标记矩形的起始点（左上角）
        super().__init__(-width / 2, -height / 2, width, height)

        # 此处的 xy 值是以 scene coordinate 标记矩形，结合上面的初始化，标记点是矩形的几何中心
        self.setPos(x, y)

        # 背景黑色
        self.setBrush(black_brush)

        # icon（相对于父 item 的 xy 值）
        QGraphicsPixmapItem(
            QPixmap(RM_path("./source/station.png"))
            .scaled(ICON_WIDTH, ICON_HEIGHT),
            self
        ).setPos(-width / 2 + 8, -ICON_HEIGHT / 2)

        # name（相对于父 item 的 xy 值）
        name = QGraphicsSimpleTextItem(name, self)
        name.setBrush(white_brush)
        name.setFont(title_font)
        name.setPos(
            -width / 2 + 8 + ICON_WIDTH,
            -name.boundingRect().height() / 2
        )

    def contextMenuEvent(self, event):

        self.scene().focusPosition = self.scenePos()
        self.scene().stationContextMenu.popup(event.screenPos())


class RMCAPQGraphicsItem(QGraphicsPixmapItem):

    def __init__(self, x, y):

        super().__init__(QPixmap(RM_path("./source/cap.png")).scaled(ICON_WIDTH, ICON_HEIGHT))

        # 配合偏移值，以几何中心为 scenePos
        self.setPos(x, y)
        self.setOffset(-ICON_WIDTH / 2, -ICON_HEIGHT / 2)

    def contextMenuEvent(self, event):

        self.scene().focusPosition = self.scenePos()
        self.scene().CAPContextMenu.popup(event.screenPos())


class RMRailQGraphicsItem(QGraphicsLineItem):

    def __init__(self, x1, y1, x2, y2):

        super().__init__(x1, y1, x2, y2)

    def contextMenuEvent(self, event):

        print("TODO")


class RMQGraphicsScene(QGraphicsScene):

    def __init__(self, parent):

        super().__init__(parent)

        self.backgroundItem = None
        self.focusPosition = None
        self.parent = parent
        self.drawBackgroundContextMenu(parent)
        self.drawStationContextMenu(parent)
        self.drawCAPContextMenu(parent)

    def changeBackground(self, newBackground):

        # 移除所有图元（业务设计如此）
        self.clear()

        # 把 backgroundItem 指向新的背景图元并设置
        self.backgroundItem = RMBackgroundQGraphicsItem(newBackground)
        self.addItem(self.backgroundItem)

        # resize
        self.setSceneRect(self.backgroundItem.boundingRect())

        # 默认首先展示此 scene 的 view 是主视图
        self.views()[0].resetScale()

    def drawBackgroundContextMenu(self, parent):

        self.backgroundContextMenu = QMenu(parent)

        createStationAction = RMQAction(
            "新增站台",
            "./source/station.png",
            "新增站台（矩形）",
            self.createStation,
            parent
        )
        createCAPAction = RMQAction(
            "新增 CAP",
            "./source/cap.png",
            "新增 CAP（点）",
            self.createCAP,
            parent
        )
        createRailAction = RMQAction(
            "新增轨道",
            "./source/rail.png",
            "新增轨道（线）",
            self.createRail,
            parent
        )

        self.backgroundContextMenu.addAction(createStationAction)
        self.backgroundContextMenu.addAction(createCAPAction)
        self.backgroundContextMenu.addAction(createRailAction)

    def drawStationContextMenu(self, parent):

        self.stationContextMenu = QMenu(parent)

        createStationUpwardsAction = RMQAction(
            "新增站台",
            "./source/station.png",
            "向上新增站台（矩形）",
            lambda: self.createStation(0, -STATION_HEIGHT),
            parent
        )
        createCAPUpwardsAction = RMQAction(
            "新增 CAP",
            "./source/cap.png",
            "向上新增 CAP（点）",
            lambda: self.createCAP(0, -(STATION_HEIGHT / 2 + ICON_HEIGHT / 2)),
            parent
        )
        createRailUpwardsAction = RMQAction(
            "新增轨道",
            "./source/rail.png",
            "向上新增轨道（线）",
            lambda: self.createRail(
                0,
                -(STATION_HEIGHT / 2 + ICON_HEIGHT / 2)
            ),
            parent
        )

        upwardsSubmenu = self.stationContextMenu.addMenu("向上")
        upwardsSubmenu.addAction(createStationUpwardsAction)
        upwardsSubmenu.addAction(createCAPUpwardsAction)
        upwardsSubmenu.addAction(createRailUpwardsAction)

        createStationDownwardsAction = RMQAction(
            "新增站台",
            "./source/station.png",
            "向下新增站台（矩形）",
            lambda: self.createStation(0, STATION_HEIGHT),
            parent
        )
        createCAPDownwardsAction = RMQAction(
            "新增 CAP",
            "./source/cap.png",
            "向下新增 CAP（点）",
            lambda: self.createCAP(0, STATION_HEIGHT / 2 + ICON_HEIGHT / 2),
            parent
        )
        createRailDownwardsAction = RMQAction(
            "新增轨道",
            "./source/rail.png",
            "向下新增轨道（线）",
            lambda: self.createRail(0, STATION_HEIGHT / 2 + ICON_HEIGHT / 2),
            parent
        )

        downwardsSubmenu = self.stationContextMenu.addMenu("向下")
        downwardsSubmenu.addAction(createStationDownwardsAction)
        downwardsSubmenu.addAction(createCAPDownwardsAction)
        downwardsSubmenu.addAction(createRailDownwardsAction)

        createStationLeftwardsAction = RMQAction(
            "新增站台",
            "./source/station.png",
            "向左新增站台（矩形）",
            lambda: self.createStation(-STATION_WIDTH, 0),
            parent
        )
        createCAPLeftwardsAction = RMQAction(
            "新增 CAP",
            "./source/cap.png",
            "向左新增 CAP（点）",
            lambda: self.createCAP(-(STATION_WIDTH / 2 + ICON_WIDTH / 2), 0),
            parent
        )
        createRailLeftwardsAction = RMQAction(
            "新增轨道",
            "./source/rail.png",
            "向左新增轨道（线）",
            lambda: self.createRail(-(STATION_WIDTH / 2 + ICON_WIDTH / 2), 0),
            parent
        )

        leftwardsSubmenu = self.stationContextMenu.addMenu("向左")
        leftwardsSubmenu.addAction(createStationLeftwardsAction)
        leftwardsSubmenu.addAction(createCAPLeftwardsAction)
        leftwardsSubmenu.addAction(createRailLeftwardsAction)

        createStationRightwardsAction = RMQAction(
            "新增站台",
            "./source/station.png",
            "向右新增站台（矩形）",
            lambda: self.createStation(STATION_WIDTH, 0),
            parent
        )
        createCAPRightwardsAction = RMQAction(
            "新增 CAP",
            "./source/cap.png",
            "向右新增 CAP（点）",
            lambda: self.createCAP(STATION_WIDTH / 2 + ICON_WIDTH / 2, 0),
            parent
        )
        createRailRightwardsAction = RMQAction(
            "新增轨道",
            "./source/rail.png",
            "向右新增轨道（线）",
            lambda: self.createRail(STATION_WIDTH / 2 + ICON_WIDTH / 2, 0),
            parent
        )

        rightwardsSubmenu = self.stationContextMenu.addMenu("向右")
        rightwardsSubmenu.addAction(createStationRightwardsAction)
        rightwardsSubmenu.addAction(createCAPRightwardsAction)
        rightwardsSubmenu.addAction(createRailRightwardsAction)

    def drawCAPContextMenu(self, parent):

        self.CAPContextMenu = QMenu(parent)

        createStationUpwardsAction = RMQAction(
            "新增站台",
            "./source/station.png",
            "向上新增站台（矩形）",
            lambda: self.createStation(
                0,
                -(ICON_HEIGHT / 2 + STATION_HEIGHT / 2)
            ),
            parent
        )
        createCAPUpwardsAction = RMQAction(
            "新增 CAP",
            "./source/cap.png",
            "向上新增 CAP（点）",
            lambda: self.createCAP(0, -ICON_HEIGHT),
            parent
        )
        createRailUpwardsAction = RMQAction(
            "新增轨道",
            "./source/rail.png",
            "向上新增轨道（线）",
            lambda: self.createRail(0, -ICON_HEIGHT),
            parent
        )

        upwardsSubmenu = self.CAPContextMenu.addMenu("向上")
        upwardsSubmenu.addAction(createStationUpwardsAction)
        upwardsSubmenu.addAction(createCAPUpwardsAction)
        upwardsSubmenu.addAction(createRailUpwardsAction)

        createStationDownwardsAction = RMQAction(
            "新增站台",
            "./source/station.png",
            "向下新增站台（矩形）",
            lambda: self.createStation(
                0,
                ICON_HEIGHT / 2 + STATION_HEIGHT / 2
            ),
            parent
        )
        createCAPDownwardsAction = RMQAction(
            "新增 CAP",
            "./source/cap.png",
            "向下新增 CAP（点）",
            lambda: self.createCAP(0, ICON_HEIGHT),
            parent
        )
        createRailDownwardsAction = RMQAction(
            "新增轨道",
            "./source/rail.png",
            "向下新增轨道（线）",
            lambda: self.createRail(0, ICON_HEIGHT),
            parent
        )

        downwardsSubmenu = self.CAPContextMenu.addMenu("向下")
        downwardsSubmenu.addAction(createStationDownwardsAction)
        downwardsSubmenu.addAction(createCAPDownwardsAction)
        downwardsSubmenu.addAction(createRailDownwardsAction)

        createStationLeftwardsAction = RMQAction(
            "新增站台",
            "./source/station.png",
            "向左新增站台（矩形）",
            lambda: self.createStation(
                -(ICON_WIDTH / 2 + STATION_WIDTH / 2),
                0
            ),
            parent
        )
        createCAPLeftwardsAction = RMQAction(
            "新增 CAP",
            "./source/cap.png",
            "向左新增 CAP（点）",
            lambda: self.createCAP(-ICON_WIDTH, 0),
            parent
        )
        createRailLeftwardsAction = RMQAction(
            "新增轨道",
            "./source/rail.png",
            "向左新增轨道（线）",
            lambda: self.createRail(-ICON_WIDTH, 0),
            parent
        )

        leftwardsSubmenu = self.CAPContextMenu.addMenu("向左")
        leftwardsSubmenu.addAction(createStationLeftwardsAction)
        leftwardsSubmenu.addAction(createCAPLeftwardsAction)
        leftwardsSubmenu.addAction(createRailLeftwardsAction)

        createStationRightwardsAction = RMQAction(
            "新增站台",
            "./source/station.png",
            "向右新增站台（矩形）",
            lambda: self.createStation(ICON_WIDTH / 2 + STATION_WIDTH / 2, 0),
            parent
        )
        createCAPRightwardsAction = RMQAction(
            "新增 CAP",
            "./source/cap.png",
            "向右新增 CAP（点）",
            lambda: self.createCAP(ICON_WIDTH, 0),
            parent
        )
        createRailRightwardsAction = RMQAction(
            "新增轨道",
            "./source/rail.png",
            "向右新增轨道（线）",
            lambda: self.createRail(ICON_WIDTH, 0),
            parent
        )

        rightwardsSubmenu = self.CAPContextMenu.addMenu("向右")
        rightwardsSubmenu.addAction(createStationRightwardsAction)
        rightwardsSubmenu.addAction(createCAPRightwardsAction)
        rightwardsSubmenu.addAction(createRailRightwardsAction)

    def createStation(self, offsetX=0, offsetY=0):

        stationName, ok = QInputDialog.getText(
            self.parent,
            "请输入站点名",
            "站点名"
        )

        if ok:

            self.addItem(
                RMStationQGraphicsItem(
                    self.focusPosition.x() + offsetX,
                    self.focusPosition.y() + offsetY,
                    name=stationName
                )
            )

    def createCAP(self, offsetX=0, offsetY=0):

        self.addItem(
            RMCAPQGraphicsItem(
                self.focusPosition.x() + offsetX,
                self.focusPosition.y() + offsetY,
            )
        )

    def createRail(self, offsetX=0, offsetY=0):

        self.addItem(
            RMRailQGraphicsItem(
                self.focusPosition.x() + offsetX,
                self.focusPosition.y() + offsetY,
            )
        )


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

        # 设置 dragMode 为拖拽
        self.setDragMode(QGraphicsView.ScrollHandDrag)

        # 设置 cursor 为十字镐
        self.viewport().setCursor(Qt.CrossCursor)

        # 解决 “画橡皮筋时释放 L 键” 的问题

        # 设置 rubberBandDragging flag 为 False
        self.rubberBandDragging = False

        # 设置 LReleasedWhileRubberBandDragging flag 为 False
        self.LReleasedWhileRubberBandDragging = False

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

    def mousePressEvent(self, event):

        # 重载鼠标按下函数

        # 调用超类的处理，防止不可追踪的 BUG
        super().mousePressEvent(event)

        # 左键且处于橡皮筋 dragMode

        if event.button() == Qt.LeftButton and self.dragMode() == QGraphicsView.RubberBandDrag:

            # 设置 rubberBandDragging flag 为 True
            self.rubberBandDragging = True

    def mouseReleaseEvent(self, event):

        # 重载鼠标释放函数

        # 调用超类的处理，防止不可追踪的 BUG
        super().mouseReleaseEvent(event)

        # 左键
        if event.button() == Qt.LeftButton:

            # 先释放鼠标左键再释放 L 键
            if self.LReleasedWhileRubberBandDragging == False:

                if self.dragMode() == QGraphicsView.RubberBandDrag:

                    # 橡皮筋完成后恢复箭头
                    self.viewport().setCursor(Qt.ArrowCursor)

                    # 设置 rubberBandDragging flag 为 False
                    self.rubberBandDragging = False

                elif self.dragMode() == QGraphicsView.ScrollHandDrag:

                    # 拖拽完成后恢复十字镐
                    self.viewport().setCursor(Qt.CrossCursor)

            # 先释放 L 键再释放鼠标左键
            elif self.LReleasedWhileRubberBandDragging:

                # 设置 dragMode 为拖拽
                self.setDragMode(QGraphicsView.ScrollHandDrag)

                # 设置 cursor 为十字镐
                self.viewport().setCursor(Qt.CrossCursor)

                # 设置 rubberBandDragging flag 为 False
                self.rubberBandDragging = False

                # 设置 LReleasedWhileRubberBandDragging flag 为 False
                self.LReleasedWhileRubberBandDragging = False

    def keyPressEvent(self, event):

        # 重载键盘按下函数

        # 调用超类的处理，防止不可追踪的 BUG
        super().keyPressEvent(event)

        # L 键且不是长按
        if event.key() == 76 and event.isAutoRepeat() == False:

            # 设置 dragMode 为橡皮筋
            self.setDragMode(QGraphicsView.RubberBandDrag)

            # 设置 cursor 为箭头
            self.viewport().setCursor(Qt.ArrowCursor)

    def keyReleaseEvent(self, event):

        # 重载键盘释放函数

        # 调用超类的处理，防止不可追踪的 BUG
        super().keyReleaseEvent(event)

        # L 键且不是长按
        if event.key() == 76 and event.isAutoRepeat() == False:

            # 没有正在画橡皮筋
            if self.rubberBandDragging == False:

                # 设置 dragMode 为拖拽
                self.setDragMode(QGraphicsView.ScrollHandDrag)

                # 设置 cursor 为十字镐
                self.viewport().setCursor(Qt.CrossCursor)

                # 设置 LReleasedWhileRubberBandDragging flag 为 False
                self.LReleasedWhileRubberBandDragging = False

            # 正在画橡皮筋
            elif self.rubberBandDragging:

                # 设置 LReleasedWhileRubberBandDragging flag 为 True
                self.LReleasedWhileRubberBandDragging = True


class RMApp(QMainWindow):

    def __init__(self):

        super().__init__()

        # 绘图 scene
        self.graphicsScene = RMQGraphicsScene(self)

        # 绘图 view
        self.graphicsView = RMQGraphicsView(self.graphicsScene, self)

        # 标题栏
        self.setWindowIcon(QIcon(RM_path("./source/logo.png")))
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

        newAction = RMQAction(
            "新建背景",
            "./source/new.png",
            "选择背景文件用作参考",
            self.new,
            self
        )
        fileMenu.addAction(newAction)

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

    def new(self):

        if len(self.graphicsScene.items()):

            reply = QMessageBox.question(
                self,
                "提示",
                "新建背景前请确保已保存当前任务",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.No:

                return

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
