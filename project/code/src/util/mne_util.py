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

DEFAULT_SAMPLE_LENGTH = 1

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
        a = self._createMNEEpochsObject(eegData, awakeData.getEEGHeader(), filePath)
        a.drop_bad()
        b = self._createMNEEpochsArrayObject(eegData, awakeData.getEEGHeader(), filePath)
        print(a.get_data()[0,0] / max(a.get_data()[0,0]))
        print(b.get_data()[0,0] / max(b.get_data()[0,0]))
        return b

    def _createMNEEpochsObject(self, raw, header, filePath):
        info = self._createInfo(header, filePath)
        data = mne.io.RawArray(raw, info)
        events = self._createEventsArray(self.getSampleCount(raw))
        event_id = dict(awake=0, drowsy=1)

        return mne.Epochs(data, events=events, event_id=event_id, tmin=0.0, tmax=1.0, add_eeg_ref=True)

    def getSampleCount(self, raw):
        length = len(raw[0])
        winSize = self.config.getCollectorConfig().get("windowSize")

        return len(range(0, length-winSize, winSize / 2))
        
    def _createMNEEpochsArrayObject(self, raw, header, filePath):
        info = self._createInfo(header, filePath)
        data = self._createEpochDataArray(raw)
        events = self._createEventsArray(len(data))
        event_id = dict(awake=0, drowsy=1)

        tmin = 0.0
        return mne.EpochsArray(data, info, events, tmin, event_id, 
                               baseline=(None, 0))

    def _createEpochDataArray(self, raw):
        length = len(raw[0])
        winSize = self.config.getCollectorConfig().get("windowSize")
        epochArray = []
        for start in range(0, length-winSize, winSize / 2):
            end = start + winSize
            epoch = raw[:, start: end]
            epochArray.append(epoch)
        return np.array(epochArray)

    def _createEventsArray(self, size):
        awakeClass = self.config.getClassConfig().get("awake")
        drowsyClass = self.config.getClassConfig().get("drowsy")
        awakeList = [[i, DEFAULT_SAMPLE_LENGTH, awakeClass] for i in range(0, size / 2)]
        drowsyList = [[i, DEFAULT_SAMPLE_LENGTH, drowsyClass] for i in range(size / 2, size)]
        return np.array(awakeList + drowsyList)

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
    epochs = util.createMNEEpochsObject(awakeData, drowsyData)

    #epochs.plot(block=True)