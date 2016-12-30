#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 07.12.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

import sys

from PyQt4 import QtGui, QtCore

from control import ControlPanelWidget
from data_plotter import DataWidget
from video_player import VideoPlayer, VideoWidget
from info import InfoPanelWidget
from visualizer_ui import Ui_MainWindow


class DataVisualizerWidget(QtGui.QWidget):
    def __init__(self, videoWidget, dataWidget, infoPanel, controlWidget):
        super(DataVisualizerWidget, self).__init__()

        self.mainLayout = QtGui.QVBoxLayout(self)
        self.mainLayout.addWidget(videoWidget, 10)
        self.mainLayout.addWidget(dataWidget, 10)
        self.mainLayout.addWidget(infoPanel, 1)
        self.mainLayout.addWidget(controlWidget, 1)

        self.setObjectName("mainwidget")

class DataVisualizer(QtGui.QMainWindow):
    def __init__(self, parent, videoUrls, dataUrls, interval=32):
        super(DataVisualizer, self).__init__()
        self.interval = interval
        self.direction = 1
        self.curFrame = 0

        self._initPlayer(videoUrls)
        self._initPlotter(dataUrls)
        self._initControlPanel()
        self._initInfoPanel()
        self.wrapper = DataVisualizerWidget(self.videoWidget, self.plotter, self.infoPanel, self.controlPanel)

        self._initUI()
        self._initTimer()
        self.play()
        self.update()

        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background,QtCore.Qt.white)
        self.setPalette(palette)

        self.setObjectName("mainwindow")

    def _initPlotter(self, dataUrls):
        self.plotter = DataWidget(dataUrls, self.maxFps)

    def _initPlayer(self, videoUrls):
        self.videoWidget = VideoWidget()
        self.videoPlayers = []
        self.maxFps = 0
        self.maxFrameCount = 0
        for playerId, videoUrl in enumerate(videoUrls):
            videoPlayer = VideoPlayer(self, playerId, videoUrl)
            self.maxFps = max(self.maxFps, videoPlayer.fps)
            self.maxFrameCount = max(self.maxFrameCount, videoPlayer.frameCount)
            self.videoPlayers.append(videoPlayer)
        self.videoWidget.setPlayers(self.videoPlayers)

    def _initControlPanel(self):
        self.controlPanel = ControlPanelWidget(self.maxFrameCount)

    def _initInfoPanel(self):
        self.infoPanel = InfoPanelWidget(self.maxFps, self.curFrame)

    def _initUI(self):
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self, self.wrapper)

    def _initTimer(self):
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.step)

    def step(self):
        self.addFrame(self.direction)
        self.update()

    def stepSec(self):
        self.addFrame(self.direction * round(self.maxFps))
        self.update()

    def update(self):
        for videoPlayer in self.videoPlayers:
            videoPlayer.show(self.curFrame)
        self.plotter.next(self.curFrame)
        self.infoPanel.update(self.curFrame)
        self.controlPanel.slider.setValue(self.curFrame)

    def play(self):
        if not self._timer.isActive():
            self._timer.start(self.interval)

    def pause(self):
        if self._timer.isActive():
            self._timer.stop()

    def next(self):
        self.direction = 1
        self.step()

    def nextSec(self):
        self.direction = 1
        self.stepSec()

    def prev(self):
        self.direction = -1
        self.step()

    def prevSec(self):
        self.direction = -1
        self.stepSec()

    def addFrame(self, addFrame):
        newFrame = self.curFrame + addFrame
        if 0 <= newFrame <= self.maxFrameCount:
            self.curFrame = newFrame

    def setCurFrame(self, newFrame):
        if 0 <= newFrame <= self.maxFrameCount:
            self.curFrame = newFrame
            self.update()

def main():
    app = QtGui.QApplication(sys.argv)
    expPath = "E:/thesis/experiment/"
    probands = ["1/2016-12-05_14-25", "2/2016-12-01_17-50", "3/2016-12-20_14-11-18", "test/blink"]
    files = ["_drive.mp4", "_face.mp4", "_EEG.csv"]
    #dataUrls = ['../../examples/example_4096.csv']

    url = expPath + probands[3]
    videoUrls = [url+files[0], url+files[1]]
    dataUrls = [url+files[2]]

    vis = DataVisualizer(None, videoUrls, dataUrls)
    vis.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()