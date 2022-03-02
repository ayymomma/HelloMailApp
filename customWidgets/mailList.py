from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QRect
from PyQt5.QtWidgets import QLayout, QFrame

from customWidgets.buttons.iconCheckButton import IconCheckButton
from customWidgets.buttons.iconClickButton import IconClickButton
from customWidgets.mailItem import MailItem


class MailList(QtWidgets.QScrollArea):
    mailItemChange = pyqtSignal(QtWidgets.QFrame)
    firstLastSelectSignal = pyqtSignal(bool)

    def __init__(self, container):
        super(MailList, self).__init__(container)
        self.settings = None

        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.spacerItem = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)

        self.selectedMailItem = None
        self.selectedMails = []
        self.mailItems = []
        self.setupUi()

    def setupUi(self):
        self.setEnabled(True)
        self.setGeometry(QtCore.QRect(254, 139, 422, 741))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sizePolicy().hasHeightForWidth())
        self.setSizePolicy(sizePolicy)
        self.setMinimumSize(QtCore.QSize(422, 741))
        self.setMaximumSize(QtCore.QSize(422, 16777215))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setLineWidth(0)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidgetResizable(False)
        self.setAlignment(Qt.AlignCenter)

        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 422, 911))

        self.verticalLayout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(10)

        self.verticalLayout.addSpacerItem(self.spacerItem)

        self.setWidget(self.scrollAreaWidgetContents)

    def addMailItem(self, mailData):
        self.verticalLayout.removeItem(self.spacerItem)

        mailItem = MailItem(self.scrollAreaWidgetContents, mailData)
        mailItem.setObjectName("mailItem")
        mailItem.setSettings(self.settings)
        mailItem.click_signal.connect(lambda itm: self.onMailClicked(itm))
        mailItem.select_check_signal.connect(lambda ch: self.onMailChecked(ch, mailItem))
        self.verticalLayout.addWidget(mailItem, 0, Qt.AlignHCenter)
        self.verticalLayout.addSpacerItem(self.spacerItem)

        self.mailItems.append(mailItem)

        return mailItem

    def removeMailItem(self, mailItem):
        mailItem.settings.unsubscribe(mailItem)
        mailItem.setParent(None)
        self.verticalLayout.removeWidget(mailItem)

    @QtCore.pyqtSlot()
    def onMailClicked(self, mailItem):
        self.selectMailItem(mailItem)
        self.mailItemChange.emit(mailItem)

    @QtCore.pyqtSlot()
    def onMailChecked(self, checked, mailItem):
        if checked:
            if len(self.selectedMails) == 0:
                self.firstLastSelectSignal.emit(True)
            self.selectedMails.append(mailItem)
        else:
            self.selectedMails.remove(mailItem)
            if len(self.selectedMails) == 0:
                self.firstLastSelectSignal.emit(False)

    def selectMailItem(self, mailItem):
        if self.selectedMailItem:
            self.selectedMailItem.deselect()
        mailItem.select()
        self.selectedMailItem = mailItem

    def unselectMailItem(self):
        if self.selectedMailItem:
            self.selectedMailItem.deselect()
        self.selectedMailItem = None

    def resizeContent(self, e: QSize) -> None:
        self.resize(QSize(422, self.size().height() + e.height()))
        self.scrollAreaWidgetContents.resize(QSize(422, self.scrollAreaWidgetContents.size().height() + e.height()))

    def setSettings(self, settings):
        self.settings = settings

    def getSelected(self):
        return self.selectedMailItem

    def clearMailList(self):
        for i in reversed(range(self.verticalLayout.count()-1)):
            widget = self.verticalLayout.takeAt(i).widget()
            if widget is not None:
                widget.setParent(None)
        self.selectedMailItem = None

    def clearSelectedList(self):
        self.selectedMails.clear()

    def notify(self):
        pass

    def selectAll(self):
        for item in self.mailItems:
            item.checkItem(True)
            self.selectedMails.append(item)

    def unselectAll(self):
        copySelectedMail = []
        for item in self.selectedMails:
            copySelectedMail.append(item)
        for item in copySelectedMail:
            item.checkItem(False)
            self.selectedMails.remove(item)

    def getSelectedMails(self):
        if len(self.selectedMails) == 0 and self.selectedMailItem:
            return [self.selectedMailItem]
        return self.selectedMails

