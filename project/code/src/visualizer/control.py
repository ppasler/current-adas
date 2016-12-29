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
PREV_STRING = "prev"
NEXT_STRING = "next"

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

        self._initPrev()
        self._initPlayPause()
        self._initNext()

        self.setObjectName("buttonpanel")

    def _initPrev(self):
        self.prevButton = QtGui.QPushButton(PREV_STRING, self)
        self.prevButton.clicked.connect(self.prev)
        self.mainLayout.addWidget(self.prevButton)

    def prev(self):
        # TODO
        self.window().prev()

    def _initPlayPause(self):
        self.playPauseButton = QtGui.QPushButton(PAUSE_STRING, self)
        self.playPauseButton.clicked.connect(self._handlePlayPause)
        self.mainLayout.addWidget(self.playPauseButton)

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

    def _initNext(self):
        self.nextButton = QtGui.QPushButton(NEXT_STRING, self)
        self.nextButton.clicked.connect(self.next)
        self.mainLayout.addWidget(self.nextButton)

    def next(self):
        self.pause(self.playPauseButton)
        self.window().next()
