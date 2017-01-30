#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 30.05.2016

:author: Paul Pasler
:organization: Reutlingen University
'''
import os
import threading

from time import sleep
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
    #filePath = "%s/test/%s" % (experimentDir, "awake_full.csv")
    filePath = "%s/test/%s" % (experimentDir, "drowsy_full.csv")

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
    runProcAndSave("2", "EOG.raw.fif")
    #runProcAndSave("Test", "blink.csv")