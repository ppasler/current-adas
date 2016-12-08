#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 07.12.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

import sys

from PyQt4 import QtGui, QtCore

from video_player import VideoPlayer, VideoWidget
from visualizer.data_plotter import DataWidget
from visualizer.data_visualizer_ui import Ui_MainWindow


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class DataVisualizerWidget(QtGui.QWidget):
    def __init__(self, videoWidget, dataWidget):
        super(DataVisualizerWidget, self).__init__()
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.addWidget(videoWidget)
        self.mainLayout.addWidget(dataWidget)

        self.setLayout(self.mainLayout)
        self.setObjectName(_fromUtf8("centralwidget"))

class DataVisualizer(QtGui.QMainWindow):
    def __init__(self, parent, videoUrls):
        super(DataVisualizer, self).__init__()

        self._initPlotter()
        self._initPlayer(videoUrls)
        self.wrapper = DataVisualizerWidget(self.videoWidget, self.plotter)

        self._initUI()
        self._initTimer()
        self.update()

    def _initPlotter(self):
        self.plotter = DataWidget()
        self.plotter.plot()

    def _initPlayer(self, videoUrls):
        self.videoPlayers = []
        for videoUrl in videoUrls:
            self.videoPlayers.append(VideoPlayer(self, videoUrl))
        self.videoWidget = VideoWidget(self.videoPlayers)

    def _initUI(self):
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self, self.wrapper)

    def _initTimer(self):
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.start)
        self._timer.start(32)

    def start(self):
        #self.plotter.plot()
        for videoPlayer in self.videoPlayers:
            videoPlayer.play()

def main():
    app = QtGui.QApplication(sys.argv)
    videoUrls = ['E:/thesis/experiment/1/2016-12-05_14-25_drive.mp4', 'E:/thesis/experiment/1/2016-12-05_14-25_face.mp4']
    vis = DataVisualizer(None, videoUrls)
    vis.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()