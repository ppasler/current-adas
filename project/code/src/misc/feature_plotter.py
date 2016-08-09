'''
Created on 09.08.2016

@author: Paul Pasler
'''

import os

from config.config import ConfigProvider
import matplotlib.pyplot as plt
import numpy as np
from statistic.signal_statistic_plotter import AbstractSignalPlotter
from util.eeg_table_util import EEGTableFileUtil


scriptPath = os.path.dirname(os.path.abspath(__file__))


SCREEN_SIZE = (24, 12)

class FeaturePlotter(AbstractSignalPlotter):
    '''
    Plots feature vector
    '''
    def __init__(self, data, header, filePath):
        AbstractSignalPlotter.__init__(self, "featureset", "test", data, header, filePath, False, True, False)
        self.data = data
        self.figsize = SCREEN_SIZE
        
    def _configurePlot(self):
        mng = plt.get_current_fig_manager()
        mng.window.wm_geometry("+0+0")
        plt.tight_layout()
        plt.subplots_adjust(wspace=0.1, hspace=0.1)

    def doPlot(self):
        fig, axes = self._initPlot()
        fig.canvas.set_window_title(self.title)

        for i, signal in enumerate(self.signals):
            self._plotSignal(signal, self.data[:,i], axes[i])

        self._configurePlot()

        self.savePlot()
        self.showPlot()
        print "plotting done"

    def _initPlot(self):
        signalCount = self._calcSignalCount()

        fig, axes = plt.subplots(signalCount, figsize=self.figsize, dpi=80, sharex=True, sharey=False)
        return fig, axes

    def _plotSignal(self, header, data, axis):
        axis.yaxis.set_label_position("right")
        axis.set_ylabel(header)

        axis.plot(data)

if __name__ == '__main__': # pragma: no cover
    filePath = scriptPath + "/../../data/test.csv"
    fileUtil = EEGTableFileUtil()
    fp = FeaturePlotter(fileUtil.readData(filePath), fileUtil.readHeader(filePath), filePath)
    fp.doPlot()
