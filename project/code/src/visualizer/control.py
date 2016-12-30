#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 19.12.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

from PyQt4 import QtGui
from PyQt4.Qt import Qt


PLAY_STRING = "play"
PAUSE_STRING = "pause"
PREV_SEC_STRING = "prev second"
PREV_STRING = "prev"
NEXT_STRING = "next"
NEXT_SEC_STRING = "next second"

class ControlPanelWidget(QtGui.QWidget):
    def __init__(self, frameCount):
        super(ControlPanelWidget, self).__init__()
        self.mainLayout = QtGui.QVBoxLayout(self)

        self.buttonPanel = ButtonPanelWidget()
        self.slider = Slider(frameCount)
        self.mainLayout.addWidget(self.slider)
        self.mainLayout.addWidget(self.buttonPanel)

        self.setObjectName("controlpanel")

class Slider(QtGui.QSlider):

    def __init__(self, frameCount):
        super(Slider, self).__init__(Qt.Horizontal)
        self.setMaximum(frameCount)
        self.sliderReleased.connect(self.handleSliderReleased)

        self.setObjectName("sliderpanel")

    def handleSliderReleased(self):
        self.window().setCurFrame(self.value())

class ButtonPanelWidget(QtGui.QWidget):

    def __init__(self):
        super(ButtonPanelWidget, self).__init__()
        self.mainLayout = QtGui.QHBoxLayout(self)

        self._initButtons()

        self.setObjectName("buttonpanel")

    def _initButtons(self):
        self.prevSecButton = self._createButton(PREV_SEC_STRING, self.prevSec)
        self.prevButton = self._createButton(PREV_STRING, self.prev)
        self.playPauseButton = self._createButton(PAUSE_STRING, self._handlePlayPause)
        self.nextButton = self._createButton(NEXT_STRING, self.next)
        self.nextSecButton = self._createButton(NEXT_SEC_STRING, self.nextSec)

    def _createButton(self, label, method):
        button = QtGui.QPushButton(label, self)
        button.clicked.connect(method)
        self.mainLayout.addWidget(button)
        return button

    def prevSec(self):
        self.pause(self.playPauseButton)
        self.window().prevSec()

    def prev(self):
        self.pause(self.playPauseButton)
        self.window().prev()

    def _handlePlayPause(self):
        button = self.sender()
        if button.text() == PAUSE_STRING:
            self.pause(button)
        else:
            self.play(button)

    def play(self, button):
        button.setText(PAUSE_STRING)
        self.window().play()

    def pause(self, button):
        button.setText(PLAY_STRING)
        self.window().pause()

    def next(self):
        self.pause(self.playPauseButton)
        self.window().next()

    def nextSec(self):
        self.pause(self.playPauseButton)
        self.window().nextSec()
