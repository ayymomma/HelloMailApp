import json
import logging

from PyQt5.QtCore import pyqtSignal

from customWidgets.settingsPanel import SettingsPanel


class SettingsConfig:

    def __init__(self):
        self.subs = []
        self.theme = None
        self.settingsData = None
        self.numberMessage = 5
        self.initSettings()

    def initSettings(self):
        with open(f"customWidgets/settings/settings.json") as file_object:
            self.settingsData = json.load(file_object)
            self.theme = self.initTheme(self.settingsData["theme"])
            self.numberMessage = self.settingsData["nr_mess"]

    def initTheme(self, filename):
        with open(f"customWidgets/styles/{filename}.json") as file_object:
            # store file data in object
            data = json.load(file_object)
            return data

    def getData(self):
        return self.settingsData

    def setTheme(self, newTheme):
        self.theme = self.initTheme(newTheme)
        self.notify()

    def getTheme(self):
        return self.theme

    def getThemeValues(self, element):
        if self.theme:
            return self.theme.get(element)
        else:
            return None

    def getMessageNumber(self):
        return self.numberMessage

    def setMessageNumber(self, nr):
        self.numberMessage = nr

    def getStyleSheet(self, element, state="default"):
        styleSheet = ""
        elementValues = self.getThemeValues(element)
        if elementValues:
            stateValues = elementValues.get(state)
            if stateValues:
                for elementVal in stateValues:
                    styleSheet = styleSheet + f"{elementVal.get('name')}:{elementVal.get('value')};"
        return styleSheet

    def applyStylesheet(self, widget, state="default"):
        name = widget.objectName()
        #uita te aici
        style = self.getStyleSheet(name, state)
        if style:
            widget.setStyleSheet(style)
        else:
            logging.info(f"{name} - {state} style not found.")

    def subscribe(self, element):
        self.subs.append(element)

    def unsubscribe(self, element):
        self.subs.remove(element)

    def getTheme(self):
        return self.theme

    def notify(self):
        for sub in self.subs:
            try:
                sub.notify()
            except Exception  as es:
                print(es)
                self.subs.remove(sub)
