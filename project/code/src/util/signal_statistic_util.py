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
from util.quality_util import QualityUtil
from util.signal_util import SignalUtil


DIVIDER = "******************************\n\n"
TITLE = "Statistics for %s's EEG Signal"

SIGNALS_KEY = "signals"
GENERAL_KEY = "general"
RAW_KEY = "raw"
QUALITY_KEY = "quality"

TIME_FORMAT_STRING = "%Y-%m-%d %H:%M:%S"
DURATION_FORMAT_STRING = "%M:%S"

MAX_TYPE = "max"
MIN_TYPE = "min"
MEAN_TYPE = "mean"
AGGREGATION_TYPE = "aggregation"

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

    def __init__(self, person, filePath, signals=None, save=True, plot=True, logScale=False):
        self.person = person
        self.filePath = filePath
        self._initStatsDict()
        self._readData()
        self._initSignals(signals)
        self.su = SignalUtil()
        self.qu = QualityUtil()
        self._initFields()
        self.save = save
        self._initPlotter(person, plot, logScale)

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
            "max": self._initField(self.su.maximum, MAX_TYPE), 
            "min": self._initField(self.su.minimum, MIN_TYPE), 
            "mean": self._initField(self.su.mean, MEAN_TYPE),
            "var": self._initField(self.su.var, MEAN_TYPE),
            "zeros": self._initField(self.qu.countZeros, AGGREGATION_TYPE),
            "seq": self._initField(self.qu.countSequences, AGGREGATION_TYPE)
        }

    def _initField(self, method, typ):
        return {"type": typ,
                 "method": method}

    def _initPlotter(self, person, plot, logScale):
        self.ssp = SignalStatisticPlotter(person, self.eegData, self.signals, self.filePath, self.save, plot, logScale)


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
        for field, attributes in self.statFields.iteritems():
            self._addSignalStat(signal, category, field, attributes["method"], data, 0)

    def _addSignalStat(self, signal, category, name, method, raw, decPlace=2):
        value = ("%." + str(decPlace) + "f") % method(raw)
        self._addSignalStatValue(signal, category, name, value)

    def _addSignalStatValue(self, signal, category, name, value):
        self.stats[SIGNALS_KEY][signal][category][name] = value

    def setStats(self, stats):
        self.stats = stats

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

    def __init__(self, person, eegData, signals, filePath, save=True, plot=True, logScale=False):
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

class SignalStatisticCollector(object):
    
    def __init__(self, experimentDir, experiments=None):
        self.experimentDir = experimentDir
        if experiments is None:
            self.experiments = ConfigProvider().getExperimentConfig()
        else:
            self.experiments = experiments
        self.stats = []
        self.merge = {}
        self.statUtil = SignalStatisticUtil("MERGE", "")
    
    def main(self):
        for person, fileNames in self.experiments.iteritems():
            for fileName in fileNames:
                filePath =  "%s%s/%s" % (self.experimentDir, person, fileName)
                s = SignalStatisticUtil(person, filePath, save=False, plot=False, logScale=False)
                s.main()
                self.stats.append(s.stats)
        self._addCollections()

    def _addCollections(self):
        '''[signals][channel][signal][type]'''
        self.merge = self.stats[0][SIGNALS_KEY]
        for stat in self.stats[1:]:
            self._addChannels(stat[SIGNALS_KEY])
            
        self._mergeChannels(len(self.stats), self.merge)
        self.printCollection()

    def _addChannels(self, channels):
        for channel, value in channels.iteritems():
            self._addValues(channel, value)

    def _addValues(self, channel, dic):
        for key, field in self.statUtil.statFields.iteritems():
            typ = field["type"]
            self._addValue(dic, typ, channel, RAW_KEY, key)
            self._addValue(dic, typ, channel, QUALITY_KEY, key)

    def _addValue(self, dic, typ, channel, signal, key):
        old = float(self.merge[channel][signal][key])
        new = float(dic[signal][key])
        self.merge[channel][signal][key] = self._getByType(typ, old, new)

    def _getByType(self, typ, old, new):
        if typ == MAX_TYPE:
            return new if new > old else old
        if typ == MIN_TYPE:
            return new if new < old else old
        if typ in [AGGREGATION_TYPE, MEAN_TYPE]:
            return new + old

    def _mergeChannels(self, count, channels):
        for channel, value in channels.iteritems():
            self._mergeValues(count, channel, value)

    def _mergeValues(self, count, channel, dic):
        for key, field in self.statUtil.statFields.iteritems():
            typ = field["type"]
            self._mergeValue(dic, typ, count, channel, RAW_KEY, key)
            self._mergeValue(dic, typ, count, channel, QUALITY_KEY, key)

    def _mergeValue(self, dic, typ, count, channel, signal, key):
        self.merge[channel][signal][key] = self._mergeByType(typ, self.merge[channel][signal][key], count)

    def _mergeByType(self, typ, value, count):
        if typ in [MAX_TYPE, MIN_TYPE, AGGREGATION_TYPE]:
            return str(value)
        if typ == MEAN_TYPE:
            return str(value / float(count))

    def printCollection(self):
        self.statUtil.setStats({"signals": self.merge, "general":{}})
        s = self.statUtil.getSignalStatsString()
        print s
        saveAs(self.experimentDir + "merged_signal.txt", s)

if __name__ == "__main__":
    scriptPath = os.path.dirname(os.path.abspath(__file__))
    experimentDir = scriptPath + "/../../../captured_data/"
    smallData = {
        "janis": ["2016-07-12-11-15_EEG_1.csv", "2016-07-12-11-15_EEG_2.csv"]
    }
    s = SignalStatisticCollector(experimentDir)
    s.main()

