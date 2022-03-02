import logging

from PyQt5.QtWidgets import QFrame
from PyQt5.QtCore import QRect, pyqtSignal, Qt, QEvent
from PyQt5.QtGui import QMouseEvent, QCursor


class SelectButton(QFrame):
    check_signal = pyqtSignal(bool)

    def __init__(self, container):
        super(SelectButton, self).__init__(container)
        self.settings = None

        self.checkedFlag = False
        self.setupUi()

    def setupUi(self):
        self.setGeometry(QRect(6, 6, 20, 20))
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

    def check(self):
        self.settings.applyStylesheet(self, 'pressed')
        self.checkedFlag = True

    def uncheck(self):
        self.settings.applyStylesheet(self, 'default')
        self.checkedFlag = False

    def mouseReleaseEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.LeftButton:
            if self.checkedFlag:
                self.uncheck()
            else:
                self.check()
            self.check_signal.emit(self.checkedFlag)

    def enterEvent(self, e: QEvent) -> None:
        if not self.checkedFlag:
            self.settings.applyStylesheet(self, 'hover')
        super(SelectButton, self).enterEvent(e)

    def leaveEvent(self, e: QEvent) -> None:
        if not self.checkedFlag:
            self.settings.applyStylesheet(self, 'default')
        super(SelectButton, self).leaveEvent(e)

    def notify(self):
        pass

