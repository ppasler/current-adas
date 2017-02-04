#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 08.12.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

import os
import logging
from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar

import matplotlib.pyplot as plt
from posdbos.util.file_util import FileUtil

scriptPath = os.path.dirname(os.path.abspath(__file__))

class DataWidget(QtGui.QWidget):

    def __init__(self, dataUrls, maxFps):
        super(DataWidget, self).__init__()
        self.fileUtil = FileUtil()

        self._initData(dataUrls[0])
        self.maxFps = maxFps
        self.curSecond = 0
        self._initPlot()

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        self.setObjectName("datawidget")

    def _initData(self, filePath):
        if self.fileUtil.isCSVFile(filePath):
            dto = self.fileUtil.getDtoFromCsv(filePath)
        else:
            dto = self.fileUtil.getDtoFromFif(filePath)

        self.eegHeader = dto.getEEGHeader()
        self.eegData = dto.getEEGData()
        self.numChannels = len(self.eegData)
        self.samplingRate = dto.getSamplingRate()
        self.length = len(self.eegData[0])
        logging.info("plotter\t#%d\t%.2fHz" % (self.length, self.samplingRate))

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
            data = self.eegData[i]
            line, = ax.plot(x_values, data[start:end], '-')
            self.lines.append(line)

            ax.set_xlim([start,end])
            ax.set_ylim([min(data), max(data)])
            ax.set_ylabel(self.eegHeader[i])

    def show(self, curSecond):
        if self._isReplot(curSecond):
            self.plot()

    def plot(self):
        start, end = self._getRange()
        if self._isInDataRange(start, end):
            for i, line in enumerate(self.lines):
                line.set_ydata(self.eegData[i][start:end])
    
            self.canvas.draw()
        else:
            logging.warn("no data found for index range [%d:%d]" % (start, end))

    def _isInDataRange(self, start, end):
        return end < self.length

    def _getRange(self):
        start = int(self.curSecond * self.samplingRate)
        end = int(start + self.samplingRate)
        return start, end

    # TODO method does 2 things
    def _isReplot(self, curSecond):
        if curSecond != self.curSecond:
            self.curSecond = curSecond
            return True
        return False