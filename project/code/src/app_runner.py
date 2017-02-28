#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 30.05.2016

:author: Paul Pasler
:organization: Reutlingen University
'''
import logging
logging.basicConfig(level=logging.INFO,
                format='%(asctime)s.%(msecs)03d %(levelname)-8s %(module)s.%(funcName)s:%(lineno)d %(message)s',
                datefmt='%H:%M:%S')
from posdbos.util.file_util import FileUtil

import threading
from config.config import ConfigProvider
from posdbos.factory import Factory

exConfig = ConfigProvider().getExperimentConfig()
probands = exConfig.get("probands")
experimentDir = exConfig.get("filePath")

fileUtil = FileUtil()


def getFilePaths(fileName):
    filePaths = []
    for proband in probands:
        filePath = "%s%s/" % (experimentDir, proband)
        filePaths.append(filePath + fileName)
    return filePaths

def splitDtos(filePaths):
    awakes, drowsies = [], []
    for filePath in filePaths:
        dto = fileUtil.getDto(filePath)
        s1, e1, s2, e2 = _getStartStopPercent(dto)
        awake = fileUtil.getPartialDto(dto, s1, e1)
        drowsy = fileUtil.getPartialDto(dto, s2, e2)
        awakes.append(awake)
        drowsies.append(drowsy)
    return awakes, drowsies

def _getStartStopPercent(dto, s1=10, s2=20, s3=85, s4=95):
    length = len(dto) / 100
    return s1*length, s2*length, s3*length, s4*length

def runAndSaveSplits(fileName):
    filePaths = getFilePaths(fileName)
    awakes, drowsies = splitDtos(filePaths)
    runAndSave(awakes, experimentDir + "test/awakes_proc_new8.csv")
    runAndSave(drowsies, experimentDir + "test/drowsies_proc_new8.csv")

def runDemoSplits(fileName):
    filePaths = getFilePaths(fileName)
    awakes, drowsies = splitDtos(filePaths)
    runDemo(awakes)
    runDemo(drowsies)

def runDemoSplitsSeparate(fileName):
    filePaths = getFilePaths(fileName)
    for filePath in filePaths:
        print filePath
        awakes, drowsies = splitDtos([filePath])
        runDemo(awakes)
        runDemo(drowsies)

def runMPData():
    awake = "%s/mp/%s" % (experimentDir, "awake_full_norm.raw.fif")
    drowsy = "%s/mp/%s" % (experimentDir, "drowsy_full_norm.raw.fif")
    runAndSave(awake, experimentDir + "test/awakes_proc_new2.csv")
    runAndSave(drowsy, experimentDir + "test/drowsies_proc_new2.csv")

def runProcAndSaveAll(filename):
    for proband in probands:
        runProcAndSave(proband, filename)

def runProcAndSave(proband, filename):
    #filePath = "%s/test/%s" % (experimentDir, "awake_full.csv")
    filePath = "%s%s/" % (experimentDir, proband)
    runAndSave(filePath + filename, filePath + "proc.csv")

def runAndSave(filePath, outPath):
    p = Factory.getForSave(filePath)
    logging.info("STARTING")
    pt = threading.Thread(target=p.runAndSave, args=(outPath,))
    pt.start()

    pt.join()
    logging.info("ENDING")

def runDemo(filePath):
    # 584
    #filePath = "%s/mp/%s" % (experimentDir, "drowsy_full.csv")            # 361
    #filePath = "%s/mp/%s" % (experimentDir, "drowsy_full_norm.raw.fif")   # 426 of 545 / "full_norm_4_3" 508

    #filePath = "%s/mp/%s" % (experimentDir, "awake_full.csv")             # 218
    #filePath = "%s/mp/%s" % (experimentDir, "awake_full_norm.raw.fif")     # 70 of 414 / "full_norm_4_3" 71

    #filePath = "%s/1/%s" % (experimentDir, "EEGNormGyro.raw.fif")         # 532 / 503

    nn = "2017-02-27-16-05_0"#"knn_1"
    p = Factory.getForDemo(nn, filePath)
    logging.info("STARTING")
    pt = threading.Thread(target=p.run)
    pt.start()

    pt.join()
    logging.info("ENDING")

def testFolder():
    global probands
    probands = ["test"]

if __name__ == '__main__': # pragma: no cover
    #runProcAndSave("2", "EOG.raw.fif")
    #runProcAndSave("test", "awake_full.raw.fif")
    #runDemoSplits("EEGNormed.raw.fif")
    runDemoSplitsSeparate("EEGNormed.raw.fif")
    #runAndSaveSplits("EEGNormed.raw.fif")
    #runMPData()
    #runDemo()