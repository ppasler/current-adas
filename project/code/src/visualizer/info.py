#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 19.12.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

from PyQt4 import QtGui

INFO_STRING = "FPS: %.2f\t%ds\tFrame: %d"

class InfoPanelWidget(QtGui.QWidget):

    def __init__(self, maxFps, curFrame):
        super(InfoPanelWidget, self).__init__()
        self.mainLayout = QtGui.QHBoxLayout(self)
        self.mainWindow = self.window()

        self.maxFps = maxFps
        self.textbox = QtGui.QLineEdit(self)
        self.textbox.setFixedWidth(400)
        self.setText(0)

        self.setObjectName("infopanel")

    def update(self, curFrame):
        self.setText(curFrame)

    def setText(self, curFrame):
        self.textbox.setText(INFO_STRING % (self.maxFps, round(curFrame / self.maxFps), curFrame))