#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 19.12.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

from PyQt4 import QtGui

def toggleText(button, text1, text2, method):
    if button.text() == text1:
        button.setText(text2)
    else:
        button.setText(text1)

class ControlPanelWidget(QtGui.QWidget):


    def __init__(self, ):
        super(ControlPanelWidget, self).__init__()
        self.mainLayout = QtGui.QHBoxLayout(self)
        self.mainWindow = self.window()

        self._initPrev()
        self._initPlayPause()
        self._initNext()

        self.setObjectName("controlpanel")


    def _initPrev(self):
        self.prevButton = QtGui.QPushButton('prev', self)
        self.prevButton.clicked.connect(self.prev)
        self.mainLayout.addWidget(self.prevButton)

    def prev(self):
        # TODO
        self.window().prev()

    def _initPlayPause(self):
        self.playPauseButton = QtGui.QPushButton('play', self)
        self.playPauseButton.clicked.connect(self._handlePlayPause)
        self.mainLayout.addWidget(self.playPauseButton)

    def _handlePlayPause(self):
        button = self.sender()
        if button.text() == "play":
            self.pause(button)
        else:
            self.play(button)

    def play(self, button):
        button.setText("play")
        self.window().play()

    def pause(self, button):
        button.setText("pause")
        self.window().pause()

    def _initNext(self):
        self.nextButton = QtGui.QPushButton('next', self)
        self.nextButton.clicked.connect(self.next)
        self.mainLayout.addWidget(self.nextButton)

    def next(self):
        self.pause(self.playPauseButton)
        self.window().next()
