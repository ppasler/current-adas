#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 02.08.2016

:author: Paul Pasler
:organization: Reutlingen University
'''
from statistic.signal_statistic_contants import TITLE, GENERAL_KEY, SIGNALS_KEY, STAT_FIELDS, RAW_KEY, QUALITY_KEY


DIVIDER = "******************************\n\n"


class SignalStatisticPrinter(object):

    def __init__(self, person):
        self.person = person

    def getSignalStatsString(self, stats):
        s = TITLE % (self.person)
        s += "\n"
        s += DIVIDER
        for key, value in stats[GENERAL_KEY].iteritems():
            s += "%s:\t%s\n" % (key, value)
        s += DIVIDER
        s += self._getSignalStatString(stats)
        s += DIVIDER
        return s

    def _getSignalStatString(self, stats):
        header = [SIGNALS_KEY] + STAT_FIELDS.keys() + [s + "_Q" for s in STAT_FIELDS]
        s = "\t".join(header) + "\n"
        for signal, values in stats[SIGNALS_KEY].iteritems():
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

    def saveStats(self, filePath, content):
        with open(filePath, 'w') as fileObj:
            fileObj.write(content)

if __name__ == "__main__":
    SignalStatisticPrinter("test")
