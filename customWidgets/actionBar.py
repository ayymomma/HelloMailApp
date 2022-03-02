from PyQt5.QtCore import QRect, pyqtSignal
from PyQt5.QtWidgets import QFrame

from customWidgets.buttons.iconCheckButton import IconCheckButton
from customWidgets.buttons.iconClickButton import IconClickButton


class ActionBar(QFrame):
    action_signal = pyqtSignal(int)

    def __init__(self, parent):
        super(ActionBar, self).__init__(parent)
        self.settings = None

        self.selectCheckButton = IconCheckButton(self, "circle_unselected.svg", "circle_selected.svg",
                                                 "circle_hover.svg")
        self.archiveButton = IconClickButton(self, "archive_unselected.svg", "archive_hover.svg",
                                             "archive_hover.svg")
        self.warningButton = IconClickButton(self, "warning_unselected.svg", "warning_hover.svg",
                                             "warning_hover.svg")
        self.trashButton = IconClickButton(self, "trash_unselected.svg", "trash_hover.svg", "trash_hover.svg")
        self.unreadMailButton = IconClickButton(self, "mail_unread_unselected.svg", "mail_unread_hover.svg",
                                                "mail_unread_hover.svg")
        self.readMailButton = IconClickButton(self, "mail_read_unselected.svg", "mail_read_hover.svg",
                                              "mail_read_hover.svg")

        self.setupUi()

    def setupUi(self):
        self.setGeometry(QRect(268, 87, 392, 42))
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)

        self.selectCheckButton.setObjectName("actionButton")
        self.selectCheckButton.setGeometry(QRect(13, 10, 20, 20))
        self.selectCheckButton.check_signal.connect(lambda check: self.onCheck(check))

        self.archiveButton.setObjectName("actionButton")

        self.archiveButton.setGeometry(QRect(97, 10, 22, 21))
        self.archiveButton.click_signal.connect(lambda: self.onArchive())

        self.warningButton.setObjectName("actionButton")
        self.warningButton.setGeometry(QRect(140, 4, 36, 36))
        self.warningButton.click_signal.connect(lambda: self.onWarning())

        self.trashButton.setObjectName("actionButton")
        self.trashButton.setGeometry(QRect(190, 4, 34, 34))
        self.trashButton.click_signal.connect(lambda: self.onTrash())

        self.unreadMailButton.setObjectName("actionButton")
        self.unreadMailButton.setGeometry(QRect(292, 15, 26, 18))
        self.unreadMailButton.click_signal.connect(lambda: self.onUnread())

        self.readMailButton.setObjectName("actionButton")
        self.readMailButton.setGeometry(QRect(340, 8, 32, 32))
        self.readMailButton.click_signal.connect(lambda: self.onRead())

    def onCheck(self, check):
        if check:
            self.action_signal.emit(ACTION.CHECKED_FLAG)
        else:
            self.action_signal.emit(ACTION.UNCHECKED_FLAG)

    def onArchive(self):
        self.action_signal.emit(ACTION.ARCHIVE_FLAG)

    def onWarning(self):
        self.action_signal.emit(ACTION.WARNING_FLAG)

    def onTrash(self):
        self.action_signal.emit(ACTION.TRASH_FLAG)

    def onUnread(self):
        self.action_signal.emit(ACTION.UNREAD_FLAG)

    def onRead(self):
        self.action_signal.emit(ACTION.READ_FLAG)

    def setSettings(self, settings):
        self.settings = settings
        if self.settings:
            self.settings.subscribe(self)
            self.selectCheckButton.setSettings(settings)
            self.archiveButton.setSettings(settings)
            self.warningButton.setSettings(settings)
            self.trashButton.setSettings(settings)
            self.unreadMailButton.setSettings(settings)
            self.readMailButton.setSettings(settings)
            self.applyStyleSheets()

    def applyStyleSheets(self):
        if self.settings:
            self.settings.applyStylesheet(self)

    def notify(self):
        self.applyStyleSheets()

    def setCheckButton(self, check):
        if check:
            self.selectCheckButton.check()
        else:
            self.selectCheckButton.uncheck()


class ACTION:
    CHECKED_FLAG = 0
    UNCHECKED_FLAG = 1
    ARCHIVE_FLAG = 2
    WARNING_FLAG = 3
    TRASH_FLAG = 4
    UNREAD_FLAG = 5
    READ_FLAG = 6
