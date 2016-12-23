#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 08.12.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

import os

from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar

import matplotlib.pyplot as plt
from util.signal_table_util import TableFileUtil

scriptPath = os.path.dirname(os.path.abspath(__file__))

class DataWidget(QtGui.QWidget):

    def __init__(self, dataUrls):
        super(DataWidget, self).__init__()

        self._initData(dataUrls)
        self._initPlot()

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        self.setObjectName("datawidget")

    def _initData(self, dataUrls):
        util = TableFileUtil()
        self.dto = util.readEEGFile(dataUrls[0])

        self.eegHeader = self.dto.getEEGHeader()
        self.eegData = self.dto.getEEGData()
        self.numChannels = len(self.eegData)
        self.index = 0
        self.length = 128
        print "plotter\t#%d" % len(self.eegData[0])

    def _initPlot(self):
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        self.axes = []
        for i, _ in enumerate(self.eegData):
            self.axes.append(self.figure.add_subplot(self.numChannels, 1, i+1))

        start, end = self._getRange()
        x_values = [x for x in range(start, end)]

        self.lines = []
        for i, ax in enumerate(self.axes):
            line, = ax.plot(x_values, self.eegData[i][start:end], '-')
            self.lines.append(line)

            ax.set_xlim([start,end])
            ax.set_ylabel(self.eegHeader[i])
        self._incIndex()

    def next(self):
        self._incIndex()
        self.plot()

    def prev(self):
        self._decIndex()
        self.plot()

    def plot(self):
        start, end = self._getRange()

        for i, line in enumerate(self.lines):
            line.set_ydata(self.eegData[i][start:end])

        self.canvas.draw()

    def _incIndex(self):
        self.index += self.length

    def _decIndex(self):
        self.index -= self.length

    def _getRange(self):
        start = self.index
        end = self.index+self.length
        return start, end

