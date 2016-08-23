#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 02.07.2016

:author: Paul Pasler
:organization: Reutlingen University
'''
from datetime import datetime
import multiprocessing
import sys

from numpy import nanmax, nanmin, nansum, nanmean

from config.config import ConfigProvider
from eeg_processor import SignalPreProcessor, SignalProcessor
from signal_statistic_printer import SignalStatisticPrinter
from statistic.signal_statistic_constants import *  # @UnusedWildImport
from statistic.signal_statistic_plotter import RawSignalPlotter, DeltaSignalPlotter, ThetaSignalPlotter, AlphaSignalPlotter, ProcessedSignalPlotter, DistributionSignalPlotter
from util.eeg_table_util import EEGTableFileUtil
from util.eeg_util import EEGUtil
from util.quality_util import QualityUtil
from util.signal_util import SignalUtil


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
scriptPath = os.path.dirname(os.path.abspath(__file__))

PLOTTER = [ProcessedSignalPlotter]

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
        self.eu = EEGUtil()
        self._initFields()
        self.save = save
        self._initPlotter(person, plot, logScale)
        self.ssPrint = SignalStatisticPrinter(person)
        self.preProcessor = SignalPreProcessor()
        self.processor = SignalProcessor()
        self.windowSize = ConfigProvider().getCollectorConfig().get("windowSize")

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
        self.statFields = STAT_FIELDS
        self.statFields["max"][METHOD] = self.su.maximum 
        self.statFields["min"][METHOD] = self.su.minimum
        self.statFields["mean"][METHOD] = self.su.mean
        self.statFields["std"][METHOD] = self.su.std
        self.statFields["var"][METHOD] = self.su.var
        self.statFields["zeros"][METHOD] = self.qu.countZeros
        self.statFields["seq"][METHOD] = self.qu.countSequences
        self.statFields["out"][METHOD] = self.qu.countOutliners
        self.statFields["nrgy"][METHOD] = self.su.energy
        self.statFields["zcr"][METHOD] = self.su.zcr

    def _initPlotter(self, person, plot, logScale):
        self.plotter = []
        for clazz in PLOTTER:
            plotter = clazz(person, self.eegData, self.signals, self.filePath, self.save, plot, logScale)
            thread = multiprocessing.Process(target=plotter.doPlot)
            self.plotter.append(thread)


    def main(self):
        self.doPlot()

        self.collect_stats()
        self.printStats()

    def doPlot(self):
        for thread in self.plotter:
            thread.start()

    def collect_stats(self):
        self.collectGeneralStats()
        for signal in self.signals:
            self.stats[SIGNALS_KEY][signal] = {}
            self.collectRawStats(signal)

    def collectGeneralStats(self):
        self._addGeneralStatValue("file path", self.filePath)
        self._addGeneralStatValue("sampleRate", ("%f.2" % self.eegData.getSamplingRate()))
        self._addGeneralStatValue("dataLength", ("%d" % self.eegData.len))
        self._addGeneralStatValue("bound", ("%d - %d" % (self.qu.lowerBound, self.qu.upperBound)))

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

    def _collectSignalStat(self, signal, category, data):
        self.stats[SIGNALS_KEY][signal][category] = OrderedDict()
        for field, attributes in self.statFields.iteritems():
            fieldValues = []
            for window in self.getWindows(data):
                fieldValues.append(self._getSignalStat(signal, category, field, attributes["method"], window, 0))
            merged = self._mergeValues(fieldValues, field)
            self._addSignalStatValue(signal, category, field, merged)

    def getWindows(self, raw):
        windows = []
        for start in range(0, len(raw), self.windowSize / 2):
            end = start + self.windowSize
            if end <= len(raw):
                windows.append(raw[start:end])
        return windows

    def _getSignalStat(self, signal, category, name, method, raw, decPlace=2):
        return method(raw)

    def _addSignalStatValue(self, signal, category, name, value):
        self.stats[SIGNALS_KEY][signal][category][name] = value

    def _mergeValues(self, values, field):
        typ = self.statFields[field][TYPE]

        if typ == MAX_TYPE:
            return nanmax(values)
        if typ == MIN_TYPE:
            return nanmin(values)
        if typ == AGGREGATION_TYPE:
            return nansum(values)
        if typ == MEAN_TYPE:
            return nanmean(values)
        if typ == DIFF_TYPE:
            return nanmean(values)

    def setStats(self, stats):
        self.stats = stats

    def printStats(self):
        content = self.ssPrint.getSignalStatsString(self.stats)
        print content
        if self.save:
            filePath = getNewFileName(self.filePath, "txt", "_stats")
            self.ssPrint.saveStats(filePath, content)


class SignalStatisticCollector(object):
    
    def __init__(self, experimentDir, experiments=None, signals=None, save=False, plot=False, logScale=False):
        self.experimentDir = experimentDir
        self.experiments = experiments
        self.signals = signals
        self.save = save
        self.plot = plot
        self.logScale = logScale
        self.experimentDir = experimentDir
        if experiments is None:
            self.experiments = ConfigProvider().getExperimentConfig()
        else:
            self.experiments = experiments
        self.stats = []
        self.merge = {}
        self.ssPrint = SignalStatisticPrinter("merge")
        self.dataLen = 0
    
    def main(self):
        for person, fileNames in self.experiments.iteritems():
            for fileName in fileNames:
                filePath =  "%s%s/%s" % (self.experimentDir, person, fileName)
                s = SignalStatisticUtil(person, filePath, signals=self.signals, save=self.save, plot=self.plot, logScale=self.logScale)
                self.dataLen += s.eegData.len
                s.main()
                self.stats.append(s.stats)
        if len(self.stats) > 1:
            self._addCollections()
            self.printCollection()
        else:
            print "did not merge 1 stat"

    def _addCollections(self):
        '''[signals][channel][signal][type]'''
        self.merge = self.stats[0][SIGNALS_KEY]
        for stat in self.stats[1:]:
            self._addChannels(stat[SIGNALS_KEY])

        self._mergeChannels(len(self.stats), self.merge)

    def _addChannels(self, channels):
        for channel, value in channels.iteritems():
            self._addValues(channel, value)

    def _addValues(self, channel, dic):
        for key, field in STAT_FIELDS.iteritems():
            typ = field["type"]
            self._addValue(dic, typ, channel, RAW_KEY, key)

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
        if typ == DIFF_TYPE:
            return old-new

    def _mergeChannels(self, count, channels):
        for channel, value in channels.iteritems():
            self._mergeValues(count, channel, value)

    def _mergeValues(self, count, channel, dic):
        for key, field in STAT_FIELDS.iteritems():
            typ = field["type"]
            self._mergeValue(dic, typ, count, channel, RAW_KEY, key)

    def _mergeValue(self, dic, typ, count, channel, signal, key):
        self.merge[channel][signal][key] = self._mergeByType(typ, self.merge[channel][signal][key], count)

    def _mergeByType(self, typ, value, count):
        if typ in [MAX_TYPE, MIN_TYPE, AGGREGATION_TYPE, DIFF_TYPE]:
            return str(value)
        if typ == MEAN_TYPE:
            return str(value / float(count))

    def printCollection(self):
        general = {"dataLength": str(self.dataLen)}
        stats = {SIGNALS_KEY: self.merge, GENERAL_KEY: general}
        content = self.ssPrint.getSignalStatsString(stats)
        print content
        filePath = experimentDir + "merge.txt"
        self.ssPrint.saveStats(filePath, content) 

def rawDataStatisticSingle():
    experimentDir = scriptPath + "/../../../captured_data/"
    experiments = {
        #"janis/parts": ["2016-07-12-11-15_EEG_2.csv", "2016-07-12-11-15_EEG_7.csv"]
        #"nati/parts": ["2016-07-13-14-38_EEG_2.csv", "2016-07-13-14-38_EEG_7.csv"]
        #"gregor/parts": ["2016-07-12-13-45_EEG_2.csv", "2016-07-12-13-45_EEG_5.csv"]
        #"gerald/parts": ["2016-07-12-10-00_EEG_2.csv", "2016-07-12-10-00_EEG_5.csv"]
        #"test_data": ["awake_1.csv", "awake_2.csv", "awake_3.csv"]
        #"test_data": ["drowsy_1.csv", "drowsy_2.csv", "drowsy_3.csv"]
        #"test_data": ["awake_4_bad.csv", "drowsy_4_bad.csv"]
        "test_data": ["drowsy_full.csv", "awake_full.csv"]
    }
    return experimentDir, experiments

def rawDataStatisticAll():
    experimentDir = scriptPath + "/../../../captured_data/"
    experiments = None
    return experimentDir, experiments

if __name__ == "__main__":
    experimentDir, experiments = rawDataStatisticSingle()
    s = SignalStatisticCollector(experimentDir, experiments, plot=True, save=False)
    s.main()

