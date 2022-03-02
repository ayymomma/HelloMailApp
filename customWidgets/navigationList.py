from PyQt5.QtCore import QRect, pyqtSignal
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel, QWidget

from customWidgets.buttons.iconCheckButton import IconCheckButton


class NavigationList(QWidget):
    label_change_signal = pyqtSignal(int)

    def __init__(self, container):
        super(NavigationList, self).__init__(container)
        self.container = container
        self.settings = None
        self.selected = None
        self.last_label_id = "INBOX"

        self.navigationLabel = QLabel(container)
        self.inboxIcon = IconCheckButton(self.container, "inbox_navigation_unselected.svg",
                                         "inbox_navigation_hover.svg",
                                         "inbox_navigation_hover.svg")
        self.selected = self.inboxIcon

        self.staredIcon = IconCheckButton(self.container, "stared_navigation_unselected.svg",
                                          "stared_navigation_hover.svg",
                                          "stared_navigation_hover.svg")
        self.sentIcon = IconCheckButton(self.container, "sent_navigation_unselected.svg",
                                        "sent_navigation_hover.svg",
                                        "sent_navigation_hover.svg")
        self.warningIcon = IconCheckButton(self.container, "warning_navigation_unselected.svg",
                                           "warning_navigation_hover.svg",
                                           "warning_navigation_hover.svg")
        self.draftsIcon = IconCheckButton(self.container, "drafts_navigation_unselected.svg",
                                          "drafts_navigation_hover.svg",
                                          "drafts_navigation_hover.svg")
        self.trashIcon = IconCheckButton(self.container, "trash_navigation_unselected.svg",
                                         "trash_navigation_hover.svg",
                                         "trash_navigation_hover.svg")

        self.setupUI()

    def setupUI(self):
        self.navigationLabel.setObjectName("label")
        self.navigationLabel.setGeometry(QRect(23, 244, 148, 31))
        font = QFont()
        font.setFamily("Calibri")
        font.setPointSize(18)
        font.setWeight(75)
        self.navigationLabel.setFont(font)
        self.navigationLabel.setText("Navigation")

        self.inboxIcon.setObjectName("navigationButton")
        self.inboxIcon.setGeometry(QRect(61, 296, 100, 24))
        font = QFont()
        font.setFamily("Calibri")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.inboxIcon.setFont(font)
        self.inboxIcon.setText(" Inbox")
        self.inboxIcon.setFlat(True)
        self.inboxIcon.check_signal.connect(lambda ch: self.onInbox())

        self.staredIcon.setObjectName("navigationButton")
        self.staredIcon.setGeometry(QRect(61, 331, 100, 24))
        font = QFont()
        font.setFamily("Calibri")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.staredIcon.setFont(font)
        self.staredIcon.setText(" Starred")
        self.staredIcon.setFlat(True)
        self.staredIcon.check_signal.connect(lambda ch: self.onStared())

        self.sentIcon.setObjectName("navigationButton")
        self.sentIcon.setGeometry(QRect(61, 364, 100, 24))
        font = QFont()
        font.setFamily("Calibri")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.sentIcon.setFont(font)
        self.sentIcon.setText(" Sent")
        self.sentIcon.setFlat(True)
        self.sentIcon.check_signal.connect(lambda ch: self.onSent())

        self.warningIcon.setObjectName("navigationButton")
        self.warningIcon.setGeometry(QRect(61, 397, 100, 24))
        font = QFont()
        font.setFamily("Calibri")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.warningIcon.setFont(font)
        self.warningIcon.setText(" Spam")
        self.warningIcon.setFlat(True)
        self.warningIcon.check_signal.connect(lambda ch: self.onSpam())

        self.draftsIcon.setObjectName("navigationButton")
        self.draftsIcon.setGeometry(QRect(62, 430, 100, 24))
        font = QFont()
        font.setFamily("Calibri")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.draftsIcon.setFont(font)
        self.draftsIcon.setText(" Drafts")
        self.draftsIcon.setFlat(True)
        self.draftsIcon.check_signal.connect(lambda ch: self.onDraft())

        self.trashIcon.setObjectName("navigationButton")
        self.trashIcon.setGeometry(QRect(62, 462, 100, 24))
        font = QFont()
        font.setFamily("Calibri")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.trashIcon.setFont(font)
        self.trashIcon.setText(" Trash")
        self.trashIcon.setFlat(True)
        self.trashIcon.check_signal.connect(lambda ch: self.onTrash())

    def setSettings(self, settings):
        self.settings = settings
        if settings:
            self.inboxIcon.setSettings(settings)
            self.inboxIcon.check()
            self.staredIcon.setSettings(settings)
            self.sentIcon.setSettings(settings)
            self.warningIcon.setSettings(settings)
            self.draftsIcon.setSettings(settings)
            self.trashIcon.setSettings(settings)

            self.settings.subscribe(self)

            self.settings.applyStylesheet(self.navigationLabel)

    def notify(self):
        self.settings.applyStylesheet(self.navigationLabel)

    def onInbox(self):
        if self.selected == self.inboxIcon:
            self.selected.check()
        else:
            if self.selected:
                self.selected.uncheck()
            self.selected = self.inboxIcon
        self.last_label_id = "INBOX"
        self.label_change_signal.emit(BUTTON.INBOX)

    def onStared(self):
        if self.selected == self.staredIcon:
            self.staredIcon.check()
        else:
            if self.selected:
                self.selected.uncheck()
            self.selected = self.staredIcon
        self.last_label_id = "STARRED"
        self.label_change_signal.emit(BUTTON.STARRED)

    def onSent(self):
        if self.selected == self.sentIcon:
            self.sentIcon.check()
        else:
            if self.selected:
                self.selected.uncheck()
            self.selected = self.sentIcon
        self.last_label_id = "SENT"
        self.label_change_signal.emit(BUTTON.SENT)

    def onSpam(self):
        if self.selected == self.warningIcon:
            self.warningIcon.check()
        else:
            if self.selected:
                self.selected.uncheck()
            self.selected = self.warningIcon
        self.last_label_id = "SPAM"
        self.label_change_signal.emit(BUTTON.SPAM)

    def onDraft(self):
        if self.selected == self.draftsIcon:
            self.draftsIcon.check()
        else:
            if self.selected:
                self.selected.uncheck()
            self.selected = self.draftsIcon
        self.last_label_id = "DRAFT"
        self.label_change_signal.emit(BUTTON.DRAFT)

    def onTrash(self):
        if self.selected == self.trashIcon:
            self.trashIcon.check()
        else:
            if self.selected:
                self.selected.uncheck()
            self.selected = self.trashIcon
        self.last_label_id = "TRASH"
        self.label_change_signal.emit(BUTTON.TRASH)

    def getLabel(self):
        return self.selected.text()

    def deselect(self):
        if self.selected:
            self.selected.uncheck()
        self.selected = None
        self.last_label_id = None


class BUTTON:
    INBOX = 0
    STARRED = 1
    SENT = 2
    SPAM = 3
    DRAFT = 4
    TRASH = 5
