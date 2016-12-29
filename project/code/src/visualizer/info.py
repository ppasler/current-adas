#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 19.12.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

from PyQt4 import QtGui

INFO_STRING = "FPS: %s\nFrame: %s"

class InfoPanelWidget(QtGui.QWidget):

    def __init__(self, maxFps, curFrame):
        super(InfoPanelWidget, self).__init__()
        self.mainLayout = QtGui.QHBoxLayout(self)
        self.mainWindow = self.window()

        self.maxFps = maxFps
        self.textbox = QtGui.QLineEdit(self)
        self.textbox.setText(INFO_STRING % (self.maxFps, curFrame))

        self.setObjectName("infopanel")

    def update(self, curFrame):
        self.textbox.setText(INFO_STRING % (self.maxFps, curFrame))