#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 10.01.2017

:author: Paul Pasler
:organization: Reutlingen University
'''

import time
import warnings

from mne.viz.utils import plt_show

from config.config import ConfigProvider
from posdbos.util.eog_extractor import EOGExtractor
from posdbos.util.file_util import FileUtil
from posdbos.util.mne_util import MNEUtil, MNEPlotter
from posdbos.processor.mne_processor import MNEProcessor, SignalPreProcessor, FreqProcessor
from numpy import count_nonzero, mean


warnings.filterwarnings(action='ignore')


mneUtil = MNEUtil()
mnePlotter = MNEPlotter()
fileUtil = FileUtil()
#eogExtractor = EOGExtractor()
procConfig = ConfigProvider().getProcessingConfig()
FILE_PATH = "E:/thesis/experiment/%s/"
sFreq = procConfig.get("resamplingRate")
icCount = procConfig.get("icCount")
probands = ConfigProvider().getExperimentConfig().get("probands")

def _filter(raw):
    start = time.time()
    mneUtil.bandpassFilterData(raw)
    dur = time.time() - start
    print "filter EEG: %.2f" % dur

def _resample(raw):
    start = time.time()
    raw.resample(sFreq, npad='auto', n_jobs=8, verbose=True)
    dur = time.time() - start
    print "resampled EEG: %.2f" % dur

def _addECGChannel(filePath, raw):
    try:
        start = time.time()
        ecgFileName = filePath + "ECG.csv"
        ecgData = fileUtil.getECGDto(ecgFileName)
        ecgRaw = mneUtil.createMNEObjectFromECGDto(ecgData)

        dur = time.time() - start
        print "read ECG: %.2f" % dur
        start = time.time()
    
        mneUtil.addECGChannel(raw, ecgRaw)

        dur = time.time() - start
        print "merged channels: %.2f" % dur
    except Exception as e:
        print e

def processRaw(proband, fileName, outName="EEG_"):
    filePath = FILE_PATH % str(proband)

    start = time.time()
    eegFileName = filePath + fileName
    eegData = fileUtil.getDto(eegFileName)
    eegRaw = mneUtil.createMNEObjectFromEEGDto(eegData)
    dur = time.time() - start
    print "read EEG and create MNE object: %.2f" % dur

    _filter(eegRaw)
    _resample(eegRaw)

    _addECGChannel(filePath, eegRaw)

    start = time.time()
    fileUtil.save(eegRaw, filePath + outName)
    dur = time.time() - start
    print "saved file: %.2f" % dur

def processRawAll(fileName="EEG.csv", outName="EEG"):
    start = time.time()
    for proband in probands:
        processRaw(proband, fileName, outName)
    dur = time.time() - start
    print "\n\nTOTAL: %.2f" % dur

def loadRaw(proband, name = "EEG"):
    fifname = (FILE_PATH % str(proband)) + name + ".raw.fif"
    start = time.time()
    fifraw = fileUtil.load(fifname)
    dur = time.time() - start
    print "read EEG: %.2f" % dur
    start = time.time()

    #mnePlotter.plotRaw(fifraw, title="Raw data " + proband)
    return fifraw

def loadRawAll(fileName):
    start = time.time()
    raws = []
    for proband in probands:
        raws.append(loadRaw(proband, fileName))
    dur = time.time() - start
    print "\n\nTOTAL: %.2f" % dur
    return raws

def testLoadRaw():
    loadRaw("Test")

def plotRaw(raw, title="RAW"):
    mnePlotter.plotRaw(raw, title, show=False)

def plotICA(raw, ica):
    mnePlotter.plotICA(raw, ica)

def createICAAll(fileName):
    icas_from_other_data = list()
    raw_from_other_data = list()
    for proband in probands:
        raw = loadRaw(proband, fileName)
        raw, ica = createICA(proband, raw)
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
    fileUtil.saveICA(ica, filePath)

def loadICAAll():
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
    raw = fileUtil.load(filePath + ".raw.fif")
    ica = fileUtil.loadICA(filePath + ".ica.fif")
    return raw, ica

def excludeAndPlotRaw(raw, ica, exclude, title=""):
    raw1 = raw.copy()
    ica.apply(raw1, exclude=exclude)
    raw.plot(show=False, scalings=dict(eeg=300), title=title + " raw")
    raw1.plot(show=False, scalings=dict(eeg=300), title=title + " eog")

def getAndAddEOGChannel(raws, icas, outName="EOG"):
    extractor = EOGExtractor()
    extractor.labelEOGChannel(icas)
    for raw, ica, proband in zip(raws, icas, probands):
        eogRaw = extractor.getEOGChannel(raw, ica)
        raw = extractor.removeEOGChannel(raw, ica)
        mneUtil.addEOGChannel(raw, eogRaw)
        #plotICA(raw, ica)
        raw.info["description"] = proband
        filePath = (FILE_PATH % proband) + outName
        fileUtil.save(raw, filePath)

def addBlink():
    global probands
    probands.insert(0, "Test")

def testFolder():
    global probands
    probands = ["test_data"]
    global FILE_PATH
    FILE_PATH = "../test/%s/"

def tryThis():
    fpath = (FILE_PATH % "test") + "blink.csv"
    raw = fileUtil.getDto(fpath)
    mneRaw = mneUtil.createMNEObject(raw.getEEGData(), raw.getEEGHeader(), "", raw.getSamplingRate())

    mneUtil.filterData(mneRaw, 0.5, 30)
    mneRaw.resample(sFreq, npad='auto', n_jobs=2, verbose=True)


    ica = mneUtil.ICA(mneRaw)
    ica.plot_components(show=False)
    ica.plot_sources(mneRaw, show=False)
    mneUtil.plotRaw(mneRaw, show=False)
    plt_show()
    fileUtil.save(mneRaw, fpath + ".fif")
    fileUtil.saveICA(ica, fpath)

def saveRaw(raw, proband, fileName):
    filePath = (FILE_PATH % proband) + fileName
    fileUtil.save(raw, filePath)

def addICAChannels(fileName, outName):
    for proband in probands:
        raw = loadRaw(proband, fileName)
        raw, ica = createICA(proband, raw)
        rawIca = addICAChannel(raw, ica)
        saveRaw(rawIca, proband, outName)

def addICAChannel(raw, ica):
    rawIca = mneUtil.addICASources(raw, ica)
    mnePlotter.plotRaw(rawIca)
    return rawIca

def orThis():
    extractor = EOGExtractor()
    pat = (FILE_PATH % "test")
    files = ["drowsy_full.csv", "awake_full.csv"]
    raws, icas = [], []
    for name in files:
        fpath = pat + name
        dto = fileUtil.getDto(fpath)
        raw = mneUtil.createMNEObject(dto.getEEGData(), dto.getEEGHeader(), dto.filePath, 128)
        mneUtil.bandpassFilterData(raw)
        raw.resample(sFreq, npad='auto', n_jobs=8, verbose=True)
        raws.append(raw)
        _, ica = createICA("", raw)
        icas.append(ica)

    extractor.labelEOGChannel(icas)

    for raw, ica, name in zip(raws, icas, files):
        raw = extractor.removeEOGChannel(raw, ica)
        raw.info["description"] = name
        fileUtil.save(raw, pat + name)

def csvToRaw():
    start = time.time()
    for proband in probands:
        filePath = FILE_PATH % str(proband)
    
        start = time.time()
        eegFileName = filePath + "EEG.csv"
        dto = fileUtil.getDto(eegFileName)
        raw = mneUtil.createMNEObjectFromEEGDto(dto)
        dur = time.time() - start
        print "read EEG and create MNE object: %.2f" % dur

        _filter(raw)
        _resample(raw)

        _addECGChannel(filePath, raw)
    
        start = time.time()
        fileUtil.save(raw, filePath + "EEGGyro")
        dur = time.time() - start
        print "saved file: %.2f" % dur
    dur = time.time() - start
    print "\n\nTOTAL: %.2f" % dur

def rawWithEOGAndICA():
    start = time.time()
    raws, icas = [], []
    for proband in probands:
        start2 = time.time()
        raw = loadRaw(proband, "EEGGyro")

        raw, ica = createICA(proband, raw)
        saveICA(proband, ica, "EEGGyro")
        raws.append(raw)
        icas.append(ica)

        dur = time.time() - start2
        print "ica created: %.2f" % dur

    start2 = time.time()
    getAndAddEOGChannel(raws, icas, outName="EEGEOG")
    dur = time.time() - start2
    print "eog added: %.2f" % dur

    start2 = time.time()
    rawIcas = []
    for raw, ica in zip(raws, icas):
        rawIcas.append(addICAChannel(raw, ica))
    dur = time.time() - start2
    print "ica added: %.2f" % dur

    start2 = time.time()
    for proband, rawIca in zip(probands, rawIcas):
        saveRaw(rawIca, proband, "EEGICA")
    dur = time.time() - start2
    print "saved: %.2f" % dur

    dur = time.time() - start
    print "\n\nTOTAL: %.2f" % dur

def rawWithNormedGyro():
    config = ConfigProvider().getProcessingConfig()
    xGround, yGround = config.get("xGround"), config.get("yGround")
    for proband in probands:
        raw = loadRaw(proband, "EEGGyro")
        normGyroChannel(raw, xGround, yGround)
        saveRaw(raw, proband, "EEGNormGyro")

def normGyroChannel(raw, xGround, yGround):
    ch_names = raw.info["ch_names"]
    data = raw._data
    xChannel = data[ch_names.index("X")]
    xChannel -= xGround
    yChannel = data[ch_names.index("Y")]
    yChannel -= yGround

if __name__ == '__main__':
    raw = loadRaw("2", "EEGNormGyro")
    ch_names = raw.info["ch_names"]
    print mean(raw._data[ch_names.index("X")])

    mnePlotter.plotRaw(raw)
    plt_show()