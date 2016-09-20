#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 19.09.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

import os

import mne

from config.config import ConfigProvider
from util.eeg_table_util import EEGTableFileUtil
import numpy as np


class MNEUtil():

    def __init__(self):
        self.config = ConfigProvider()

    def _createInfo(self, channelNames, filename):
        channelTypes = ["eeg"] * len(channelNames)
        samplingRate = self.config.getEmotivConfig().get("samplingRate")
        info = mne.create_info(channelNames, samplingRate, channelTypes)
        info["description"] = "PoSDBoS"
        info["filename"] = filename
        return info

    def createRawObject(self, data):
        info = self._createInfo(data.getEEGHeader(), data.filePath)
        return mne.io.RawArray(data.getEEGData(), info)

    def removeArtifacts(self, mneObj):
        mneObj.copy().pick_types(eeg=True).plot(duration=60, n_channels=14, remove_dc=False)
        mneObj.plot_psd(fmax=250)

    def bandpassFilterData(self, mneObj):
        picks = mne.pick_types(mneObj.info, eeg=True)

        upperFreq = self.config.getProcessingConfig().get("upperFreq")
        lowerFreq = self.config.getProcessingConfig().get("lowerFreq")
        mneObj.filter(lowerFreq, upperFreq)
        #mneObj.plot_psd(area_mode='range', tmax=10.0, picks=picks)

    def plotChannels(self, mneObj):
        layout = mne.channels.read_layout('EEG1005')
        mneObj.plot_psd_topo(tmax=30., fmin=5., fmax=60., n_fft=128, layout=layout)
        layout.plot()

if __name__ == '__main__':
    path = os.path.dirname(os.path.abspath(__file__)) +  "/../../examples/"
    util = MNEUtil()
    eegData = EEGTableFileUtil().readFile(path + "example_1024.csv")
    mneObj = util.createRawObject(eegData)

    util.plotChannels(mneObj)
    