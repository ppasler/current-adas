#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 02.07.2016

:author: Paul Pasler
:organization: Reutlingen University
'''
from signal_statistic_constants import *  # @UnusedWildImport
from signal_statistic_util import SignalStatisticCollector
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from posdbos.util.file_util import FileUtil

scriptPath = os.path.dirname(os.path.abspath(__file__))

def test():
    return [buildPath("test", "test.csv")]

def tests():
    return [buildPath("test", "test.csv"), buildPath("test", "blink.csv")]

def runTest():
    fileNames = tests()
    s = SignalStatisticCollector(fileNames=fileNames, plot=False, save=True, name="xxx")
    s.main()

def single():
    return ["1", "2"], None

def runMNE():
    fileNames = singleMNE()
    s = SignalStatisticCollector(fileNames=fileNames, plot=False, save=True)
    s.main()

def singleMNE():
    return [buildPath("1", "EOG.raw.fif")]


def runAll(fileName):
    probands = ConfigProvider().getExperimentConfig().get("probands")
    fileNames = [buildPath(proband, fileName) for proband in probands]
    s = SignalStatisticCollector(fileNames=fileNames, plot=False, save=True, name="raw")
    s.main()

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

if __name__ == "__main__":
    runTest()
    #runWithSplits()
    #runAll("EOG.raw.fif")