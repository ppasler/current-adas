#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 30.05.2016

:author: Paul Pasler
:organization: Reutlingen University
'''
import os

from util.eeg_table_util import EEGTableFileUtil
from util.signal_util import SignalUtil

class SignalStatisticUtil(object):
    '''
    class to show some statistical values for a channel
    '''


    def __init__(self, name, filePath):
        self.stats = {}
        self.stats["name"] = name
        self.name = name
        self.readData(filePath)
        self.su = SignalUtil()

    def readData(self, filePath):
        self.reader = EEGTableFileUtil()
        eeg_data = self.reader.readFile(filePath)
        self.raw = eeg_data.getColumn(self.name)
        self.quality = eeg_data.getQuality(self.name)

    def _addRawSignalStat(self, categroy, name, method):
        self.stats[categroy][name] = method(self.raw)
    
    def collectRawStats(self):
        category = "raw"
        self.stats[category] = {}
        self._addRawSignalStat(category, "max", self.su.maximum)
        self._addRawSignalStat(category, "min", self.su.minimum)
        self._addRawSignalStat(category, "mean", self.su.mean)

    def _addQualSignalStat(self, categroy, name, method):
        self.stats[categroy][name] = method(self.quality)

    def collectQualityStats(self):
        category = "quality"
        self.stats[category] = {}
        self._addQualSignalStat(category, "max", self.su.maximum)
        self._addQualSignalStat(category, "min", self.su.minimum)
        self._addQualSignalStat(category, "mean", self.su.mean)

    def collect_stats(self):
        self.collectRawStats()
        self.collectQualityStats()
        print self.stats
        
if __name__ == "__main__":
    filePath = os.path.dirname(os.path.abspath(__file__)) + "/../../examples/example_4096.csv"

    s = SignalStatisticUtil("F4", filePath)
    s.collect_stats()