import logging
import os
import sys

from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import QPushButton, QFrame, QGraphicsBlurEffect, QFileDialog
from PyQt5.QtCore import QSize, QPoint, QRect, Qt, QRunnable, QThreadPool, QFile, QIODevice

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import QtCore, QtWidgets, QtGui

from customWidgets.actionBar import ActionBar, ACTION
from customWidgets.labelList import LabelList
from customWidgets.newMessageDialog import NewMessageDialog
from customWidgets.mailList import MailList
from customWidgets.mailView import MailView
from customWidgets.searchBar import SearchBar
from customWidgets.buttons.settingsButton import SettingsButton
from customWidgets.settingsPanel import SettingsPanel
from module.gmailApiService import GmailApi
from customWidgets.buttons.iconClickButton import IconClickButton
from module.settingsConfig import SettingsConfig

from customWidgets.navigationList import NavigationList, BUTTON

API_NAME = 'gmail'
API_VERSION = 'v1'
SCOPES = ['https://mail.google.com/']
CLIENT_FILE = 'token/credentials.json'

logging.basicConfig(level=logging.INFO)


class HelloMail(QMainWindow):

    def __init__(self):
        super(HelloMail, self).__init__()
        self.hasFirstResize = False

        self.gmailApi = GmailApi(CLIENT_FILE, API_NAME, API_VERSION, SCOPES, 'x')
        self.settings = SettingsConfig()
        self.settings.subscribe(self)

        self.centralWidget = QtWidgets.QWidget(self)
        self.mailList = MailList(self.centralWidget)
        self.mailView = MailView(self.centralWidget)
        self.mailCover = QtWidgets.QFrame(self.centralWidget)
        self.searchBar = SearchBar(self.centralWidget)
        self.actionBar = ActionBar(self.centralWidget)
        self.refreshButton = IconClickButton(self.centralWidget, "refresh_unselected", "refresh_unselected",
                                             "refresh_hover")

        self.navigationList = NavigationList(self.centralWidget)
        self.newMessageButton = IconClickButton(self.centralWidget, "new_message.svg", "new_message.svg",
                                                "new_message.svg")

        self.customLabelList = LabelList(self.centralWidget)
        self.settingsPanel = SettingsPanel(self.centralWidget)

        self.logoImage = QtWidgets.QLabel(self.centralWidget)
        self.logoImage.setGeometry(QtCore.QRect(3, 40, 260, 59))
        self.logoImage.setStyleSheet("border-radius:10px")
        pixmap = QPixmap("customWidgets" + os.path.sep + "icons" + os.path.sep + "logo.png")
        self.logoImage.setPixmap(pixmap)

        self.setWindowIcon(QtGui.QIcon("customWidgets" + os.path.sep + "icons" + os.path.sep + "icon.png"))

        self.loadingFrame = QFrame(self.centralWidget)
        self.blur_effect = QGraphicsBlurEffect()

        self.setupUi()
        self.setupStyleSheets()
        self.addMailItemsOnStartUp()
        self.addCustomLabels()

    def setupUi(self):

        self.setWindowTitle("HelloMail")
        self.resize(1440, 900)
        self.setMinimumSize(QtCore.QSize(1440, 900))
        self.setCentralWidget(self.centralWidget)

        self.mailCover.setGeometry(QtCore.QRect(244, 830, 432, 81))
        self.mailCover.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.mailCover.setFrameShadow(QtWidgets.QFrame.Raised)

        self.mailList.setObjectName("mailList")
        self.mailList.mailItemChange.connect(lambda mailItem: self.onMailItemChange(mailItem))
        self.mailList.firstLastSelectSignal.connect(lambda first: self.actionBar.setCheckButton(first))
        self.mailList.setSettings(self.settings)

        self.newMessageButton.setGeometry(QRect(20, 156, 209, 45))
        font = QFont()
        font.setFamily("Calibri")
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.newMessageButton.setFont(font)
        self.newMessageButton.setText(" New Message")
        self.newMessageButton.setFlat(True)
        self.newMessageButton.setObjectName("textButton")
        self.newMessageButton.setSettings(self.settings)

        self.mailView.setObjectName("mailView")
        self.mailView.setSettings(self.settings)
        self.mailView.star_check_signal.connect(lambda ch: self.onMailViewStarChecked(ch))
        self.mailView.reply_check_signal.connect(lambda: self.onReplyMailViewClicked())
        self.mailView.attachment_download_signal.connect(lambda msId, att: self.onAttachmentDownloadSignal(msId, att))
        self.mailView.delete_signal.connect(lambda: self.onActionBarSignal(ACTION.TRASH_FLAG))
        self.mailView.forward_signal.connect(lambda: self.onForwardButton())

        self.navigationList.setSettings(self.settings)
        self.navigationList.label_change_signal.connect(lambda button: self.onLabelChange(button))

        self.newMessageButton.click_signal.connect(lambda: self.onNewMessageDialog())
        self.newMessageButton.setWindowFlags(Qt.WindowStaysOnBottomHint)

        self.searchBar.setObjectName('searchBar')
        self.searchBar.setSettings(self.settings)
        self.searchBar.search_signal.connect(lambda query: self.onSearch(query))

        self.actionBar.setObjectName("actionBar")
        self.actionBar.setSettings(self.settings)
        self.actionBar.action_signal.connect(lambda action: self.onActionBarSignal(action))

        self.settingsPanel.setObjectName("settingPanel")
        self.settingsPanel.setSettings(self.settings)

        self.customLabelList.setSettings(self.settings)
        self.customLabelList.click_signal.connect(lambda label_id: self.onCustomLabel(label_id))
        self.customLabelList.newLabelFrame.create_signal.connect(lambda name: self.onCreateNewLabel(name))

        self.refreshButton.setObjectName("refreshButton")
        self.refreshButton.setSettings(self.settings)
        self.refreshButton.setGeometry(QRect(12, 850, 40, 40))
        self.refreshButton.click_signal.connect(lambda: self.onRefresh())

        self.loadingFrame.setGeometry(QRect(16, 16, 1408, 868))
        self.blur_effect.setBlurRadius(500)
        self.loadingFrame.setGraphicsEffect(self.blur_effect)
        self.loadingFrame.hide()

    def resizeEvent(self, e: QtGui.QResizeEvent) -> None:
        if self.hasFirstResize:
            difH = e.size().height() - e.oldSize().height()
            difW = e.size().width() - e.oldSize().width()

    def setupStyleSheets(self):
        self.setStyleSheet(self.settings.getStyleSheet("mainWindow"))
        self.mailCover.setStyleSheet(self.settings.getStyleSheet("mailCover"))

    def addMailItemsOnStartUp(self):
        mails_data = self.gmailApi.get_emails_by_tags(["INBOX"], self.settings.getMessageNumber())
        for mail_data in mails_data:
            mailItem = self.mailList.addMailItem(mail_data)
            mailItem.star_check_signal.connect(lambda ch, mI: self.onMailItemStarChecked(ch, mI))

    def addCustomLabels(self):
        labels = self.gmailApi.get_custom_labels()
        for label in labels:
            self.customLabelList.addTagElement(label)

    @QtCore.pyqtSlot()
    def onNewMessageDialog(self):
        newMessageDialog = NewMessageDialog(self.centralWidget)
        newMessageDialog.setSettings(self.settings)
        newMessageDialog.finish_signal.connect(
            lambda destination, subject, messageText, attachment:
            self.onSendMessage(destination, subject, messageText, None, None, attachment))
        newMessageDialog.show()

    @QtCore.pyqtSlot()
    def onMailItemStarChecked(self, checked, mailItem):
        if checked:
            self.gmailApi.modify_labels_to_email(mailItem.mailData.get('id'), ['STARRED'], [])
            mailItem.mailData['labelIds'].append('STARRED')
        else:
            self.gmailApi.modify_labels_to_email(mailItem.mailData.get('id'), [], ['STARRED'])
            mailItem.mailData['labelIds'].remove('STARRED')
        self.mailView.checkStar(checked)

    @QtCore.pyqtSlot()
    def onMailViewStarChecked(self, checked):
        if checked:
            self.gmailApi.modify_labels_to_email(self.mailList.getSelected().mailData.get('id'), ['STARRED'], [])
            self.mailList.getSelected().mailData['labelIds'].append('STARRED')
        else:
            self.gmailApi.modify_labels_to_email(self.mailList.getSelected().mailData.get('id'), [], ['STARRED'])
            self.mailList.getSelected().mailData['labelIds'].remove('STARRED')
        self.mailList.getSelected().checkStar(checked)

    @QtCore.pyqtSlot()
    def onMailItemChange(self, mailItem):
        self.mailView.setMailContentView(mailItem.mailData)
        if 'UNREAD' in mailItem.mailData['labelIds']:
            self.gmailApi.modify_labels_to_email(mailItem.mailData.get('id'), [], ['UNREAD'])
            mailItem.mailData['labelIds'].remove('UNREAD')

    @QtCore.pyqtSlot()
    def onLabelChange(self, label):
        mails = None
        self.mailView.hideMail()
        self.mailList.clearMailList()
        self.customLabelList.deselect()
        if label == BUTTON.INBOX:
            mails = self.gmailApi.get_emails_by_tags(['INBOX'], self.settings.getMessageNumber())
        elif label == BUTTON.STARRED:
            mails = self.gmailApi.get_emails_by_tags(['STARRED'], self.settings.getMessageNumber())
        elif label == BUTTON.SENT:
            mails = self.gmailApi.get_emails_by_tags(['SENT'], self.settings.getMessageNumber())
        elif label == BUTTON.SPAM:
            mails = self.gmailApi.get_emails_by_tags(['SPAM'], self.settings.getMessageNumber())
        elif label == BUTTON.DRAFT:
            mails = self.gmailApi.get_emails_by_tags(['DRAFT'], self.settings.getMessageNumber())
        elif label == BUTTON.TRASH:
            mails = self.gmailApi.get_emails_by_tags(['TRASH'], self.settings.getMessageNumber())
        for mail_data in mails:
            mailItem = self.mailList.addMailItem(mail_data)
            mailItem.star_check_signal.connect(lambda ch, mI: self.onMailItemStarChecked(ch, mI))

    @QtCore.pyqtSlot()
    def onCustomLabel(self, label_id):
        self.mailView.hideMail()
        self.mailList.clearMailList()
        self.navigationList.deselect()
        mails = self.gmailApi.get_emails_by_tags([label_id], self.settings.getMessageNumber())
        for mail_data in mails:
            mailItem = self.mailList.addMailItem(mail_data)
            mailItem.star_check_signal.connect(lambda ch, mI: self.onMailItemStarChecked(ch, mI))

    @QtCore.pyqtSlot()
    def onCreateNewLabel(self, name):
        newLabel = self.gmailApi.create_custom_label(name)
        self.customLabelList.addTagElement(newLabel)

    @QtCore.pyqtSlot()
    def onActionBarSignal(self, action):
        if action == ACTION.CHECKED_FLAG:
            self.mailList.selectAll()
        elif action == ACTION.UNCHECKED_FLAG:
            self.mailList.unselectAll()
        elif action == ACTION.UNREAD_FLAG:
            mailIds = []
            selectedMails = self.mailList.getSelectedMails()
            selectedMail = self.mailList.getSelected()
            for selected in selectedMails:
                if selectedMail and selected == selectedMail:
                    selectedMail.deselect()
                    self.mailView.hideMail()
                selected.unread()
                mailIds.append(selected.mailData.get('id'))
            self.mailList.clearSelectedList()
            self.actionBar.setCheckButton(False)
            self.gmailApi.modify_labels_to_emails(mailIds, ['UNREAD'], [])
        elif action == ACTION.READ_FLAG:
            mailIds = []
            selectedMails = self.mailList.getSelectedMails()
            selectedMail = self.mailList.getSelected()
            for selected in selectedMails:
                if selectedMail and selected == selectedMail:
                    selectedMail.deselect()
                    self.mailView.hideMail()
                selected.read()
                mailIds.append(selected.mailData.get('id'))
            self.mailList.clearSelectedList()
            self.actionBar.setCheckButton(False)
            self.gmailApi.modify_labels_to_emails(mailIds, [], ['UNREAD'])
        elif action == ACTION.TRASH_FLAG:
            mailIds = []
            selectedMails = self.mailList.getSelectedMails()
            selectedMail = self.mailList.getSelected()
            for selected in selectedMails:
                if selectedMail and selected == selectedMail:
                    selectedMail.deselect()
                    self.mailView.hideMail()
                self.mailList.removeMailItem(selected)
                mailIds.append(selected.mailData.get('id'))
            if self.navigationList.getLabel().replace(" ", "").upper() == "TRASH" or \
                    self.navigationList.getLabel().replace(" ", "").upper() == "SPAM":
                self.gmailApi.delete_emails(mailIds)
            else:
                self.actionBar.setCheckButton(False)
                self.gmailApi.modify_labels_to_emails(mailIds, ['TRASH'], ['INBOX', 'STARRED', 'SPAM'])
            self.mailList.clearSelectedList()
        elif action == ACTION.ARCHIVE_FLAG:
            mailIds = []
            selectedMails = self.mailList.getSelectedMails()
            selectedMail = self.mailList.getSelected()
            for selected in selectedMails:
                if selectedMail and selected == selectedMail:
                    selectedMail.deselect()
                    self.mailView.hideMail()
                self.mailList.removeMailItem(selected)
                mailIds.append(selected.mailData.get('id'))
            self.mailList.clearSelectedList()
            self.actionBar.setCheckButton(False)
            self.gmailApi.modify_labels_to_emails(mailIds, [], ['INBOX'])
        elif action == ACTION.WARNING_FLAG:
            mailIds = []
            selectedMails = self.mailList.getSelectedMails()
            selectedMail = self.mailList.getSelected()
            for selected in selectedMails:
                if selectedMail and selected == selectedMail:
                    selectedMail.deselect()
                    self.mailView.hideMail()
                self.mailList.removeMailItem(selected)
                mailIds.append(selected.mailData.get('id'))
            self.mailList.clearSelectedList()
            self.actionBar.setCheckButton(False)
            self.gmailApi.modify_labels_to_emails(mailIds, ['SPAM'], ['INBOX'])

    @QtCore.pyqtSlot()
    def onReplyMailViewClicked(self):
        threadId = self.mailList.getSelected().mailData.get('threadId')
        messageId = self.mailList.getSelected().mailData.get('id')
        newMessageDialog = NewMessageDialog(self.centralWidget)
        newMessageDialog.setSettings(self.settings)
        newMessageDialog.setSubject("Re: " + self.mailList.selectedMailItem.getEmailSubject())
        newMessageDialog.setEmail(self.mailList.selectedMailItem.getEmailAddress())
        newMessageDialog.finish_signal.connect(
            lambda destination, subject, messageText, attachment:
            self.onSendMessage(destination, subject, messageText, messageId, threadId, attachment))
        newMessageDialog.show()

    @QtCore.pyqtSlot()
    def onSearch(self, query):
        self.mailView.hideMail()
        self.mailList.clearMailList()
        self.navigationList.deselect()
        self.customLabelList.deselect()
        mails = self.gmailApi.search_messages(query, self.settings.getMessageNumber())
        for mail_data in mails:
            mailItem = self.mailList.addMailItem(mail_data)
            mailItem.star_check_signal.connect(lambda ch, mI: self.onMailItemStarChecked(ch, mI))

    @QtCore.pyqtSlot()
    def onSendMessage(self, destination, subject, messageText, messageId, threadId=None, attachment=[]):
        rez = self.gmailApi.get_profile()
        myEmail = rez['emailAddress']
        print(threadId)
        self.gmailApi.send_message(myEmail, destination, subject, messageText, messageId, threadId, attachment)

    @QtCore.pyqtSlot()
    def onRefresh(self):
        self.mailView.hideMail()
        self.mailList.clearMailList()
        mails = []

        if self.navigationList.last_label_id:
            print('ok')
            self.customLabelList.deselect()
            mails = self.gmailApi.get_emails_by_tags([self.navigationList.last_label_id],
                                                     self.settings.getMessageNumber())
        if self.customLabelList.last_label_id:
            print('ok')
            self.navigationList.deselect()
            mails = self.gmailApi.get_emails_by_tags([self.customLabelList.last_label_id],
                                                     self.settings.getMessageNumber())
        for mail_data in mails:
            mailItem = self.mailList.addMailItem(mail_data)
            mailItem.star_check_signal.connect(lambda ch, mI: self.onMailItemStarChecked(ch, mI))

    @QtCore.pyqtSlot()
    def onAttachmentDownloadSignal(self, message_id, attachment):
        fileName, _ = QFileDialog.getSaveFileName(self, "Save file", attachment["name"], "All Files (*)")
        if fileName:
            file = self.gmailApi.download_attachment(attachment['id'], message_id)
            f = QFile(fileName)
            if f.open(QIODevice.WriteOnly):
                f.write(file)
                f.close()

    @QtCore.pyqtSlot()
    def onForwardButton(self):

        threadId = self.mailList.getSelected().mailData.get('threadId')
        messageId = self.mailList.getSelected().mailData.get('id')
        newMessageDialog = NewMessageDialog(self.centralWidget)
        newMessageDialog.setSettings(self.settings)
        newMessageDialog.setSubject("Forward: " + self.mailList.selectedMailItem.getEmailSubject())
        newMessageDialog.richTextEdit.setText(self.mailList.selectedMailItem.mailData['body'])

        newMessageDialog.finish_signal.connect(
            lambda destination, subject, messageText, attachment:
            self.onSendMessage(destination, subject, messageText, messageId, threadId, attachment))
        newMessageDialog.show()

    def resizeEvent(self, e: QtGui.QResizeEvent) -> None:
        if self.hasFirstResize:
            difH = e.size().height() - e.oldSize().height()
            difW = e.size().width() - e.oldSize().width()

            self.mailList.resizeContent(QSize(difW, difH))
            self.mailCover.move(QPoint(self.mailCover.pos().x(), self.mailCover.pos().y() + difH))
            self.mailView.resizeContent(QSize(difW, difH))

            self.searchBar.move(QPoint(self.searchBar.pos().x() + difW, self.searchBar.pos().y()))
            self.settingsPanel.resizeContent(QSize(difW, difH))

            self.refreshButton.move(QPoint(self.refreshButton.pos().x(), self.refreshButton.pos().y() + difH))

        if not self.hasFirstResize:
            self.hasFirstResize = True

        super(HelloMail, self).resizeEvent(e)

    def notify(self):
        self.setupStyleSheets()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    helloMail = HelloMail()

    helloMail.show()
    sys.exit(app.exec())
