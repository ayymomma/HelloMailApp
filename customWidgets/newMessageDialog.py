import logging
import os

from PyQt5.QtCore import Qt, QRect, QSize, pyqtSignal
from PyQt5.QtGui import QFont, QResizeEvent
from PyQt5.QtWidgets import QDialog, QLabel, QTextEdit, QFileDialog, QFrame, QLineEdit, QWidget, QVBoxLayout, \
    QSpacerItem, QSizePolicy, QScrollArea, QLayout

from customWidgets.buttons.iconCheckButton import IconCheckButton
from customWidgets.buttons.iconClickButton import IconClickButton


class NewMessageDialog(QDialog):
    finish_signal = pyqtSignal(str, str, str, list)

    def __init__(self, container):
        super().__init__(container)
        self.setWindowTitle("New Message")
        self.settings = None
        self.container = QFrame(self)

        self.memoryCount = 0
        self.memoryShow = QLabel(self.container)

        self.titleLabel = QLabel(self.container)
        self.toLabel = QLabel(self.container)
        self.subjectLabel = QLabel(self.container)

        self.toTextEdit = QLineEdit(self.container)
        self.subjectTextEdit = QLineEdit(self.container)
        self.richTextEdit = QTextEdit(self.container)
        self.filename = ""

        self.pressed = False
        self.lastPos = None
        self.hasFirstResize = False
        self.attachmentList = []
        self.attachmentReffList = []

        self.exitIcon = IconClickButton(self.container, "exit_chat_unselected.svg",
                                        "exit_chat_selected.svg",
                                        "exit_chat_selected.svg")

        self.attachmentIco = IconClickButton(self.container, "attachment_popup_unselected.svg",
                                             "attachment_popup_selected.svg",
                                             "attachment_popup_selected.svg")

        self.trashIco = IconClickButton(self.container, "trash_popup_unselected.svg",
                                        "trash_popup_selected.svg",
                                        "trash_popup_selected.svg")

        self.sendIco = IconClickButton(self.container, "send_popup_selected.svg",
                                       "send_popup_selected.svg",
                                       "send_popup_selected.svg")

        self.attachmentScrollArea = QScrollArea(self)
        self.scrollAreaWidgetContents = QWidget()
        self.verticalLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.spacerItem = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.setupUI()
        self.setWindowFlag(Qt.FramelessWindowHint)

    def setupUI(self):

        font = QFont()
        font.setFamily("Calibri")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(35)
        self.memoryShow.setFont(font)
        self.memoryShow.setText("")
        self.memoryShow.setGeometry(QRect(0, 400, 601, 21))
        self.memoryShow.setStyleSheet("color: #15F346")
        self.memoryShow.setAlignment(Qt.AlignCenter)

        self.exitIcon.setObjectName("iconClickButton")
        self.attachmentIco.setObjectName("iconClickButton")
        self.trashIco.setObjectName("iconClickButton")

        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setGeometry(QRect(0, 0, 601, 456))
        self.setStyleSheet("background-color: rgba(0,0,0,0);")

        self.container.setObjectName("newMessageContainer")
        self.container.setGeometry(QRect(0, 0, 601, 456))

        self.titleLabel.setGeometry(QRect(247, 11, 127, 22))
        font = QFont()
        font.setFamily("Calibri")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(65)
        self.titleLabel.setFont(font)
        self.titleLabel.setText("New Message")
        self.titleLabel.setObjectName("label")

        self.toLabel.setGeometry(QRect(16, 47, 59, 19))
        font = QFont()
        font.setFamily("Calibri")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(65)
        self.toLabel.setFont(font)
        self.toLabel.setText("To:")
        self.toLabel.setObjectName("label")

        self.subjectLabel.setGeometry(QRect(16, 86, 75, 19))
        font = QFont()
        font.setFamily("Calibri")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(65)
        self.subjectLabel.setFont(font)
        self.subjectLabel.setText("Subject:")
        self.subjectLabel.setObjectName("label")

        self.toTextEdit.setGeometry(QRect(95, 47, 473, 25))
        self.toTextEdit.setObjectName("newMessageTextEdit")

        self.subjectTextEdit.setGeometry(QRect(95, 86, 473, 25))
        self.subjectTextEdit.setObjectName("newMessageTextEdit")

        self.richTextEdit.setGeometry(QRect(16, 125, 555, 260))
        self.richTextEdit.setObjectName("newMessageTextEdit")

        self.exitIcon.setGeometry(QRect(574, 11, 14, 14))
        self.exitIcon.click_signal.connect(self.close)

        self.attachmentIco.setGeometry(QRect(26, 409, 20, 18))
        self.attachmentIco.click_signal.connect(self.openFileNameDialog)

        self.trashIco.setGeometry(QRect(70, 409, 20, 19))

        self.sendIco.setGeometry(QRect(469, 400, 103, 34))
        font = QFont()
        font.setFamily("Calibri")
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.sendIco.setFont(font)
        self.sendIco.setText(" Send")
        self.sendIco.setFlat(True)
        self.sendIco.setObjectName("textButton")
        self.sendIco.click_signal.connect(lambda: self.onSendSignal())

        self.attachmentScrollArea.setObjectName("newMessageAttachmentArea")
        self.attachmentScrollArea.setEnabled(True)
        self.attachmentScrollArea.setGeometry(QRect(16, 345, 555, 50))
        sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.attachmentScrollArea.setSizePolicy(sizePolicy)
        self.attachmentScrollArea.setMinimumSize(QSize(555, 50))
        self.attachmentScrollArea.setMaximumSize(QSize(555, 50))
        self.attachmentScrollArea.setFrameShape(QFrame.NoFrame)
        self.attachmentScrollArea.setLineWidth(0)
        self.attachmentScrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.attachmentScrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.attachmentScrollArea.setWidgetResizable(False)

        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 555, 50))

        self.verticalLayout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(5)

        self.attachmentScrollArea.setWidget(self.scrollAreaWidgetContents)
        # self.attachmentScrollArea.setStyleSheet("background-color: #FFFFFF;")

    def addAttachment(self, path):
        self.verticalLayout.removeItem(self.spacerItem)
        # aici mai e o pb nu afiseaza continutul
        elButton = AttachmentItem(
            self.scrollAreaWidgetContents)  # ,"close_attachment.svg","close_attachment.svg","close_attachment.svg")
        elButton.setObjectName("navigationButton")
        elButton.setStyleSheet("background-color: #C4C4C4; border-radius: 10px")
        elButton.setMinimumSize(25, 25)
        elButton.setPath(path)
        elButton.click_signal.connect(lambda: self.closeAttachment(elButton))
        elButton.adjustSize()
        self.verticalLayout.addWidget(elButton)

        if self.memoryCount == 0:
            self.richTextEdit.setGeometry(QRect(16, 125, 555, 210))

        self.memoryCount += elButton.getMem()

        if self.memoryCount < 1000:
            self.memoryShow.setText(str(self.memoryCount) + " bytes")
        elif self.memoryCount < 1000000:
            self.memoryShow.setText("{:.2f}".format(self.memoryCount / 1000) + " KB")
        elif self.memoryCount < 25000000:
            self.memoryShow.setText("{:.2f}".format(self.memoryCount / 1000000) + " MB")
        else:
            self.memoryShow.setText("{:.2f}".format(self.memoryCount / 1000000) + " MB")
            self.memoryShow.setStyleSheet("color: #F60D0D")
            self.sendIco.setDisabled(True)

        self.verticalLayout.addSpacerItem(self.spacerItem)

    def closeAttachment(self, elButton):
        self.attachmentList.remove(elButton.path)
        self.memoryCount -= elButton.getMem()
        elButton.setParent(None)
        self.verticalLayout.removeWidget(elButton)

        if self.memoryCount == 0:
            self.memoryShow.setText("")
            self.richTextEdit.setGeometry(QRect(16, 125, 555, 260))
        if self.memoryCount > 0:
            if self.memoryCount < 1000:
                self.memoryShow.setText(str(self.memoryCount) + " bytes")
                self.sendIco.setDisabled(False)
                self.memoryShow.setStyleSheet("color: #15F346")
            elif self.memoryCount < 1000000:
                self.memoryShow.setText("{:.2f}".format(self.memoryCount / 1000) + " KB")
                self.sendIco.setDisabled(False)
                self.memoryShow.setStyleSheet("color: #15F346")
            elif self.memoryCount < 25000000:
                self.sendIco.setDisabled(False)
                self.memoryShow.setStyleSheet("color: #15F346")
                self.memoryShow.setText("{:.2f}".format(self.memoryCount / 1000000) + " MB")
            else:
                self.memoryShow.setText("{:.2f}".format(self.memoryCount / 1000000) + " MB")
                self.memoryShow.setStyleSheet("color: #F60D0D")

    def onSendSignal(self):
        destination = self.toTextEdit.text()
        subject = self.subjectTextEdit.text()
        messageText = self.richTextEdit.toPlainText()
        if "@gmail.com" in destination:
            self.finish_signal.emit(destination, subject, messageText, self.attachmentList)
            self.toTextEdit.setStyleSheet(self.toTextEdit.styleSheet() + "color: white;")
            self.close()
        else:
            self.toTextEdit.setStyleSheet(self.toTextEdit.styleSheet() + "color: red;")

    def close(self) -> bool:
        self.attachmentList.clear()
        self.setParent(None)
        return super(NewMessageDialog, self).close()

    def openFileNameDialog(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Select a file", "",
                                                  "All Files (*);;Python Files (*.py)")
        if fileName:
            self.attachmentList.append(fileName)
            self.addAttachment(fileName)

    def setSubject(self, subject):
        self.subjectTextEdit.setText(subject)

    def setEmail(self, email):
        self.toTextEdit.setText(email)

    def mousePressEvent(self, event):
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if event.button() == Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()

        super(NewMessageDialog, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            # adjust offset from clicked point to origin of widget
            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPos()
            diff = globalPos - self.__mouseMovePos
            newPos = self.mapFromGlobal(currPos + diff)
            self.move(newPos)

            self.__mouseMovePos = globalPos

        super(NewMessageDialog, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.__mousePressPos is not None:
            moved = event.globalPos() - self.__mousePressPos
            if moved.manhattanLength() > 3:
                event.ignore()
                return

            super(NewMessageDialog, self).mouseReleaseEvent(event)

    def setSettings(self, settings):
        self.settings = settings
        if settings:
            self.exitIcon.setSettings(self.settings)
            self.attachmentIco.setSettings(self.settings)
            self.trashIco.setSettings(self.settings)
            self.sendIco.setSettings(self.settings)
            self.applyStyleSheets()
            self.settings.subscribe(self)

    def applyStyleSheets(self):
        self.settings.applyStylesheet(self)
        self.settings.applyStylesheet(self.container)
        self.settings.applyStylesheet(self.titleLabel)
        self.settings.applyStylesheet(self.toTextEdit)
        self.settings.applyStylesheet(self.subjectTextEdit)
        self.settings.applyStylesheet(self.toLabel)
        self.settings.applyStylesheet(self.subjectLabel)
        self.settings.applyStylesheet(self.richTextEdit)
        self.settings.applyStylesheet(self.attachmentScrollArea)

    # def resizeEvent(self, e: QResizeEvent) -> None:
    #     if self.hasFirstResize:
    #         difH = e.size().height() - e.oldSize().height()
    #         difW = e.size().width() - e.oldSize().width()
    #         print(f"{difW} {difH}")
    #         self.resize(QSize(self.size().width()+difW, self.size().height()+difH))
    #     self.hasFirstResize = True
    #     super(NewMessageDialog, self).resizeEvent(e)

    def notify(self):
        self.applyStyleSheets()


class AttachmentItem(IconClickButton):
    def __init__(self, parent, iconUnClicked=None, iconClicked=None, iconHover=None):
        super(AttachmentItem, self).__init__(parent, iconUnClicked, iconClicked, iconHover)
        self.name = None
        self.path = None
        self.memory = 0

    def setPath(self, path):
        self.name = path.split("/")[-1]
        self.path = path
        self.memory = os.path.getsize(path)

        if self.memory < 1000:
            self.setText(self.name + "(" + str(self.memory) + " bytes)")
        elif self.memory < 1000000:
            self.setText(self.name + "({:.2f}".format(self.memory / 1000) + " KB)")
        else:
            self.setText(self.name + "({:.2f}".format(self.memory / 1000000) + " MB)")

    def getMem(self):
        return self.memory
