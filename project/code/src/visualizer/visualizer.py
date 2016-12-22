#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 07.12.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

import sys

from PyQt4 import QtGui, QtCore

from visualizer_ui import Ui_MainWindow
from video_player import VideoPlayer, VideoWidget
from data_plotter import DataWidget
from control import ControlPanelWidget

class DataVisualizerWidget(QtGui.QWidget):
    def __init__(self, videoWidget, dataWidget, controlWidget):
        super(DataVisualizerWidget, self).__init__()

        self.mainLayout = QtGui.QVBoxLayout(self)
        self.mainLayout.addWidget(videoWidget, 10)
        self.mainLayout.addWidget(dataWidget, 10)
        self.mainLayout.addWidget(controlWidget, 1)

        self.setObjectName("mainwidget")

class DataVisualizer(QtGui.QMainWindow):
    def __init__(self, parent, videoUrls, dataUrls, interval=32):
        super(DataVisualizer, self).__init__()
        self.interval = interval

        self._initPlotter(dataUrls)
        self._initPlayer(videoUrls)
        self._initControlPanel()
        self.wrapper = DataVisualizerWidget(self.videoWidget, self.plotter, self.controlPanel)

        self._initUI()
        self._initTimer()
        self.play()
        self.update()

        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Background,QtCore.Qt.white)
        self.setPalette(palette)

        self.setObjectName("mainwindow")

    def _initPlotter(self, dataUrls):
        self.plotter = DataWidget(dataUrls)
        self.plotter.plot()

    def _initPlayer(self, videoUrls):
        self.videoWidget = VideoWidget()
        self.videoPlayers = []
        for videoUrl in videoUrls:
            self.videoPlayers.append(VideoPlayer(self, videoUrl))
        self.videoWidget.setPlayers(self.videoPlayers)

    def _initControlPanel(self):
        self.controlPanel = ControlPanelWidget()

    def _initUI(self):
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self, self.wrapper)

    def _initTimer(self):
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.step)

    def step(self):
        for videoPlayer in self.videoPlayers:
            videoPlayer.play()
        self.plotter.next()

    def play(self):
        if not self._timer.isActive():
            self._timer.start(self.interval)

    def pause(self):
        if self._timer.isActive():
            self._timer.stop()

    def next(self):
        self.pause()
        self.step()

    def prev(self):
        self.pause()
        self.plotter.prev()

def main():
    app = QtGui.QApplication(sys.argv)
    videoUrls = ['E:/thesis/experiment/1/2016-12-05_14-25_drive.mp4', 'E:/thesis/experiment/1/2016-12-05_14-25_face.mp4']
    dataUrls = ['../../examples/example_4096.csv']
    #dataUrls = ['E:/thesis/experiment/1/2016-12-05_14-25_EEG.csv']
    vis = DataVisualizer(None, videoUrls, dataUrls)
    vis.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()