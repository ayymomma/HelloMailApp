import os

from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import QRect, pyqtSignal, Qt
from PyQt5.QtGui import QMouseEvent, QCursor, QPixmap
import logging


class AvatarIcon(QLabel):
    click_signal = pyqtSignal()

    def __init__(self, container):
        super(AvatarIcon, self).__init__(container)
        self.settings = None

        self.setupUi()

    def setupUi(self):
        self.setGeometry(QRect(30, 20, 40, 40))
        self.setCursor(QCursor(Qt.PointingHandCursor))

    def mouseReleaseEvent(self, e: QMouseEvent) -> None:
        if e.button() == Qt.LeftButton:
            self.click_signal.emit()

    def setSettings(self, settings):
        self.settings = settings
        if self.settings:
            self.settings.subscribe(self)
            self.applyStyleSheets()
        else:
            logging.warning(f"{self.objectName()}: settings value noneType")

    def applyStyleSheets(self):
        if self.settings:
            self.settings.applyStylesheet(self)

    def notify(self):
        self.applyStyleSheets()

    def setImage(self, name):
        pixmap = QPixmap("customWidgets" + os.path.sep + "icons" + os.path.sep + "avatars" + os.path.sep + name)
        pixmap = pixmap.scaled(self.size().width(), self.size().height(), Qt.KeepAspectRatio)
        self.setPixmap(pixmap)
