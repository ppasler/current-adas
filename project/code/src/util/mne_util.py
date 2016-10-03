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
from mne.preprocessing.ica import ICA
from mne.time_frequency.psd import psd_multitaper

from config.config import ConfigProvider
from util.eeg_table_util import EEGTableFileUtil, EEGTableDto

import numpy as np

class MNEUtil():

    def __init__(self):
        self.config = ConfigProvider()

    def _createInfo(self, channelNames, filename):
        channelTypes = ["eeg"] * len(channelNames)
        samplingRate = self.config.getEmotivConfig().get("samplingRate")
        montage = mne.channels.read_montage("standard_1020")
        info = mne.create_info(channelNames, samplingRate, channelTypes, montage)
        info["description"] = "PoSDBoS"
        info["filename"] = filename
        return info

    def createMNEObject(self, eegData):
        info = self._createInfo(eegData.getEEGHeader(), eegData.filePath)
        return mne.io.RawArray(eegData.getEEGData(), info)

    def convertMNEToEEGTableDto(self, mneObj):
        header = mneObj.ch_names
        data = mneObj._data
        filePath = mneObj.info["filename"]
        return EEGTableDto(header, data, filePath)

    def createMNEEpochsObject(self, awakeData, drowsyData):
        filePath = awakeData.filePath
        eegData = np.concatenate((awakeData.getEEGData(), drowsyData.getEEGData()), axis=1)
        return self._createMNEEpochsObject(eegData, awakeData.getEEGHeader(), filePath)

    def _createMNEEpochsObject(self, raw, header, filePath):
        info = self._createInfo(header, filePath)
        data = self._createEpochDataArray(raw)
        events = self._createEventsArray(len(data), 0)
        event_id = dict(awake=0)

        tmin = 0.0
        return mne.EpochsArray(data, info, events, tmin, event_id)

    def _createEpochDataArray(self, raw):
        length = len(raw[0])
        winSize = self.config.getCollectorConfig().get("windowSize")
        epochArray = []
        for start in range(0, length-winSize, winSize / 2):
            end = start + winSize
            epoch = raw[:, start: end]
            epochArray.append(epoch)
        return np.array(epochArray)

    def _createEventsArray(self, size, clazz):
        return np.array([[i, 1, clazz] for i in range(size)])

    def plotPSDTopo(self, mneObj):
        layout = mne.channels.read_layout('EEG1005')
        mneObj.plot_psd_topo(tmax=30., fmin=5., fmax=60., n_fft=128, layout=layout)
        layout.plot()

    def plotSensors(self, mneObj):
        mneObj.plot_sensors(kind='3d', ch_type='eeg', show_names=True)

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
        #TODO what to do with this?
        picks = mne.pick_types(mneObj.info, meg=False, eeg=True, eog=False, stim=False, exclude='bads')
        ica = ICA(n_components=0.95, method='fastica', max_iter=500)
        ica.fit(mneObj, picks=picks) # eeg=40e-6 V (EEG channels)
        return ica

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
    path = os.path.dirname(os.path.abspath(__file__)) +  "/../../../captured_data/test_data/"
    util = MNEUtil()
    awakeData = EEGTableFileUtil().readFile(path + "awake_full.csv")
    drowsyData = EEGTableFileUtil().readFile(path + "drowsy_full.csv")
    custom_epochs = util.createMNEEpochsObject(awakeData, drowsyData)

    _ = custom_epochs['awake'].average().plot()
    