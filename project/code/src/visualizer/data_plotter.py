#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 08.12.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

import os
import random

from PyQt4 import QtGui
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar

import matplotlib.pyplot as plt
from util.signal_table_util import TableFileUtil


scriptPath = os.path.dirname(os.path.abspath(__file__))

class DataWidget(QtGui.QWidget):
    def __init__(self, dataUrls):
        super(DataWidget, self).__init__()
        util = TableFileUtil()
        self.dto = util.readEEGFile(dataUrls[0])
        
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def plot(self):
        ''' plot some random stuff '''
        eegHeader = self.dto.getEEGHeader()
        eegData = self.dto.getEEGData()
        
        channels = len(eegData)
        print channels
        axes = []
        for i, column in enumerate(eegData):
            axes.append(self.figure.add_subplot(channels, 1, i+1))

        for i, ax in enumerate(axes):
            ax.hold(False)
            ax.plot(eegData[i], '*-')
            ax.set_ylabel(eegHeader[i])
        # refresh canvas
        self.canvas.draw()