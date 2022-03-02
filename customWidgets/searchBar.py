import logging

from PyQt5.QtCore import QRect, QEvent, pyqtSignal, Qt
from PyQt5.QtGui import QFont, QFocusEvent, QKeyEvent
from PyQt5.QtWidgets import QFrame, QLineEdit

from customWidgets.buttons.iconClickButton import IconClickButton


class CustomLineEdit(QLineEdit):
    focus_signal = pyqtSignal(bool)
    enter_signal = pyqtSignal()

    def __init__(self, parent=None):
        super(CustomLineEdit, self).__init__(parent)

    def focusInEvent(self, a0: QFocusEvent) -> None:
        self.focus_signal.emit(True)
        super(CustomLineEdit, self).focusInEvent(a0)

    def focusOutEvent(self, a0: QFocusEvent) -> None:
        self.focus_signal.emit(False)
        super(CustomLineEdit, self).focusOutEvent(a0)

    def keyPressEvent(self, a0: QKeyEvent) -> None:
        if a0.key() == 16777220 or a0.key() == 16777221:  # enter key
            self.enter_signal.emit()
        super(CustomLineEdit, self).keyPressEvent(a0)


class SearchBar(QFrame):
    search_signal = pyqtSignal(str)

    def __init__(self, parent):
        super(SearchBar, self).__init__(parent)
        self.settings = None

        self.searchButton = IconClickButton(self, "search_button.svg", "search_button_hover.svg",
                                            "search_button_hover.svg")
        self.searchInput = CustomLineEdit(self)
        self.setupUi()

    def setupUi(self):
        self.setGeometry(QRect(968, 50, 450, 24))
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)

        self.searchButton.setObjectName("searchInput")
        self.searchButton.setGeometry(QRect(7, 2, 20, 21))
        self.searchButton.click_signal.connect(lambda: self.onSearch())

        self.searchInput.setObjectName('searchInput')
        font = QFont()
        font.setFamily("Calibri")
        font.setPointSize(12)
        self.searchInput.setGeometry(QRect(30, 1, 355, 21))
        self.searchInput.setFont(font)
        self.searchInput.focus_signal.connect(lambda focused: self.onFocus(focused))
        self.searchInput.enter_signal.connect(lambda: self.onSearch())
        self.searchInput.setPlaceholderText("type here to search...")

    def setSettings(self, settings):
        self.settings = settings
        if settings:
            self.settings.subscribe(self)
            self.searchButton.setSettings(settings)
            self.applyStyleSheets()
        else:
            logging.warning(f"{self.objectName()}: settings value noneType")

    def applyStyleSheets(self):
        if self.settings:
            self.settings.applyStylesheet(self)
            self.settings.applyStylesheet(self.searchInput)
        else:
            logging.warning(f"{self.objectName()}: settings value noneType")

    def enterEvent(self, a0: QEvent) -> None:
        super(SearchBar, self).enterEvent(a0)

    def leaveEvent(self, a0: QEvent) -> None:
        super(SearchBar, self).enterEvent(a0)

    def onFocus(self, focused):
        if focused:
            if self.settings:
                self.settings.applyStylesheet(self, 'pressed')
        else:
            if self.settings:
                self.settings.applyStylesheet(self, 'default')

    def onSearch(self):
        query = self.searchInput.text()
        self.search_signal.emit(query)

    def notify(self):
        self.applyStyleSheets()
