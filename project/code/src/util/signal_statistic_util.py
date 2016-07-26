#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 30.05.2016

:author: Paul Pasler
:organization: Reutlingen University
'''
from collections import OrderedDict
from datetime import datetime
import multiprocessing
import os
import time

from config.config import ConfigProvider
import matplotlib.pyplot as plt
import seaborn as sns
from util.eeg_table_util import EEGTableFileUtil
from util.signal_util import SignalUtil


DIVIDER = "******************************\n\n"
TITLE = "Statistics for %s's EEG Signal"

SIGNALS_KEY = "signals"
GENERAL_KEY = "general"
RAW_KEY = "raw"
QUALITY_KEY = "quality"

TIME_FORMAT_STRING = "%Y-%m-%d %H:%M:%S"
DURATION_FORMAT_STRING = "%M:%S"

def getNewFileName(filePath, fileExtension, suffix=None):
    fileName, _ = os.path.splitext(filePath)
    if suffix:
        fileName += suffix
    return "%s.%s" % (fileName, fileExtension)

def saveAs(filePath, content):
    with open(filePath, 'w') as fileObj:
        fileObj.write(content)

class SignalStatisticUtil(object):
    '''
    class to show some statistical values for a channel
    '''

    def __init__(self, person, filePath, signals=None, plot=True, save=True):
        self.person = person
        self.filePath = filePath
        self._initStatsDict()
        self._readData()
        self._initSignals(signals)
        self.su = SignalUtil()
        self._initFields()
        self.plot = plot
        self.save = save
        self._initPlotter(person)

    def _initStatsDict(self):
        self.stats = OrderedDict()
        self.stats[GENERAL_KEY] = OrderedDict()
        self.stats[SIGNALS_KEY] = OrderedDict()

    def _readData(self):
        self.reader = EEGTableFileUtil()
        self.eegData = self.reader.readFile(self.filePath)

    def _initSignals(self, signals):
        if not signals:
            signals = ConfigProvider().getEmotivConfig().get("eegFields")
        self.signals = signals

    def _initFields(self):
        self.statFields = {
            "max":self.su.maximum, 
            "min":self.su.minimum, 
            "mean":self.su.mean, 
            "var":self.su.var, 
            "countZeros":self.su.countZeros}

    def _initPlotter(self, person):
        self.ssp = SignalStatisticPlotter(person, self.eegData, self.signals, self.filePath, True, self.plot, self.save)


    def main(self):
        self.plotDistribution()
        
        start = time.time()
        self.collect_stats()
        s = self.getSignalStatsString()
        print s
        print "calculation took %s" % (self._buildFormattedTime(time.time()-start, DURATION_FORMAT_STRING),)
        self.saveStats(s)

    def plotDistribution(self):
        target = self.ssp.plotDistribution
        plotThread = multiprocessing.Process(target=target)
        plotThread.start()

    def collect_stats(self):
        self.collectGeneralStats()
        for signal in self.signals:
            self.stats[SIGNALS_KEY][signal] = {}
            self.collectRawStats(signal)
            self.collectQualityStats(signal)

    def collectGeneralStats(self):
        self._addGeneralStatValue("file path", self.filePath)
        self._addGeneralStatValue("sampleRate", ("%f.2" % self.eegData.getSamplingRate()))
        self._addGeneralTimeStat("start time", "getStartTime", TIME_FORMAT_STRING)
        self._addGeneralTimeStat("end time", "getEndTime", TIME_FORMAT_STRING)
        self._addGeneralTimeStat("duration", "getDuration", DURATION_FORMAT_STRING)

    def _addGeneralTimeStat(self, name, method, formatString):
        time = getattr(self.eegData, method)()
        value = self._buildFormattedTime(time, formatString)
        self._addGeneralStatValue(name, value)

    def _buildFormattedTime(self, time, formatString):
        value = datetime.fromtimestamp(time).strftime(formatString)
        return value
    
    def _addGeneralStatValue(self, name, value):
        self.stats[GENERAL_KEY][name] = value

    def collectRawStats(self, signal):
        data = self.eegData.getColumn(signal)
        self._collectSignalStat(signal, RAW_KEY, data)

    def collectQualityStats(self, signal):
        data = self.eegData.getQuality(signal)
        self._collectSignalStat(signal, QUALITY_KEY, data)

    def _collectSignalStat(self, signal, category, data):
        self.stats[SIGNALS_KEY][signal][category] = OrderedDict()
        for field, method in self.statFields.iteritems():
            self._addSignalStat(signal, category, field, method, data, 0)

    def _addSignalStat(self, signal, category, name, method, raw, decPlace=2):
        value = ("%." + str(decPlace) + "f") % method(raw)
        self._addSignalStatValue(signal, category, name, value)

    def _addSignalStatValue(self, signal, category, name, value):
        self.stats[SIGNALS_KEY][signal][category][name] = value

    def getSignalStatsString(self):
        s = TITLE % (self.person)
        s += "\n"
        s += DIVIDER
        for key, value in self.stats[GENERAL_KEY].iteritems():
            s += "%s:\t%s\n" % (key, value)
        s += DIVIDER
        s += self._getSignalStatString()
        s += DIVIDER
        return s

    def _getSignalStatString(self):
        header = [SIGNALS_KEY] + self.statFields.keys() + [s + "_Q" for s in self.statFields.keys()]
        s = "\t".join(header) + "\n"
        for signal, values in self.stats[SIGNALS_KEY].iteritems():
            l = [signal]
            l.extend(self._printSignalStat(RAW_KEY, signal, values))
            l.extend(self._printSignalStat(QUALITY_KEY, signal, values))
            s += "\t".join([x for x in l]) + "\n"
        return s

    def _printSignalStat(self, category, signal, values):
        l = []
        for _, value in values[category].iteritems():
            l.append(value)
        return l
    
    def saveStats(self, content):
        filePath = getNewFileName(self.filePath, "txt", "_stats")
        saveAs(filePath, content)

class SignalStatisticPlotter(object):

    def __init__(self, person, eegData, signals, filePath, logScale=False, plot=True, save=True):
        self.title = TITLE % person
        self.eegData = eegData
        self.signals = signals
        self.logScale = logScale
        self.plot = plot
        self.save = save
        self.figsize = (24, 12)
        if not self.plot:
            self.figsize = (96, 48)
        self.filePath = filePath

    def plotDistribution(self):
        if not self.plot and not self.save:
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
    scriptPath = os.path.dirname(os.path.abspath(__file__))
    person = "janis"
    fileName = "2016-07-12-11-15_EEG.csv"
    filePath = scriptPath + "/../../../captured_data/" + person + "/" + fileName

    s = SignalStatisticUtil(person, filePath, signals=["F3"], plot=False, save=False)
    s.main()