#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 10.01.2017

:author: Paul Pasler
:organization: Reutlingen University
'''

import warnings
warnings.filterwarnings(action='ignore')

import time

from mne.viz.utils import plt_show

from config.config import ConfigProvider
from util.eog_extractor import EOGExtractor
from util.mne_util import MNEUtil
from util.signal_table_util import TableFileUtil

mneUtil = MNEUtil()
#eogExtractor = EOGExtractor()
procConfig = ConfigProvider().getProcessingConfig()
FILE_PATH = "E:/thesis/experiment/%s/"
sFreq = procConfig.get("samplingRate")
icCount = procConfig.get("icCount")
probands = ConfigProvider().getExperimentConfig().get("probands")

def saveRaw(proband):
    filepath = FILE_PATH % str(proband)

    start = time.time()
    eegFileName = filepath + "EEG.csv"
    eegData = TableFileUtil().readEEGFile(eegFileName)
    eegRaw = mneUtil.createMNEObjectFromEEGDto(eegData)
    dur = time.time() - start
    print "read EEG and create MNE object: %.2f" % dur

    #start = time.time()
    #mneUtil.bandpassFilterData(eegRaw)
    #dur = time.time() - start
    #print "filter EEG: %.2f" % dur

    #start = time.time()
    #eegRaw.resample(sFreq, npad='auto', n_jobs=8, verbose=True)
    #dur = time.time() - start
    #print "resampled EEG: %.2f" % dur

    mneUtil.markBadChannels(eegRaw, ["AF3"])
    #eegRaw = mneUtil.interpolateBadChannels(eegRaw)

    try:
        start = time.time()
        ecgFileName = filepath + "ECG.csv"
        ecgData = TableFileUtil().readECGFile(ecgFileName)
        ecgRaw = mneUtil.createMNEObjectFromECGDto(ecgData)

        dur = time.time() - start
        print "read ECG: %.2f" % dur
        start = time.time()
    
        mneUtil.addECGChannel(eegRaw, ecgRaw)

        dur = time.time() - start
        print "merged channels: %.2f" % dur
    except Exception as e:
        print e

    start = time.time()
    mneUtil.save(eegRaw, filepath + "EEG_")
    dur = time.time() - start
    print "saved file: %.2f" % dur

def saveRawAll():
    start = time.time()
    for proband in probands:
        saveRaw(proband)
    dur = time.time() - start
    print "\n\nTOTAL: %.2f" % dur

def loadRaw(proband, name = "EEG"):
    fifname = (FILE_PATH % str(proband)) + name + ".raw.fif"
    start = time.time()
    fifraw = mneUtil.load(fifname)
    dur = time.time() - start
    print "read EEG: %.2f" % dur
    start = time.time()

    #mneUtil.plotRaw(fifraw, title="Raw data " + proband)
    return fifraw


def testLoadRaw():
    loadRaw("Test")

def plotICA(raw, ica):
    picks=None
    ica.plot_components(inst=raw, colorbar=True, show=False, picks=picks)
    ica.plot_sources(raw, show=False, picks=picks)
    #ica.plot_properties(raw, picks=0, psd_args={'fmax': 35.})

def createICAList():
    icas_from_other_data = list()
    raw_from_other_data = list()
    for proband in probands:
        raw, ica = createICA(proband)
        raw_from_other_data.append(raw)
        icas_from_other_data.append(ica)
    return raw_from_other_data, icas_from_other_data

def createICA(proband, raw = None, icCount=None, random_state=None):
    if raw is None:
        raw = loadRaw(proband)
    ica = mneUtil.ICA(raw, icCount=icCount, random_state=random_state)
    return raw, ica

def saveICAList(icas, name="EEG"):
    for proband, ica in zip(probands, icas):
        saveICA(proband, ica, name)

def saveICA(proband, ica, name="EEG"):
    filePath = (FILE_PATH % str(proband)) + name + ".ica.fif"
    mneUtil.saveICA(ica, filePath)

def loadICAList():
    icas_from_other_data = list()
    raw_from_other_data = list()
    for proband in probands:
        raw, ica = loadICA(proband)
        ica.labels_ = dict()
        raw_from_other_data.append(raw)
        icas_from_other_data.append(ica)
    return raw_from_other_data, icas_from_other_data

def loadICA(proband):
    filePath = (FILE_PATH % str(proband)) + "EEG"
    raw = mneUtil.load(filePath + ".raw.fif")
    ica = mneUtil.loadICA(filePath + ".ica.fif")
    return raw, ica

def excludeAndPlotRaw(raw, ica, exclude, title=""):
    raw1 = raw.copy()
    ica.apply(raw1, exclude=exclude)
    raw.plot(show=False, scalings=dict(eeg=300), title=title + " raw")
    raw1.plot(show=False, scalings=dict(eeg=300), title=title + " eog")

def getAndAddEOGChannel(raws, icas):
    extractor = EOGExtractor()
    extractor.labelEOGChannel(icas)
    for raw, ica, proband in zip(raws, icas, probands):
        eogRaw = extractor.getEOGChannel(raw, ica)
        raw = extractor.removeEOGChannel(raw, ica)
        mneUtil.addEOGChannel(raw, eogRaw)
        raw.info["description"] = proband
        mneUtil.plotRaw(raw)

        #filePath = (FILE_PATH % proband) + "EOG"
        #mneUtil.save(raw, filePath)

def addBlink():
    global probands
    probands.insert(0, "Test")

if __name__ == '__main__':
    proband = "Test"
    raw, ica = loadICA(proband)
    plotICA(raw, ica)
    excludeAndPlotRaw(raw, ica, [2])

    plt_show()