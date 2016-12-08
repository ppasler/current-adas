# -*- coding: utf-8 -*-

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MainWindow(object):

    def setupUi(self, MainWindow, VideoWidget):
        self.MainWindow = MainWindow
        self.MainWindow.setObjectName(_fromUtf8("MainWindow"))
        self.MainWindow.resize(823, 602)

        self.MainWindow.setCentralWidget(VideoWidget)

        self._initMenuBar()

        self._initStatusBar()

        self._initToolbar()

        self.retranslateUi()

        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def _initToolbar(self):
        exitAction = QtGui.QAction(QtGui.QIcon('exit24.png'), 'Exit', self.MainWindow)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(QtGui.qApp.quit)

        self.MainWindow.toolbar = self.MainWindow.addToolBar('Exit')
        self.MainWindow.toolbar.addAction(exitAction)

    def _initStatusBar(self):
        self.statusbar = QtGui.QStatusBar(self.MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        self.MainWindow.setStatusBar(self.statusbar)

    def _initMenuBar(self):
        self.menubar = QtGui.QMenuBar(self.MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 823, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.MainWindow.setMenuBar(self.menubar)

    def retranslateUi(self):
        self.MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))
        #self.videoFrame.setText(QtGui.QApplication.translate("MainWindow", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))

