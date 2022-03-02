from PyQt5.QtCore import pyqtSignal, QRect, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFrame, QLineEdit

from customWidgets.buttons.iconCheckButton import IconCheckButton
from customWidgets.buttons.iconClickButton import IconClickButton
from module.settingsConfig import SettingsConfig


class NewLabelFrame(QFrame):
    create_signal = pyqtSignal(str)

    def __init__(self, parent):
        super(NewLabelFrame, self).__init__(parent)
        self.settings = None

        self.nameLabelEdit = QLineEdit(self)

        self.createButton = IconClickButton(self)

        self.exitIcon = IconClickButton(self, "exit_chat_unselected.svg",
                                        "exit_chat_selected.svg",
                                        "exit_chat_selected.svg")
        self.setupUI()

    def setupUI(self):
        self.setGeometry(QRect(45, 730, 185, 110))
        self.setObjectName("newMessageContainer")

        self.nameLabelEdit.setGeometry(QRect(11, 34, 163, 21))
        font = QFont()
        font.setFamily("Calibri")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.nameLabelEdit.setFont(font)
        self.nameLabelEdit.setObjectName("newMessageTextEdit")
        self.nameLabelEdit.setPlaceholderText("New Label Name")

        self.createButton.setText("Create")
        self.createButton.setGeometry(QRect(11, 68, 163, 21))
        self.createButton.setObjectName("newMessageButton")

        self.createButton.click_signal.connect(lambda: self.onClickAction())

        self.exitIcon.setGeometry(QRect(166, 7, 12, 12))
        self.exitIcon.click_signal.connect(lambda: self.hide())

    def onClickAction(self):
        self.create_signal.emit(self.nameLabelEdit.text())
        self.hide()

    def setSettings(self, settings: SettingsConfig):
        self.settings = settings
        if settings:
            self.settings.subscribe(self)
            self.createButton.setSettings(self.settings)
            self.applyStylesheets()

    def applyStylesheets(self):
        self.settings.applyStylesheet(self)
        self.settings.applyStylesheet(self.nameLabelEdit)

    def notify(self):
        self.applyStylesheets()
