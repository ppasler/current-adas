#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 30.05.2016

:author: Paul Pasler
:organization: Reutlingen University
'''
from util.eeg_util import EEGUtil
from util.quality_util import QualityUtil
from util.signal_util import SignalUtil
from numpy import NaN

class SimpleChain(object):
    def __init__(self):
        self.eegUtil = EEGUtil()
        self.qualUtil = QualityUtil()
        self.sigUtil = SignalUtil()

    def process(self, raw, quality):
        raw = self.qualUtil.replaceBadQuality(raw, quality, NaN)
        raw = self.qualUtil.replaceSequences(raw)
        raw = self.qualUtil.replaceOutliners(raw, NaN)
        raw = self.sigUtil.normalize(raw)
        return raw