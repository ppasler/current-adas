#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 19.09.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

import os

from matplotlib import pyplot as plt
import mne

from config.config import ConfigProvider
from util.eeg_table_util import EEGTableFileUtil, EEGTableDto
from mne.preprocessing.ica import ICA


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

    def createMNEObject(self, data):
        info = self._createInfo(data.getEEGHeader(), data.filePath)
        return mne.io.RawArray(data.getEEGData(), info)

    def convertMNEToEEGTableDto(self, mneObj):
        header = mneObj.ch_names
        data = mneObj._data
        filePath = mneObj.info["filename"]
        return EEGTableDto(header, data, filePath)

    def plotPSDTopo(self, mneObj):
        layout = mne.channels.read_layout('EEG1005')
        mneObj.plot_psd_topo(tmax=30., fmin=5., fmax=60., n_fft=128, layout=layout)
        layout.plot()

    def bandpassFilterData(self, mneObj):
        upperFreq = self.config.getProcessingConfig().get("upperFreq")
        lowerFreq = self.config.getProcessingConfig().get("lowerFreq")
        return mneObj.filter(lowerFreq, upperFreq)

    def getEEGCannels(self, mneObj):
        return mneObj.copy().pick_types(meg=False, eeg=True)

    def getChannels(self, mneObj, channels):
        return mneObj.copy().pick_channels(channels)

    def cropChannels(self, mneObj, tmin, tmax):
        return mneObj.copy().crop(tmin, tmax-1)

    def dropChannels(self, mneObj, channels):
        return mneObj.copy().drop_channels(channels)

    def ICA(self, mneObj):
        picks = mne.pick_types(mneObj.info, meg=False, eeg=True, eog=False, stim=False, exclude='bads')
        ica = ICA(n_components=0.95, method='fastica', max_iter=500)
        ica.fit(mneObj, picks=picks) # eeg=40e-6 V (EEG channels)
        print ica

    def getChannel(self, mneObj):
        channels = ["AF3", "AF4", "F3", "F4"]
        raw = self.getChannels(mneObj, channels)
        raw = self.cropChannels(raw, 3, 4)
        print raw
        raw = self.dropChannels(raw, channels[:2])
        print raw
        _ = plt.plot(raw._data[1, :])
        plt.show()


if __name__ == '__main__':
    path = os.path.dirname(os.path.abspath(__file__)) +  "/../../../captured_data/janis/parts/"
    util = MNEUtil()
    eegData = EEGTableFileUtil().readFile(path + "2016-07-12-11-15_EEG_4096.csv")
    mneObj = util.createMNEObject(eegData)

    util.getEEGCannels(mneObj)
    