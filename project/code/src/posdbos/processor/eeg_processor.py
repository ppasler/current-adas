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
from posdbos.util.eeg_util import EEGUtil
from posdbos.util.fft_util import FFTUtil
import numpy as np

class EEGProcessor(object):
    def __init__(self):
        self.totalInvalid = 0
        self.totalCount = 0

        self.preProcessor = SignalPreProcessor()
        self.signalProcessor = SignalProcessor()
        self.fftProcessor = FFTProcessor()

    def process(self, dto):
        invalidCount = 0
        eegData = dto.getData()
        for _, signal in eegData.iteritems():
            raw = np.array(signal["value"])
            quality = np.array(signal["quality"])

            proc = self.preProcessor.process(raw)
            proc, _ = self.signalProcessor.process(proc, quality)

            chan, fInvalid = self.fftProcessor.process(proc)
            signal["theta"] = chan["theta"]
            invalidCount += sum([fInvalid])
        if invalidCount > 0:
            self.totalInvalid += 1
        self.totalCount += 1
        return eegData, (invalidCount > 0)

class SignalPreProcessor(object):
    def __init__(self):
        config = ConfigProvider().getProcessingConfig()
        self.lowerFreq = config.get("lowerFreq")
        self.upperFreq = config.get("upperFreq")
        self.samplingRate = ConfigProvider().getEmotivConfig().get("samplingRate")
        self.sigUtil = SignalUtil()

    def process(self, raw):
        return self.sigUtil.butterBandpassFilter(raw, self.lowerFreq, self.upperFreq, self.samplingRate)

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

    def process(self, raw, quality):
        proc = self.qualUtil.replaceOutliners(raw, 0)
        proc = self.sigUtil.normalize(proc, self.normalize)

        invalid = self.qualUtil.isInvalidData(proc)
        return proc, invalid

class FFTProcessor(object):
    def __init__(self, verbose=False):
        self.samplingRate = ConfigProvider().getEmotivConfig().get("samplingRate")
        self.qualUtil = QualityUtil()
        self.fftUtil = FFTUtil()
        self.eegUtil = EEGUtil()
        self.verbose = verbose

    def process(self, proc):
        fft = self.fftUtil.fft(proc)
        chan = self.eegUtil.getChannels(fft)
        invalid = self.qualUtil.isInvalidData(fft)
        return chan, invalid