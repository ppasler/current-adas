#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 20.01.2017

:author: Paul Pasler
:organization: Reutlingen University
'''

from base_test import *  # @UnusedWildImport
from time import sleep
from helper.plotter.eeg_signal_plotter import EEGSignalPlotter
from helper.plotter.feature_plotter import FeaturePlotter
from helper.statistic.signal_statistic_util import SignalStatisticCollector
from helper.visualizer.visualizer import DataVisualizer
from PyQt4 import QtGui

class EEGSignalPlotterTest(BaseTest):

    def test_eegSignalPlotter(self):
        channels = ["X", "AF3"]
        fileName = "Test"
        dto = self.readData1024CSV()
        plotter = EEGSignalPlotter()
        plotter.plotFFTSignals(dto, channels, fileName)

        self.closePlots()

class FeaturePlotterTest(BaseTest):

    def test_featurePlotter(self):
        dto = self.readData1024CSV()
        fileName = "Test"
        fp = FeaturePlotter(dto.getData(), dto.getHeader(), fileName)
        fp.doPlot()

        self.closePlots()

class StatisticTest(BaseTest):

    def test_statistic(self):
        fileNames = ["test_data/example_1024.csv"]
        s = SignalStatisticCollector(fileNames=fileNames, plot=False, save=False, name="test")
        s.main()


class VisualizerTest(BaseTest):

    def test_visualizer(self):
        app = QtGui.QApplication(sys.argv)
    
        videoUrls, dataUrls = ["test_data/test.mp4", "test_data/test.mp4"], ["test_data/example_1024.csv"]
        #videoUrls, dataUrls = runTest(["blink.mp4"], "blink.csv")
    
        vis = DataVisualizer(None, videoUrls, dataUrls)
        # TODO how to close
        #vis.show()
        #sys.exit(app.exec_())

if __name__ == '__main__':
    unittest.main()