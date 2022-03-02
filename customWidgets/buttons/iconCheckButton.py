import logging

from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QRect, pyqtSignal, QSize, Qt, QEvent
from PyQt5.QtGui import QMouseEvent, QIcon, QCursor


class IconCheckButton(QPushButton):
    check_signal = pyqtSignal(bool)

    def __init__(self, container, iconUnselectedPath, iconSelectedPath, iconHoverPath):
        super(IconCheckButton, self).__init__(container)
        self.settings = None

        self.selectedIcon = QIcon("customWidgets\icons\\" + iconSelectedPath)
        self.unselectedIcon = QIcon("customWidgets\icons\\" + iconUnselectedPath)
        self.hoverIcon = QIcon("customWidgets\icons\\" + iconHoverPath)

        self.active = False
        self.onTop = False
        self.setupUi()

    def setupUi(self):
        self.setStyleSheet("background-color: rgba(255, 255, 255, 0);")
        self.setText("")
        self.setIcon(self.unselectedIcon)
        self.setCursor(QCursor(Qt.PointingHandCursor))

    def setSettings(self, settings):
        self.settings = settings
        if settings:
            self.settings.subscribe(self)
            self.applyStyleSheets()

    def applyStyleSheets(self):
        if self.settings:
            self.settings.applyStylesheet(self)

    def check(self):
        self.setIcon(self.selectedIcon)
        self.active = True
        if self.settings:
            self.settings.applyStylesheet(self, "pressed")

    def uncheck(self):
        self.setIcon(self.unselectedIcon)
        self.active = False
        if self.settings:
            self.settings.applyStylesheet(self)

    def mouseReleaseEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.LeftButton:
            if self.active:
                self.uncheck()
            else:
                self.check()
            self.check_signal.emit(self.active)

    def enterEvent(self, e: QEvent) -> None:
        if not self.active:
            self.setIcon(self.hoverIcon)
            if self.settings:
                self.settings.applyStylesheet(self, "hover")
        self.onTop = True
        super(IconCheckButton, self).enterEvent(e)

    def leaveEvent(self, e: QEvent) -> None:
        if not self.active:
            self.setIcon(self.unselectedIcon)
            if self.settings:
                self.settings.applyStylesheet(self)
        self.onTop = False
        super(IconCheckButton, self).enterEvent(e)

    def notify(self):
        if self.active:
            if self.settings:
                self.settings.applyStylesheet(self, "pressed")
        else:
            if self.settings:
                self.settings.applyStylesheet(self, "default")
