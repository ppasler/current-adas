#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 02.08.2016

:author: Paul Pasler
:organization: Reutlingen University
'''
import matplotlib.pyplot as plt
import seaborn as sns

from statistic.signal_statistic_contants import TITLE, getNewFileName

SCREEN_SIZE = (24, 12)
FILE_SIZE = (96, 48)

class AbstractSignalStatisticPlotter(object):
    
    def __init__(self, person, eegData, signals, filePath, save=True, plot=True, logScale=False):
        self.title = TITLE % person
        self.eegData = eegData
        self.signals = signals
        self.logScale = logScale
        self.plot = plot
        self.save = save
        self.figsize = SCREEN_SIZE
        if not self.plot:
            self.figsize = FILE_SIZE
        self.filePath = filePath

    def _shouldNotPlot(self):
        return not self.plot and not self.save

    def plot(self):
        pass

    def _initPlot(self):
        signalCount = self._calcSignalCount()

        fig, axes = plt.subplots(2, signalCount, figsize=self.figsize, dpi=80, sharex=False, sharey=True)
        return fig, axes

    def _calcSignalCount(self):
        signalCount = len(self.signals)
        if signalCount < 2:
            return 2
        return signalCount

    def _plotSignal(self, signal, axes, x):
        raw = self.eegData.getColumn(signal)
        quality = self.eegData.getQuality(signal)

        rawAx = axes[0, x]
        rawAx.xaxis.set_label_position("top")
        if self.logScale:
            rawAx.set_yscale("log")
        # rug=True causes serious performance issues
        sns.distplot(raw, color="b", axlabel=signal, ax=rawAx, bins=30, kde=False)

        qualAx = axes[1, x]
        sns.distplot(quality, color="g", ax=qualAx, bins=15, kde=False)

    def _configurePlot(self):
        mng = plt.get_current_fig_manager()
        mng.window.wm_geometry("+0+0")
        plt.tight_layout()
        plt.subplots_adjust(wspace=0.1, hspace=0.1)

    def showPlot(self):
        if self.plot:
            plt.show()

    def savePlot(self):
        if self.save:
            filePath = getNewFileName(self.filePath, "png", "_stats")
            plt.savefig(filePath, bbox_inches='tight')


class DistributionSignalStatisticPlotter(AbstractSignalStatisticPlotter):

    def __init__(self, person, eegData, signals, filePath, save=True, plot=True, logScale=False):
        AbstractSignalStatisticPlotter.__init__(self, person, eegData, signals, filePath, save, plot, logScale)

    def plot(self):
        if self._shouldNotPlot():
            return

        _, axes = self._initPlot()

        for x, signal in enumerate(self.signals):
            self._plotSignal(signal, axes, x)

        self._configurePlot()

        self.savePlot()
        self.showPlot()
        print "plotting done"

    def _initPlot(self):
        signalCount = self._calcSignalCount()

        fig, axes = plt.subplots(2, signalCount, figsize=self.figsize, dpi=80, sharex=False, sharey=True)
        return fig, axes

    def _calcSignalCount(self):
        signalCount = len(self.signals)
        if signalCount < 2:
            return 2
        return signalCount

    def _plotSignal(self, signal, axes, x):
        raw = self.eegData.getColumn(signal)
        quality = self.eegData.getQuality(signal)

        rawAx = axes[0, x]
        rawAx.xaxis.set_label_position("top")
        if self.logScale:
            rawAx.set_yscale("log")
        # rug=True causes serious performance issues
        sns.distplot(raw, color="b", axlabel=signal, ax=rawAx, bins=30, kde=False)

        qualAx = axes[1, x]
        sns.distplot(quality, color="g", ax=qualAx, bins=15, kde=False)

    def _configurePlot(self):
        mng = plt.get_current_fig_manager()
        mng.window.wm_geometry("+0+0")
        plt.tight_layout()
        plt.subplots_adjust(wspace=0.1, hspace=0.1)

class RawSignalStatisticPlotter(AbstractSignalStatisticPlotter):

    def __init__(self, person, eegData, signals, filePath, save=True, plot=True, logScale=False):
        AbstractSignalStatisticPlotter.__init__(self, person, eegData, signals, filePath, save, plot, logScale)

    def plot(self):
        if self._shouldNotPlot():
            return

        _, axes = self._initPlot()

        for x, signal in enumerate(self.signals):
            self._plotSignal(signal, axes, x)

        self._configurePlot()

        self.savePlot()
        self.showPlot()
        print "plotting done"

    def _initPlot(self):
        signalCount = self._calcSignalCount()

        fig, axes = plt.subplots(2, signalCount, figsize=self.figsize, dpi=80, sharex=False, sharey=True)
        return fig, axes

    def _calcSignalCount(self):
        signalCount = len(self.signals)
        if signalCount < 2:
            return 2
        return signalCount

    def _plotSignal(self, signal, axes, x):
        raw = self.eegData.getColumn(signal)
        quality = self.eegData.getQuality(signal)

        rawAx = axes[0, x]
        rawAx.xaxis.set_label_position("top")
        if self.logScale:
            rawAx.set_yscale("log")
        # rug=True causes serious performance issues
        sns.distplot(raw, color="b", axlabel=signal, ax=rawAx, bins=30, kde=False)

        qualAx = axes[1, x]
        sns.distplot(quality, color="g", ax=qualAx, bins=15, kde=False)

    def _configurePlot(self):
        mng = plt.get_current_fig_manager()
        mng.window.wm_geometry("+0+0")
        plt.tight_layout()
        plt.subplots_adjust(wspace=0.1, hspace=0.1)

    def showPlot(self):
        if self.plot:
            plt.show()

    def savePlot(self):
        if self.save:
            filePath = getNewFileName(self.filePath, "png", "_stats")
            plt.savefig(filePath, bbox_inches='tight')

if __name__ == "__main__":
    DistributionSignalStatisticPlotter()