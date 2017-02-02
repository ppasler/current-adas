#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 30.05.2016

:author: Paul Pasler
:organization: Reutlingen University
'''
import os
import threading

from config.config import ConfigProvider
from posdbos_factory import PoSDBoSFactory


scriptPath = os.path.dirname(os.path.abspath(__file__))
probands = ConfigProvider().getExperimentConfig().get("probands")

def runProcAndSaveAll(filename):
    for proband in probands:
        runProcAndSave(proband, filename)

def runProcAndSave(proband, filename):
    experiments = ConfigProvider().getExperimentConfig()
    experimentDir = experiments["filePath"]
    #filePath = "%s/test/%s" % (experimentDir, "awake_full.csv")
    filePath = "%s%s/" % (experimentDir, proband)

    p = PoSDBoSFactory.getForSave(filePath + filename)
    print "START"
    pt = threading.Thread(target=p.runAndSave, args=(filePath + "proc.csv",))
    pt.start()

    pt.join()
    print "END"

def runDemo():
    experiments = ConfigProvider().getExperimentConfig()
    experimentDir = experiments["filePath"]
    # 584
    #filePath = "%s/test/%s" % (experimentDir, "drowsy_full.csv")            # 361
    #filePath = "%s/test/%s" % (experimentDir, "raw.drowsy_full.raw.fif")    # 480
    #filePath = "%s/test/%s" % (experimentDir, "filter.drowsy_full.raw.fif") # 538
    #filePath = "%s/test/%s" % (experimentDir, "drowsy_full.raw.fif")        # 532

    #filePath = "%s/test/%s" % (experimentDir, "awake_full.csv")             # 218
    #filePath = "%s/test/%s" % (experimentDir, "raw.awake_full.raw.fif")     # 226
    #filePath = "%s/test/%s" % (experimentDir, "filter.awake_full.raw.fif")  # 326
    filePath = "%s/test/%s" % (experimentDir, "awake_full.raw.fif")          # 301

    p = PoSDBoSFactory.getForDemo("knn_1", filePath)
    print "START"
    pt = threading.Thread(target=p.run)
    pt.start()

    pt.join()
    print "END"

def testFolder():
    global probands
    probands = ["test"]

if __name__ == '__main__': # pragma: no cover
    #runProcAndSave("2", "EOG.raw.fif")
    #runProcAndSave("test", "awake_full.raw.fif")
    runDemo()