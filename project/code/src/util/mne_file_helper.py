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
eogExtractor = EOGExtractor()
FILE_PATH = "E:/thesis/experiment/%s/"
sFreq = 64.

def saveRaw(proband):
    filepath = FILE_PATH % str(proband)

    start = time.time()
    eegFileName = filepath + "EEG.csv"
    eegData = TableFileUtil().readEEGFile(eegFileName)
    eegRaw = mneUtil.createMNEObjectFromEEGDto(eegData)
    dur = time.time() - start
    print "read EEG and create MNE object: %.2f" % dur

    start = time.time()
    mneUtil.bandpassFilterData(eegRaw)
    dur = time.time() - start
    print "filter EEG: %.2f" % dur

    start = time.time()
    eegRaw.resample(sFreq, npad='auto', n_jobs=8, verbose=True)
    dur = time.time() - start
    print "resampled EEG: %.2f" % dur

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
    mneUtil.save(eegRaw, filepath + "EEG_resampled_64hz")
    dur = time.time() - start
    print "saved file: %.2f" % dur

def saveRawAll():
    start = time.time()
    for proband in getProbands():
        saveRaw(proband)
    dur = time.time() - start
    print "\n\nTOTAL: %.2f" % dur

def loadRaw(proband):
    fifname = (FILE_PATH % str(proband)) + "EEG.raw.fif"
    start = time.time()
    fifraw = mneUtil.load(fifname)
    dur = time.time() - start
    print "read EEG: %.2f" % dur
    start = time.time()

    mneUtil.plotRaw(fifraw, title="Raw data " + proband)


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
    for proband in getProbands():
        raw, ica = createICA(proband)
        print "load ICA ", proband, ica.get_components().shape
        raw_from_other_data.append(raw)
        icas_from_other_data.append(ica)
    return raw_from_other_data, icas_from_other_data

def createICA(proband):
    filePath = (FILE_PATH % str(proband))
    raw = mneUtil.load(filePath + "EEG.raw.fif")
    ica = mneUtil.loadICA(filePath + "EEG.ica.fif")
    return raw, ica

def saveICAList(icas, name="EEG"):
    for i, proband in enumerate(getProbands()):
        filePath = (FILE_PATH % str(proband)) + name + ".ica.fif"
        mneUtil.saveICA(icas[i], filePath)

def getProbands():
    return ConfigProvider().getExperimentConfig().get("probands")

def loadICAList():
    util = MNEUtil()
    icas_from_other_data = list()
    raw_from_other_data = list()
    for proband in getProbands():
        filePath = (FILE_PATH % str(proband)) + "EEG"
        raw = util.load(filePath + ".raw.fif")
        ica = util.loadICA(filePath + ".ica.fif")

        raw_from_other_data.append(raw)
        icas_from_other_data.append(ica)
    return raw_from_other_data, icas_from_other_data

def excludeAndPlotRaw(raw, ica, exclude, title=""):
    raw1 = raw.copy()
    ica.apply(raw1, exclude=exclude)
    raw.plot(show=False, scalings=dict(eeg=300), title=title + " raw")
    raw1.plot(show=False, scalings=dict(eeg=300), title=title + " eog")

def getAndAddEOGChannel():
    extractor = EOGExtractor()
    raws, icas = createICAList()
    extractor.labelEOGChannel(icas)

    for raw, ica, proband in zip(raws, icas, getProbands()):
        eogRaw = extractor.getEOGChannel(raw, ica)
        raw = extractor.removeEOGChannel(raw, ica)
        mneUtil.addEOGChannel(raw, eogRaw)
        mneUtil.plotRaw(raw, title=proband)

        filePath = (FILE_PATH % proband) + "EOG"
        mneUtil.save(raw, filePath)
    plt_show()

if __name__ == '__main__':
    getAndAddEOGChannel()

