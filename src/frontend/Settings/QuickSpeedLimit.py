# -*- coding: utf-8 -*-

import logging

from PyQt5.QtWidgets import QApplication, QWidget, QWidgetAction

from Settings import SettingMenu
from CustomStatusBar.CStatusButton import CustomStatusBarToolButton
from .ui_quickspeedlimit import Ui_Form_quickSpeedLimit
from etmpy import EtmSetting

class QuickSpeedLimitBtn(CustomStatusBarToolButton):
    app = None
    def __init__(self, parent):
        super().__init__(parent)
        self.app = QApplication.instance()
        menu = SettingMenu(self)
        action = SpeedLimitingWidgetAction(self)
        menu.addAction(action)
        self.setMenu(menu)
        self.setText("限速")

        # Should be disabled when ETM not running
        self.app.xwaredpy.sigETMStatusPolled.connect(self.slotToggleEnableFlag)
        self.slotToggleEnableFlag()

    def slotToggleEnableFlag(self):
        self.setEnabled(self.app.xwaredpy.etmStatus)

class SpeedLimitingWidgetAction(QWidgetAction):
    def __init__(self, parent):
        super().__init__(parent)
        widget = QuickSpeedLimitForm(parent)
        self.setDefaultWidget(widget)

class QuickSpeedLimitForm(QWidget, Ui_Form_quickSpeedLimit):
    app = None
    def __init__(self, parent):
        super().__init__(parent)
        self.app = QApplication.instance()
        self.setupUi(self)
        self.checkBox_ulSpeedLimit.stateChanged.connect(self.slotStateChanged)
        self.checkBox_dlSpeedLimit.stateChanged.connect(self.slotStateChanged)
        self.slotStateChanged()

    def slotStateChanged(self):
        self.spinBox_ulSpeedLimit.setEnabled(self.checkBox_ulSpeedLimit.isChecked())
        self.spinBox_dlSpeedLimit.setEnabled(self.checkBox_dlSpeedLimit.isChecked())

    def loadSetting(self):
        etmSettings = self.app.etmpy.getSettings()

        if etmSettings.dLimit == -1:
            self.checkBox_dlSpeedLimit.setChecked(False)
            self.spinBox_dlSpeedLimit.setValue(self.app.settings.getint("internal", "dlspeedlimit"))
        else:
            self.checkBox_dlSpeedLimit.setChecked(True)
            self.spinBox_dlSpeedLimit.setValue(etmSettings.dLimit)

        if etmSettings.uLimit == -1:
            self.checkBox_ulSpeedLimit.setChecked(False)
            self.spinBox_ulSpeedLimit.setValue(self.app.settings.getint("internal", "ulspeedlimit"))
        else:
            self.checkBox_ulSpeedLimit.setChecked(True)
            self.spinBox_ulSpeedLimit.setValue(etmSettings.uLimit)

    def saveSetting(self):
        # called by parent menu's saveSettings.
        if self.checkBox_ulSpeedLimit.isChecked():
            ulSpeedLimit = self.spinBox_ulSpeedLimit.value()
        else:
            ulSpeedLimit = -1

        if self.checkBox_dlSpeedLimit.isChecked():
            dlSpeedLimit = self.spinBox_dlSpeedLimit.value()
        else:
            dlSpeedLimit = -1

        newEtmSetting = EtmSetting(dLimit = dlSpeedLimit, uLimit = ulSpeedLimit,
                                   maxRunningTasksNum = None)
        self.app.etmpy.saveSettings(newEtmSetting)
