#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 02.08.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

from processor.eeg_processor import SignalProcessor, SignalPreProcessor
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from statistic.signal_statistic_constants import TITLE, getNewFileName
from util.eeg_util import EEGUtil
from util.quality_util import QualityUtil


SCREEN_SIZE = (24, 12)
FILE_SIZE = (96, 48)

FILE_TITLE = "(%s)"
PNG_EXTENSION = "png"


# TODO right extend syntax
class AbstractSignalPlotter(object):
    
    def __init__(self, name, person, eegData, signals, filePath, save=True, plot=True, logScale=False):
        self.title = TITLE % (name + " plot", person)
        self.eegData = eegData
        self.signals = signals
        self.logScale = logScale
        self.plot = plot
        self.save = save
        self.figsize = SCREEN_SIZE
        if not self.plot:
            self.figsize = FILE_SIZE
        self.filePath = filePath
        self.name = name

    def _shouldNotPlot(self):
        return not self.plot and not self.save

    def doPlot(self):
        pass

    def _calcSignalCount(self):
        signalCount = len(self.signals)
        if signalCount < 2:
            return 2
        return signalCount

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
            filePath = getNewFileName(self.filePath, PNG_EXTENSION, "_" + self.name)
            plt.savefig(filePath, bbox_inches='tight')


class DistributionSignalPlotter(AbstractSignalPlotter):

    def __init__(self, person, eegData, signals, filePath, save=True, plot=True, logScale=False):
        AbstractSignalPlotter.__init__(self, "distribution", person, eegData, signals, filePath, save, plot, logScale)
        self.preProcessor = SignalPreProcessor()

    def doPlot(self):
        if self._shouldNotPlot():
            return

        fig, axes = self._initPlot()
        fig.canvas.set_window_title(self.title)

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

    def _plotSignal(self, signal, axes, x):
        raw = self.eegData.getColumn(signal)
        proc = self.preProcessor.process(raw)
        quality = self.eegData.getQuality(signal)

        rawAx = axes[0, x]
        rawAx.xaxis.set_label_position("top")
        if self.logScale:
            rawAx.set_yscale("log")
        # rug=True causes serious performance issues
        sns.distplot(proc, color="b", axlabel=signal, ax=rawAx, bins=30, kde=False)

        qualAx = axes[1, x]
        sns.distplot(quality, color="g", ax=qualAx, bins=15, kde=False)


class RawSignalPlotter(AbstractSignalPlotter):

    def __init__(self, person, eegData, signals, filePath, save=True, plot=True, logScale=False, name="raw"):
        AbstractSignalPlotter.__init__(self, name, person, eegData, signals, filePath, save, plot, logScale)

    def doPlot(self):
        if self._shouldNotPlot():
            return

        fig, axes = self._initPlot()
        fig.canvas.set_window_title(self.title)

        samplingRate = self.eegData.getSamplingRate()
        valueCount = self.eegData.getValueCount()
        timeArray = self._getTimeArray(valueCount, samplingRate)

        for i, signal in enumerate(self.signals):
            self._plotSignal(signal, axes[i], timeArray)

        self._configurePlot()

        self.savePlot()
        self.showPlot()
        print "plotting done"

    def _initPlot(self):
        signalCount = self._calcSignalCount()

        fig, axes = plt.subplots(signalCount, figsize=self.figsize, dpi=80, sharex=True, sharey=False)
        return fig, axes

    def _getData(self, signal):
        return self.eegData.getColumn(signal)

    def _plotSignal(self, signal, axis, timeArray):
        raw = self._getData(signal)

        axis.yaxis.set_label_position("right")
        axis.set_ylabel(signal)

        if self.logScale:
            axis.set_yscale("log")
        axis.plot(timeArray, raw)

    def _getTimeArray(self, n, samplingRate):
        timeArray = np.arange(0, n, 1)
        timeArray = (timeArray / samplingRate) * 1000
        return timeArray

class AlphaSignalPlotter(RawSignalPlotter):
    def __init__(self, person, eegData, signals, filePath, save=True, plot=True, logScale=False):
        RawSignalPlotter.__init__(self, person, eegData, signals, filePath, save, plot, logScale, name="alpha")
        self.chain = SignalProcessor()
        self.eegUtil = EEGUtil()

    def _getData(self, signal):
        raw = self.eegData.getColumn(signal)
        qual = self.eegData.getQuality(signal)
        samplingRate = self.eegData.getSamplingRate()

        proc, _ = self.chain.process(raw, qual)
        proc = QualityUtil().replaceNans(proc)
        return self.eegUtil.getAlphaWaves(proc, samplingRate)

class ThetaSignalPlotter(RawSignalPlotter):
    def __init__(self, person, eegData, signals, filePath, save=True, plot=True, logScale=False):
        RawSignalPlotter.__init__(self, person, eegData, signals, filePath, save, plot, logScale, name="theta")
        self.chain = SignalProcessor()
        self.eegUtil = EEGUtil()

    def _getData(self, signal):
        raw = self.eegData.getColumn(signal)
        qual = self.eegData.getQuality(signal)
        samplingRate = self.eegData.getSamplingRate()

        proc, _ = self.chain.process(raw, qual)
        proc = QualityUtil().replaceNans(proc)
        return self.eegUtil.getThetaWaves(proc, samplingRate)

class DeltaSignalPlotter(RawSignalPlotter):
    def __init__(self, person, eegData, signals, filePath, save=True, plot=True, logScale=False):
        RawSignalPlotter.__init__(self, person, eegData, signals, filePath, save, plot, logScale, name="delta")
        self.chain = SignalProcessor()
        self.eegUtil = EEGUtil()

    def _getData(self, signal):
        raw = self.eegData.getColumn(signal)
        qual = self.eegData.getQuality(signal)
        samplingRate = self.eegData.getSamplingRate()

        proc, _ = self.chain.process(raw, qual)
        proc = QualityUtil().replaceNans(proc)
        return self.eegUtil.getDeltaWaves(proc, samplingRate)

class ProcessedSignalPlotter(RawSignalPlotter):
    def __init__(self, person, eegData, signals, filePath, save=True, plot=True, logScale=False):
        RawSignalPlotter.__init__(self, person, eegData, signals, filePath, save, plot, logScale, name="processed")
        self.pre = SignalPreProcessor()
        self.chain = SignalProcessor()

    def _getData(self, signal):
        raw = self.eegData.getColumn(signal)
        qual = self.eegData.getQuality(signal)
        proc = self.pre.process(raw)
        proc, _ = self.chain.process(proc, qual)
        return proc

class FrequencyPlotter(RawSignalPlotter):
    def __init__(self, person, eegData, signals, filePath, stats, index, save=True, plot=True, logScale=False):
        RawSignalPlotter.__init__(self, person, eegData, signals, filePath, save, plot, logScale, name="processed")
        self.stats = stats
        self.index = str(index)

    def doPlot(self):
        if self._shouldNotPlot():
            return

        fig, axes = self._initPlot()
        fig.canvas.set_window_title(self.title)

        for i, signal in enumerate(self.signals):
            self._plotSignal(signal, axes[i])

        self._configurePlot()

        self.savePlot()
        self.showPlot()
        print "plotting done"

    def _plotSignal(self, signal, axis):
        raw = self._getData(signal)

        axis.yaxis.set_label_position("right")
        axis.set_ylabel(signal)

        if self.logScale:
            axis.set_yscale("log")
        axis.plot(raw)

    def _getData(self, signal):
        return self.stats[signal][self.index]