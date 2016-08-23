#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 02.08.2016

:author: Paul Pasler
:organization: Reutlingen University
'''
from util.quality_util import QualityUtil
from util.signal_util import SignalUtil
from numpy import NaN
from config.config import ConfigProvider
from util.eeg_util import EEGUtil
from util.fft_util import FFTUtil

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