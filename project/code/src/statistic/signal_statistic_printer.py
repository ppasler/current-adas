#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 02.08.2016

:author: Paul Pasler
:organization: Reutlingen University
'''
from statistic.signal_statistic_constants import TITLE, GENERAL_KEY, SIGNALS_KEY, STAT_FIELDS, RAW_KEY
from terminaltables import AsciiTable

DIVIDER = "\n******************************\n\n"

class SignalStatisticPrinter(object):

    def __init__(self, person):
        self.person = person

    def getSignalStatsString(self, stats):
        s = TITLE % ("Statistics print", self.person)
        s += "\n"
        s += self._getGeneralInformation(stats)
        s += "\n"
        s += self._getSignalStatString(stats)
        s += "\n"
        return s

    def _getGeneralInformation(self, stats):
        infos = [[key, value] for key, value in stats[GENERAL_KEY].iteritems()]
        table = AsciiTable(infos)
        table.inner_heading_row_border = False
        return table.table

    def _getSignalStatString(self, stats):
        header = [SIGNALS_KEY] + STAT_FIELDS.keys() + [str(f)+"Hz" for f in range(1, 15)]
        table = [header[:]]
        for signal, values in stats[SIGNALS_KEY].iteritems():
            l = [signal]
            v = self._printSignalStat(RAW_KEY, signal, values)
            l.extend([self._roundIfFloat(x) for x in v])
            table.append(l)
        return AsciiTable(table).table

    def _roundIfFloat(self, value):
        if isinstance(value, float):
            return ('%.2f' % value).rstrip('0').rstrip('.')#"%.2f" % value
        return str(value)

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
