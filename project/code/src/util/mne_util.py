#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 19.09.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

import mne
from config.config import ConfigProvider

class MNEUtil():

    def __init__(self):
        self.config = ConfigProvider().getEmotivConfig()

    def createInfo(self, channelNames, filename):
        channelTypes = ["eeg"] * len(channelNames)
        samplingRate = self.config.get("samplingRate")
        info = mne.create_info(channelNames, samplingRate, channelTypes)
        info["description"] = "PoSDBoS"
        info["filename"] = filename
        return info

    def createRawObject(self, data):
        info = self.createInfo(data.getEEGHeader(), data.filePath)
        return mne.io.RawArray(data.getEEGData(), info)