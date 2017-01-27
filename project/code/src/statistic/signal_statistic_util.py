#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 02.07.2016

:author: Paul Pasler
:organization: Reutlingen University
'''
from datetime import datetime
from multiprocessing import Process
from threading import Thread
from Queue import Queue
import sys
from statistic.signal_statistic_constants import *  # @UnusedWildImport
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from numpy import nanmax, nanmin, nansum, nanmean, array

from collector.data_collector import EEGDataCollector
from config.config import ConfigProvider
from processor.eeg_processor import SignalPreProcessor, SignalProcessor
from signal_statistic_printer import SignalStatisticPrinter
from statistic.signal_statistic_plotter import RawSignalPlotter, DeltaSignalPlotter, ThetaSignalPlotter, AlphaSignalPlotter, ProcessedSignalPlotter, DistributionSignalPlotter, \
    FrequencyPlotter
from util.eeg_util import EEGUtil
from util.fft_util import FFTUtil
from util.file_util import FileUtil
from util.quality_util import QualityUtil
from util.signal_util import SignalUtil



scriptPath = os.path.dirname(os.path.abspath(__file__))

PLOTTER = []

class SignalStatisticUtil(object):
    '''
    class to show some statistical values for a channel
    '''

    def __init__(self, queue, filePath, signals=None, save=True, plot=True, logScale=False, name=""):
        self.queue = queue
        self.filePath = filePath
        self._initStatsDict()
        self.eegData = FileUtil().getDto(filePath)
        self._initSignals(signals)
        self.su = SignalUtil()
        self.qu = QualityUtil()
        self.eu = EEGUtil()
        self.fft = FFTUtil()
        self._initFields()
        self.save = save
        self.plot = plot
        self.name = name + " " + str(filePath)
        self._initPlotter(logScale)
        self.ssPrint = SignalStatisticPrinter(filePath)
        self.preProcessor = SignalPreProcessor()
        self.processor = SignalProcessor()

        windowSeconds = ConfigProvider().getCollectorConfig().get("windowSeconds")
        self.windowSize = EEGDataCollector.calcWindowSize(windowSeconds, self.eegData.samplingRate)

    def _initStatsDict(self):
        self.stats = OrderedDict()
        self.stats[GENERAL_KEY] = OrderedDict()
        self.stats[SIGNALS_KEY] = OrderedDict()

    def _initFields(self):
        self.statFields = STAT_FIELDS
        addMethods(self)

    def _initSignals(self, signals):
        if not signals:
            signals = ConfigProvider().getEmotivConfig().get("eegFields")
        self.signals = signals

    def _initPlotter(self, logScale):
        self.plotter = []
        for clazz in PLOTTER:
            plotter = clazz(self.name, self.eegData, self.signals, self.filePath, self.save, self.plot, logScale)
            thread = Process(target=plotter.doPlot)
            self.plotter.append(thread)

    def main(self):
        self.doPlot()

        self.collect_stats()
        self.printStats()
        [plot.join() for plot in self.plotter]

        self.queue.put(self.stats)

    def doPlot(self):
        for thread in self.plotter:
            thread.start()

    def collect_stats(self):
        self.collectGeneralStats()
        self.fftData = {}
        for signal in self.signals:
            self.stats[SIGNALS_KEY][signal] = {}
            self.collectRawStats(signal)
        self.plotFFT()

    def plotFFT(self):
        for freq in FREQ_RANGE:
            plotter = FrequencyPlotter(str(freq) + ": " + self.name, self.eegData, self.signals, self.filePath, self.fftData, freq, self.save, self.plot)
            thread = Process(target=plotter.doPlot)
            self.plotter.append(thread)
            thread.start()

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
        windows = self.getWindows(data)
        for field, attributes in self.statFields.iteritems():
            fieldValues = []
            for window in windows:
                sigStat = self._getSignalStat(attributes["method"], window)
                fieldValues.append(sigStat)
            merged = self._mergeValues(fieldValues, field)
            self._addSignalStatValue(signal, category, field, merged)
        self._addFFT(signal, category, windows)

    def _addFFT(self, signal, category, windows):
        ffts = []
        for window in windows:
            ffts.append(self._getFreqValues(window))
        ffts = array(ffts).transpose()
        fftDict = {}
        for i, fft in zip(FREQ_RANGE, ffts):
            fftDict[str(i)] = fft
            merged = nanmean(fft)
            self._addSignalStatValue(signal, category, str(i), merged)
        self.fftData[signal] = fftDict

    def getWindows(self, raw):
        windows = []
        for start in range(0, len(raw), self.windowSize / 2):
            end = start + self.windowSize
            if end <= len(raw):
                windows.append(raw[start:end])
        return windows

    def _getSignalStat(self, method, raw):
        return method(raw)

    def _getFreqValues(self, raw):
        fft = self.fft.fft(raw)
        return [fft[freq] for freq in FREQ_RANGE]

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

    def printStats(self):
        content = self.ssPrint.getSignalStatsString(self.stats)
        print content
        if self.save:
            filePath = getNewFileName(str(self.filePath), "txt", "_stats")
            self.ssPrint.saveStats(filePath, content)


class SignalStatisticCollector(object):
    
    def __init__(self, fileNames=None, signals=None, save=False, plot=False, logScale=False, name=""):
        self.signals = signals
        self.save = save
        self.plot = plot
        self.logScale = logScale
        self.name = name

        self.fileNames = fileNames
        self.stats = []
        self.merge = {}
        self.ssPrint = SignalStatisticPrinter("merge")
        self.dataLen = 0
        self.statsUtils = []
    
    def main(self):
        queue = Queue()
        threads = []
        for fileName in self.fileNames:
            s = SignalStatisticUtil(queue, fileName, signals=self.signals, save=self.save, plot=self.plot, logScale=self.logScale, name=self.name)
            self.dataLen += s.eegData.len
            thread = Thread(target=s.main)
            threads.append(thread)
            thread.start()

        [thread.join() for thread in threads]
        self.stats = list(queue.queue)

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
            return value
        if typ == MEAN_TYPE:
            return value / float(count)

    def printCollection(self):
        general = {"dataLength": str(self.dataLen)}
        stats = {SIGNALS_KEY: self.merge, GENERAL_KEY: general}
        content = self.ssPrint.getSignalStatsString(stats)
        print content
        filePath = experimentDir + "merge.txt"
        self.ssPrint.saveStats(filePath, content) 

def test():
    return [buildPath("test", "test.csv")]

def tests():
    return [buildPath("test", "test.csv"), buildPath("test", "test.csv"), buildPath("test", "test.csv")]

def runTest():
    fileNames = tests()
    s = SignalStatisticCollector(fileNames=fileNames, plot=False, save=False, name="xxx")
    s.main()

def single():
    return ["1", "2"], None

def runMNE():
    fileNames = singleMNE()
    s = SignalStatisticCollector(fileNames=fileNames, plot=False, save=True)
    s.main()

def singleMNE():
    return [buildPath("1", "EOG.raw.fif")]


def doAll(fileName):
    probands = ConfigProvider().getExperimentConfig().get("probands")
    return probands, fileName

def runWithSplits(fileName="EOG.raw.fif"):
    awakes, drowsys = getAllWithSplit(fileName)
    s = SignalStatisticCollector(fileNames=awakes, plot=False, save=True, name="awake")
    s.main()
    x = SignalStatisticCollector(fileNames=drowsys, plot=False, save=True, name="drowsy")
    x.main()

def getAllWithSplit(fileName):
    probands = ConfigProvider().getExperimentConfig().get("probands")
    awakes, drowsys = [], []
    for proband in probands:
        awake, drowsy = getSplit(proband, fileName)
        awakes.append(awake)
        drowsys.append(drowsy)
    return awakes, drowsys

def getSplit(proband, fileName):
    fu = FileUtil()
    filePath = "%s%s/%s" % (experimentDir, proband, fileName)
    dto = fu.getDto(filePath)
    s1, s2, s3, s4 = _getStartStopPercent(dto)
    awake = fu.getPartialDto(dto, s1, s2)
    drowsy = fu.getPartialDto(dto, s3, s4)
    return [awake, drowsy]

def _getStartStopPercent(dto, s1=5, s2=25, s3=75, s4=95):
    length = len(dto) / 100
    return s1*length, s2*length, s3*length, s4*length

def buildPath(proband, fileName):
    return "%s%s/%s" % (experimentDir, proband, fileName)

experimentDir = ConfigProvider().getExperimentConfig().get("filePath")

if __name__ == "__main__":
    runTest()
    #runWithSplits()