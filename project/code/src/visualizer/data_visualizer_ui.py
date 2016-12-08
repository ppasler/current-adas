#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 07.12.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MainWindow(object):

    def setupUi(self, mainWindow, wrapper):
        self.mainWindow = mainWindow
        self.mainWindow.setObjectName(_fromUtf8("mainWindow"))
        self.mainWindow.showMaximized()
        #self.mainWindow.resize(823, 602)

        self.mainWindow.setCentralWidget(wrapper)

        self._initMenuBar()

        self._initStatusBar()

        self._initToolbar()

        self.retranslateUi()

        QtCore.QMetaObject.connectSlotsByName(mainWindow)

    def _initToolbar(self):
        exitAction = QtGui.QAction(QtGui.QIcon('exit24.png'), 'Exit', self.mainWindow)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(QtGui.qApp.quit)

        self.mainWindow.toolbar = self.mainWindow.addToolBar('Exit')
        self.mainWindow.toolbar.addAction(exitAction)

    def _initStatusBar(self):
        self.statusbar = QtGui.QStatusBar(self.mainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        self.mainWindow.setStatusBar(self.statusbar)

    def _initMenuBar(self):
        self.menubar = QtGui.QMenuBar(self.mainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 823, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.mainWindow.setMenuBar(self.menubar)

    def retranslateUi(self):
        self.mainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        #self.videoFrame.setText(QtGui.QApplication.translate("mainWindow", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))

