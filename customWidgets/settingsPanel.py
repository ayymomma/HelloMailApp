import json
import os
import sys
from os import listdir

from PyQt5.QtCore import Qt, QRect, QPoint, QFileInfo
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFrame, QScrollArea, QWidget, QVBoxLayout, QSpacerItem, QSizePolicy, QLayout, QComboBox, \
    QLabel, QTextEdit, QTreeView, QHeaderView, QLineEdit, QColorDialog, QGraphicsColorizeEffect

from customWidgets.buttons.iconClickButton import IconClickButton
from customWidgets.buttons.settingsButton import SettingsButton
from customWidgets.jsonViewer import JsonModel


class SettingsPanel(QFrame):

    def __init__(self, parent):
        super(SettingsPanel, self).__init__(parent)
        self.settings = None
        self.savedSettings = {}
        self.cancelButton = IconClickButton(self, "exit_chat_unselected.svg",
                                            "exit_chat_selected.svg",
                                            "exit_chat_selected.svg")

        self.settingsButton = SettingsButton(parent)
        self.messageNumberText = QLabel(self)
        self.themeText = QLabel(self)
        self.customDesignText = QLabel(self)
        self.titleText = QLabel(self)

        self.messageNumberSelect = QLineEdit(self)
        self.themeSelect = QComboBox(self)

        self.view = QTreeView(self)
        self.model = JsonModel(self)

        self.saveButton = IconClickButton(self)
        self.nameFileEdit = QLineEdit(self)
        self.applyButton = IconClickButton(self)

        self.logOutButton = IconClickButton(self)

        self.hide()
        self.numberMessage = 5

        self.colorEdit = QTextEdit(self)
        self.labelShowColor = IconClickButton(self)

        self.setupUI()

    def setupUI(self):
        self.colorEdit.setGeometry(QRect(468, 371, 110, 26))
        self.colorEdit.setObjectName("saveButton")
        self.colorEdit.setReadOnly(True)
        self.colorEdit.setText("#000000")

        self.labelShowColor.setGeometry(QRect(560, 371, 26, 26))
        self.labelShowColor.setStyleSheet("background: #000000;border-radius: 10px;")


        self.labelShowColor.click_signal.connect(lambda: self.colorChose())

        self.messageNumberText.setGeometry(31, 190, 355, 22)
        font = QFont()
        font.setFamily("Calibri")
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.messageNumberText.setFont(font)
        self.messageNumberText.setText("Numer of message shown")
        self.messageNumberText.setObjectName("label")

        font.setPointSize(25)

        self.titleText.setGeometry(260, 32, 235, 45)
        self.titleText.setFont(font)
        self.titleText.setText("Settings")
        self.titleText.setObjectName("label")

        font.setPointSize(18)

        self.themeText.setGeometry(31, 239, 235, 30)
        self.themeText.setFont(font)
        self.themeText.setText("Theme")
        self.themeText.setObjectName("label")

        self.customDesignText.setGeometry(31, 363, 235, 34)
        self.customDesignText.setFont(font)
        self.customDesignText.setText("Custom Design")
        self.customDesignText.setObjectName("label")

        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setGeometry(799, 0, 648, 901)

        self.cancelButton.setGeometry(QRect(10, 10, 25, 25))
        self.cancelButton.click_signal.connect(self.closeSettings)
        self.cancelButton.setObjectName("iconClickButton")

        self.settingsButton.click_signal.connect(self.openSettings)
        self.settingsButton.setObjectName("settingButton")

        self.settingsButton.setGeometry(QRect(1405, 384, 188, 59))
        self.settingsButton.setWindowFlags(Qt.WindowStaysOnTopHint)

        font.setPointSize(13)

        self.messageNumberSelect.setGeometry(QRect(420, 190, 158, 30))
        self.messageNumberSelect.setFont(font)
        self.messageNumberSelect.setObjectName("settingsComboBox")

        self.themeSelect.setGeometry(QRect(64, 288, 515, 28))
        self.themeSelect.setFont(font)
        self.themeSelect.setObjectName("settingsComboBox")

        self.uploadFiles()

        self.themeSelect.currentTextChanged.connect(lambda: self.themeEventComboBox())

        self.view.setModel(self.model)
        json_path = QFileInfo(__file__).absoluteDir().filePath("styles/default.json")
        with open(json_path) as file:
            document = json.load(file)
            self.model.load(document)
        self.view.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.view.resize(522, 346)
        self.view.move(QPoint(64, 412))
        self.view.setObjectName("settingsComboBox")
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.saveButton.setGeometry(QRect(508, 774, 78, 29))
        self.saveButton.setText("Save")
        self.saveButton.setObjectName("saveButton")
        self.saveButton.click_signal.connect(lambda: self.saveJson())

        self.nameFileEdit.setGeometry(QRect(64, 774, 436, 29))
        self.nameFileEdit.setPlaceholderText("New File Name")
        self.nameFileEdit.setObjectName("fileNameEdit")

        self.applyButton.setGeometry(QRect(508, 843, 78, 29))
        self.applyButton.setText("Apply")
        self.applyButton.setObjectName("applyButton")
        self.applyButton.click_signal.connect(lambda: self.onApplyButton())

        self.logOutButton.setGeometry(QRect(14, 843, 211, 41))
        self.logOutButton.setText("Log Out")
        self.logOutButton.setObjectName("logOut")
        self.logOutButton.click_signal.connect(lambda: self.onDisconnect())

    def colorChose(self):
        color = QColorDialog.getColor()


        self.colorEdit.setText(str(color.name()))
        self.labelShowColor.setStyleSheet(f"background: {color.name()};border-radius: 10px;")
        #
        # graphic = QGraphicsColorizeEffect(self)
        # graphic.setColor(color)
        # self.labelShowColor.setGraphicsEffect(graphic)

    def onDisconnect(self):
        tokenPath = QFileInfo(__file__).absoluteDir().currentPath() + "/token/token.pickle"
        print(QFileInfo(__file__).absoluteDir().currentPath() + "/token/token.pickle")
        os.remove(tokenPath)
        os.execl(sys.executable, os.path.abspath(__file__), *sys.argv)

    def onApplyButton(self):
        if self.settings:
            self.nameFileEdit.setText("")
            self.saveJson()
            themeName = self.themeSelect.currentText()
            self.settings.setTheme(themeName)

            if self.messageNumberSelect.text().isnumeric() and not self.messageNumberSelect.text().isspace() \
                    and self.messageNumberSelect.text() != "":
                self.settings.setMessageNumber(self.messageNumberSelect.text())
                self.savedSettings["nr_mess"] = self.messageNumberSelect.text()

            self.savedSettings["theme"] = self.themeSelect.currentText()
            f = open(str(QFileInfo(__file__).absoluteDir().filePath("settings/settings.json")), 'w+')
            json.dump(self.savedSettings, f)

    def setSettings(self, settings):
        self.settings = settings
        if settings:
            print(self.settings.getTheme())
            settings.subscribe(self)
            self.cancelButton.setSettings(settings)
            self.saveButton.setSettings(settings)
            self.settingsButton.setSettings(settings)

            self.applyStyleSheets()
            self.savedSettings = self.settings.getData()
            self.messageNumberSelect.setText(str(self.settings.getMessageNumber()))

            print(self.savedSettings["theme"])
            self.themeSelect.setCurrentText(self.savedSettings["theme"])

    def applyStyleSheets(self):
        if self.settings:
            self.settings.applyStylesheet(self)
            self.settings.applyStylesheet(self.messageNumberText)
            self.settings.applyStylesheet(self.themeText)
            self.settings.applyStylesheet(self.customDesignText)
            self.settings.applyStylesheet(self.messageNumberSelect)
            self.settings.applyStylesheet(self.themeSelect)
            self.settings.applyStylesheet(self.view)
            self.settings.applyStylesheet(self.nameFileEdit)
            self.settings.applyStylesheet(self.logOutButton)
            self.settings.applyStylesheet(self.titleText)
            self.settings.applyStylesheet(self.applyButton)
            self.settings.applyStylesheet(self.colorEdit)


    def resizeContent(self, difSize):
        self.move(difSize.width() + self.pos().x(), self.pos().y())
        self.resize(self.size().width(), self.size().height() + difSize.height())
        self.settingsButton.move(QPoint(self.settingsButton.pos().x() + difSize.width(), self.settingsButton.pos().y()))

        self.logOutButton.move(QPoint(self.logOutButton.pos().x(), self.logOutButton.pos().y() + difSize.height()))
        self.applyButton.move(QPoint(self.applyButton.pos().x(), self.applyButton.pos().y() + difSize.height()))

    def openSettings(self):
        self.show()
        self.settingsButton.hide()
        # self.uploadCustomDesignData()

    def closeSettings(self):
        self.hide()
        self.settingsButton.show()

    def notify(self):
        self.applyStyleSheets()

    def uploadFiles(self):
        mypath = os.path.abspath(os.getcwd()) + "\customWidgets\styles"
        files = [f for f in listdir(mypath)]

        for file in files:
            self.themeSelect.addItem(file[:-5])

    def themeEventComboBox(self):
        self.view.setModel(self.model)
        json_path = QFileInfo(__file__).absoluteDir().filePath(f"styles/{self.themeSelect.currentText()}.json")
        with open(json_path) as file:
            document = json.load(file)
            self.model.load(document)
        self.view.header().setSectionResizeMode(0, QHeaderView.Stretch)
        # self.view.setAlternatingRowColors(True)
        self.view.resize(522, 346)
        self.view.move(QPoint(64, 412))
        self.view.setObjectName("settingsComboBox")

    def saveJson(self):
        nameFile = self.nameFileEdit.text()
        if nameFile != "" and nameFile != "default":
            # print(QFileInfo(__file__).absoluteDir().filePath("styles/" + nameFile + ".json"))
            with open(str(QFileInfo(__file__).absoluteDir().filePath("styles/" + nameFile + ".json")), 'w+') as f:
                json.dump(self.model.to_json(), f)
            self.nameFileEdit.setText("")
            self.nameFileEdit.setPlaceholderText("Save successfully")
            self.themeSelect.addItem(nameFile)
            self.themeSelect.setCurrentText(nameFile)
        elif nameFile == "default":
            self.nameFileEdit.setText("")
            self.nameFileEdit.setPlaceholderText("Cannot modify default file")
        else:
            nameFile = self.themeSelect.currentText()
            with  open(str(QFileInfo(__file__).absoluteDir().filePath("styles/" + nameFile + ".json")), 'w+') as f:
                json.dump(self.model.to_json(), f)
