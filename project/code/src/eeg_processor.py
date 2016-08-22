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
        self.lowerFreq = config.get("lowerFreq")
        self.upperFreq = config.get("upperFreq")
        self.normalize = config.get("normalize")
        self.samplingRate = ConfigProvider().getEmotivConfig().get("samplingRate")
        self.qualUtil = QualityUtil()
        self.sigUtil = SignalUtil()
        self.verbose = verbose

    def process(self, raw, quality):
        raw = self.sigUtil.normalize(raw, self.normalize)

        invalid = self.qualUtil.isInvalidData(raw)
        return raw, invalid

class EEGProcessor(object):
    def __init__(self, verbose=False):
        self.samplingRate = ConfigProvider().getEmotivConfig().get("samplingRate")
        self.qualUtil = QualityUtil()
        self.eegUtil = EEGUtil()

    def processAlpha(self, proc):
        proc = self.qualUtil.replaceNans(proc)
        alpha = self.eegUtil.getAlphaWaves(proc, self.samplingRate)
        invalid = self.qualUtil.isInvalidData(alpha)
        return alpha, invalid

    def processTheta(self, proc):
        proc = self.qualUtil.replaceNans(proc)
        theta = self.eegUtil.getThetaWaves(proc, self.samplingRate)
        invalid = self.qualUtil.isInvalidData(theta)
        return theta, invalid

    def processDelta(self, proc):
        proc = self.qualUtil.replaceNans(proc)
        delta = self.eegUtil.getDeltaWaves(proc, self.samplingRate)
        invalid = self.qualUtil.isInvalidData(delta)
        return delta, invalid

class FFTProcessor(object):
    def __init__(self, verbose=False):
        self.samplingRate = ConfigProvider().getEmotivConfig().get("samplingRate")
        self.qualUtil = QualityUtil()
        self.fftUtil = FFTUtil()
        self.eegUtil = EEGUtil()
        self.verbose = verbose

    def process(self, proc):
        proc = self.qualUtil.replaceNans(proc)
        fft = self.fftUtil.fft(proc)
        chan = self.eegUtil.getChannels(fft)
        invalid = self.qualUtil.isInvalidData(fft)
        return chan, invalid