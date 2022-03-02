import logging

from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QRect, pyqtSignal, QSize, Qt, QEvent
from PyQt5.QtGui import QMouseEvent, QIcon, QCursor, QFont


class IconClickButton(QPushButton):
    click_signal = pyqtSignal()

    def __init__(self, container, iconUnClicked=None, iconClicked=None, iconHover=None):
        super(IconClickButton, self).__init__(container)
        self.settings = None
        self.clickedIcon = None
        self.unClickedIcon = None
        self.hoverIcon = None

        if iconClicked:
            self.clickedIcon = QIcon("customWidgets\icons\\" + iconClicked)
        if iconUnClicked:
            self.unClickedIcon = QIcon("customWidgets\icons\\" + iconUnClicked)
        if iconHover:
            self.hoverIcon = QIcon("customWidgets\icons\\" + iconHover)

        self.onTop = False
        self.setupUi()

    def setupUi(self):
        self.setStyleSheet("background-color: rgba(255, 255, 255, 0);")
        self.setText("")
        if self.unClickedIcon:
            self.setIcon(self.unClickedIcon)
        self.setCursor(QCursor(Qt.PointingHandCursor))

    def setSettings(self, settings):
        self.settings = settings
        if settings:
            self.settings.subscribe(self)
            self.applyStyleSheets()

    def applyStyleSheets(self):
        if self.settings:
            self.settings.applyStylesheet(self)
        else:
            logging.warning(f"{self.objectName()}: settings value noneType")

    def mousePressEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.LeftButton:
            if self.clickedIcon:
                self.setIcon(self.clickedIcon)
            if self.settings:
                self.settings.applyStylesheet(self, 'pressed')
        super(IconClickButton, self).mousePressEvent(e)



    def mouseReleaseEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.LeftButton:
            if self.onTop:
                if self.hoverIcon:
                    self.setIcon(self.hoverIcon)
                if self.settings:
                    self.settings.applyStylesheet(self, 'hover')
            else:
                if self.unClickedIcon:
                    self.setIcon(self.unClickedIcon)
                if self.settings:
                    self.settings.applyStylesheet(self, 'default')
            self.click_signal.emit()

    def enterEvent(self, e: QEvent) -> None:
        self.onTop = True
        if self.hoverIcon:
            self.setIcon(self.hoverIcon)
        if self.settings:
            self.settings.applyStylesheet(self, 'hover')
        super(IconClickButton, self).enterEvent(e)

    def leaveEvent(self, e: QEvent) -> None:
        self.onTop = False
        if self.unClickedIcon:
            self.setIcon(self.unClickedIcon)
        if self.settings:
            self.settings.applyStylesheet(self, 'default')
        super(IconClickButton, self).enterEvent(e)

    def notify(self):
        if self.onTop:
            if self.hoverIcon:
                self.setIcon(self.hoverIcon)
            if self.settings:
                self.settings.applyStylesheet(self, 'hover')
        else:
            if self.unClickedIcon:
                self.setIcon(self.unClickedIcon)
            if self.settings:
                self.settings.applyStylesheet(self, 'default')
