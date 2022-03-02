import logging

from PyQt5.QtCore import QRect, QEvent, QPoint, pyqtSignal, Qt
from PyQt5.QtGui import QFont, QMouseEvent
from PyQt5.QtWidgets import QFrame

from customWidgets.buttons.iconClickButton import IconClickButton


class SettingsButton(QFrame):
    click_signal = pyqtSignal()

    def __init__(self, container):
        super(SettingsButton, self).__init__(container)
        self.settings = None

        self.settingsButton = IconClickButton(self, "settings.svg", "settings.svg", "settings.svg")
        self.setupUi()

    def setupUi(self):
        self.setGeometry(QRect(1500, 384, 188, 59))

        self.settingsButton.setObjectName("settingButton")
        self.settingsButton.setGeometry(QRect(4, 2, 188, 59))
        self.settingsButton.setText("Settings")
        self.settingsButton.click_signal.connect(lambda: self.onClick())
        font = QFont()
        font.setFamily("Calibri")
        font.setPointSize(18)
        self.settingsButton.setFont(font)

    def setSettings(self, settings):
        self.settings = settings
        if settings:
            self.settings.subscribe(self)
            self.settingsButton.setSettings(settings)
            self.applyStyleSheets()

        else:
            logging.warning(f"{self.objectName()}: settings value noneType")

    def applyStyleSheets(self):
        if self.settings:
            self.settings.applyStylesheet(self)
        else:
            logging.warning(f"{self.objectName()}: settings value noneType")

    def enterEvent(self, a0: QEvent) -> None:
        pos = self.pos()
        self.move(QPoint(pos.x() - 90, pos.y()))
        super(SettingsButton, self).enterEvent(a0)

    def leaveEvent(self, a0: QEvent) -> None:
        pos = self.pos()
        self.move(QPoint(pos.x() + 90, pos.y()))
        super(SettingsButton, self).enterEvent(a0)

    def mouseReleaseEvent(self, a0: QMouseEvent):
        if a0.button() == Qt.LeftButton:
            self.onClick()
        super(SettingsButton, self).mouseReleaseEvent(a0)

    def onClick(self):
        self.click_signal.emit()

    def notify(self):
        self.applyStyleSheets()
