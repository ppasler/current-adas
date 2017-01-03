#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 07.12.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

import sys
from math import ceil

from PyQt4 import QtGui, QtCore

from config.config import ConfigProvider
from control import ControlPanelWidget
from data_plotter import DataWidget
from video_player import VideoPlayer, VideoWidget
from visualizer_ui import Ui_MainWindow


class TopWrapper(QtGui.QWidget):
    def __init__(self, videoWidget, dataWidget):
        super(TopWrapper, self).__init__()
        self.mainLayout = QtGui.QHBoxLayout(self)
        self.mainLayout.addWidget(videoWidget, 2)
        self.mainLayout.addWidget(dataWidget, 3)

        self.setObjectName("topwrapperwidget")

class DataVisualizerWidget(QtGui.QWidget):
    def __init__(self, videoWidget, dataWidget, controlWidget):
        super(DataVisualizerWidget, self).__init__()

        topWrapper = TopWrapper(videoWidget, dataWidget)
        self.mainLayout = QtGui.QVBoxLayout(self)
        self.mainLayout.addWidget(topWrapper, 6)
        self.mainLayout.addWidget(controlWidget, 1)

        self.setObjectName("mainwidget")

class DataVisualizer(QtGui.QMainWindow):
    def __init__(self, parent, videoUrls, dataUrls, interval=32):
        super(DataVisualizer, self).__init__()
        self.interval = interval
        self.direction = 1
        self.curFrame = 0
        self.curSecond = 0
        self.maxFps = 0
        self.maxFrameCount = 0

        self._initWrapper(videoUrls, dataUrls)

        self._initUI()
        self._initTimer()
        self.play()
        self.update()

        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background,QtCore.Qt.white)
        self.setPalette(palette)

        self.setObjectName("mainwindow")

    def _initWrapper(self, videoUrls, dataUrls):
        self._initPlayer(videoUrls)
        self._initPlotter(dataUrls)
        self._initControlPanel()
        self.wrapper = DataVisualizerWidget(self.videoWidget, self.plotter, self.controlPanel)

    def _initPlotter(self, dataUrls):
        self.plotter = DataWidget(dataUrls, self.maxFps)

    def _initPlayer(self, videoUrls):
        self.videoPlayers = []
        for playerId, videoUrl in enumerate(videoUrls):
            videoPlayer = VideoPlayer(playerId, videoUrl)
            self.maxFps = max(self.maxFps, videoPlayer.fps)
            self.maxFrameCount = max(self.maxFrameCount, videoPlayer.frameCount)
            self.videoPlayers.append(videoPlayer)
        self.videoWidget = VideoWidget(self.videoPlayers)
        for videoPlayer in self.videoPlayers:
            videoPlayer.setMaxFps(self.maxFps)

    def _initControlPanel(self):
        self.controlPanel = ControlPanelWidget(self.maxFrameCount, self.maxFps)

    def _initUI(self):
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self, self.wrapper)

    def _initTimer(self):
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.step)


    def step(self):
        self._addFrame(self.direction)

    def _addFrame(self, addFrame):
        newFrame = self.curFrame + addFrame
        self.setCurFrame(newFrame)

    def stepSec(self):
        self.setCurFrame(self._calcNextFullSecondFrame())

    def setCurFrame(self, newFrame):
        newFrame = min(max(0, newFrame), self.maxFrameCount)
        if newFrame != self.curFrame:
            self.curFrame = newFrame
            self.curSecond = self._calcCurSecond()
            self.update()

    def update(self):
        for videoPlayer in self.videoPlayers:
            videoPlayer.show(self.curFrame)
        self.plotter.show(self.curSecond)
        self.controlPanel.update(self.curFrame, self.curSecond)


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


    def _calcCurSecond(self):
        return int(self.curFrame / self.maxFps)

    def _calcNextFullSecondFrame(self):
        return int(ceil((self.curSecond+self.direction) * self.maxFps))

def main():
    app = QtGui.QApplication(sys.argv)
    expPath = "E:/thesis/experiment/"
    probands = ConfigProvider().getExperimentConfig().get("probands")
    files = ["drive.mp4", "face.mp4", "EEG.raw.fif"]
    #dataUrls = ['../../examples/example_4096.csv']

    url = expPath + "Test/" #probands[1] + "/"
    videoUrls = [url+files[0], url+files[1]]
    dataUrls = [url+files[2]]

    vis = DataVisualizer(None, videoUrls, dataUrls)
    vis.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()