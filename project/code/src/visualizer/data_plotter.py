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
import numpy as np

scriptPath = os.path.dirname(os.path.abspath(__file__))

class DataWidget(QtGui.QWidget):
    def __init__(self, dataUrls):
        super(DataWidget, self).__init__()
        util = TableFileUtil()
        self.dto = util.readEEGFile(dataUrls[0])
        
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)

        self.eegHeader = self.dto.getEEGHeader()
        self.eegData = self.dto.getEEGData()
        self.numChannels = len(self.eegData)
        self.index = 0
        self.length = 128

        self.axes = []
        for i, _ in enumerate(self.eegData):
            self.axes.append(self.figure.add_subplot(self.numChannels, 1, i+1))

        self.setObjectName("datawidget")


    def plot(self):
        start = self.index
        end = self.index+self.length
        x_values = [x for x in range(start, end)]

        for i, ax in enumerate(self.axes):
            ax.hold(False)
            ax.plot(x_values, self.eegData[i][start:end], '-')
            ax.set_xlim([start,end])
            ax.set_ylabel(self.eegHeader[i])
        self.index += self.length
        # refresh canvas
        self.canvas.draw()