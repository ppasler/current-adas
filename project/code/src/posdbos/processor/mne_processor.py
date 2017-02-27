#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 02.08.2016

:author: Paul Pasler
:organization: Reutlingen University
'''
from posdbos.util.quality_util import QualityUtil
from posdbos.util.signal_util import SignalUtil
from config.config import ConfigProvider
from posdbos.util.mne_util import MNEUtil
from posdbos.util.eog_extractor import EOGExtractor
from mne.viz.utils import plt_show

import warnings
warnings.filterwarnings(action='ignore')

class MNEProcessor(object):
    def __init__(self):
        self.totalInvalid = 0
        self.totalCount = 0

        self.preProcessor = SignalPreProcessor()
        self.signalProcessor = SignalProcessor()
        self.fftProcessor = FreqProcessor()

    def process(self, eegData):
        invalidCount = 0
        preProc = self.preProcessor.process(eegData)
        psd = self.fftProcessor.process(preProc)
        #proc, procInvalid = self.signalProcessor.process(preProc)

        return psd, False

class SignalPreProcessor(object):
    def __init__(self):
        self.mneUtil = MNEUtil()
        config = ConfigProvider().getProcessingConfig()
        self.lowerFreq = config.get("lowerFreq")
        self.upperFreq = config.get("upperFreq")
        self.windowSeconds = ConfigProvider().getCollectorConfig().get("windowSeconds")
        self.resampleFreq = config.get("resamplingRate")
        self.eegFields = ConfigProvider().getEmotivConfig().get("eegFields")

        self.si = SignalUtil()
        self.qu = QualityUtil()
        self.eog = EOGExtractor()

    def _calcSamplingRate(self, data):
        return len(data) / self.windowSeconds

    def process(self, raw):
        header = self.eegFields
        data = [raw[head]["value"] for head in header]

        samplingRate = self._calcSamplingRate(data[0])
        mneRaw = self.mneUtil.createMNEObject(data, header, "", samplingRate)
        mneProc = self._process(mneRaw)
        
        return mneProc

    def _process(self, mneRaw):
        self.mneUtil.filterData(mneRaw, self.lowerFreq, self.upperFreq)
        mneRaw.resample(self.resampleFreq, npad='auto', n_jobs=2, verbose=True)

        ica = self.mneUtil.ICA(mneRaw, icCount=14)
        #self._plot(mneRaw, ica)
        self.eog.labelEOGChannel([ica])
        self.eog.removeEOGChannel(mneRaw, ica)

        return mneRaw

    def _plot(self, mneRaw, ica):
        ica.plot_components(show=False)
        ica.plot_sources(mneRaw, show=False)
        self.mneUtil.plotRaw(mneRaw, show=False)
        plt_show()

class SignalProcessor(object):
    def __init__(self, verbose=False):
        config = ConfigProvider().getProcessingConfig()
        self.maxNaNValues = config.get("maxNaNValues")
        self.lowerBound = config.get("lowerBound")
        self.upperBound = config.get("upperBound")
        self.normalize = config.get("normalize")
        self.samplingRate = ConfigProvider().getEmotivConfig().get("samplingRate")
        self.qualUtil = QualityUtil()
        self.sigUtil = SignalUtil()
        self.verbose = verbose

    def process(self, mneRaw):
        pass

class FreqProcessor(object):
    def __init__(self, verbose=False):
        config = ConfigProvider().getProcessingConfig()
        self.eegFields = config.get("eegFields")
        self.fmin = config.get("fmin")
        self.fmax = config.get("fmax")
        self.mneUtil = MNEUtil()


    def process(self, mneRaw):
        header = mneRaw.ch_names
        picks = [header.index(ch_name) for ch_name in self.eegFields]
        psd, freqs = self.mneUtil.calcPSD(mneRaw, self.fmin, self.fmax, picks=picks)

        return psd