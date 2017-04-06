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
from numpy import NaN

class EEGProcessor(object):
    def __init__(self):
        self.preProcessor = SignalPreProcessor()
        self.signalProcessor = SignalProcessor()
        self.fftProcessor = FFTProcessor()

    def process(self, dto):
        for key in dto:
            raw, quality = dto.getChannel(key)

            proc, invalid = self.preProcessor.process(raw)

            proc, invalid = self.signalProcessor.process(proc, quality)
            if invalid:
                return None, True

            chan, invalid = self.fftProcessor.process(proc)
            if invalid:
                return None, True

            dto.addNewField(key, "theta", chan["theta"])
        return dto, False

class SignalPreProcessor(object):
    def __init__(self):
        config = ConfigProvider().getProcessingConfig()
        self.lowerFreq = config.get("lowerFreq")
        self.upperFreq = config.get("upperFreq")
        self.samplingRate = ConfigProvider().getEmotivConfig().get("samplingRate")
        self.sigUtil = SignalUtil()

    def process(self, raw):
        return raw, False

class SignalProcessor(object):
    def __init__(self, verbose=False):
        config = ConfigProvider().getProcessingConfig()
        self.maxNaNValues = config.get("maxNaNValues")
        self.lowerBound = config.get("lowerBound")
        self.upperBound = config.get("upperBound")
        self.normalize = config.get("normalize")
        self.mean = config.get("mean")
        self.samplingRate = ConfigProvider().getEmotivConfig().get("samplingRate")
        self.windowSeconds = ConfigProvider().getCollectorConfig().get("windowSeconds")
        self.qualUtil = QualityUtil()
        self.sigUtil = SignalUtil()
        self.verbose = verbose

    def process(self, raw, quality):
        # remove outliners
        proc = self.qualUtil.replaceOutliners(raw, NaN)

        # too much outliners?
        if self.qualUtil.isInvalidData(proc, len(raw)/self.windowSeconds):
            return None, True

        # center signal (mean = 0)
        #proc = self.sigUtil.center(proc, self.mean)

        # normalize date between -1 and 1
        #proc = self.sigUtil.normalize(proc)

        # replace Nans with zero (for fft)
        proc = self.qualUtil.replaceNans(proc)
        return proc, False

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
        return chan, False