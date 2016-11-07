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

from config.config import ConfigProvider
from util.eeg_table_util import EEGTableFileUtil, EEGTableDto


DEFAULT_SAMPLE_LENGTH = 1

class MNEUtil():

    def __init__(self):
        self.config = ConfigProvider()

    def createMNEObjectFromDto(self, eegDto):
        return self.createMNEObject(eegDto.getEEGData(), eegDto.getEEGHeader(), eegDto.filePath)

    def createMNEObject(self, data, header, filePath):
        info = self._createInfo(header, filePath)
        return mne.io.RawArray(data, info)

    def _createInfo(self, channelNames, filename):
        channelTypes = ["eeg"] * len(channelNames)
        samplingRate = self.config.getEmotivConfig().get("samplingRate")
        montage = mne.channels.read_montage("standard_1020")
        info = mne.create_info(channelNames, samplingRate, channelTypes, montage)
        info["description"] = "PoSDBoS"
        info["filename"] = filename
        return info

    def convertMNEToEEGTableDto(self, mneObj):
        header = mneObj.ch_names
        data = mneObj._data
        filePath = mneObj.info["filename"]
        return EEGTableDto(header, data, filePath)

    def createMNEEpochsObject(self, eegData, clazz):
        raw = self.createMNEObjectFromDto(eegData)
        events = self._createEventsArray(raw, clazz)
        return mne.Epochs(raw, events=events, tmin=0.0, tmax=0.99, add_eeg_ref=True)

    def _createEventsArray(self, raw, clazz, overlapping=True):
        duration = 1
        if overlapping:
            duration=0.5
        return mne.make_fixed_length_events(raw, clazz, duration=duration)

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
        ica = ICA(n_components=0.95, method='fastica', max_iter=500)

        picks = mne.pick_types(mneObj.info, meg=False, eeg=True, eog=False, stim=False, exclude='bads')
        reject = dict()#dict(grad=4000e-13, mag=4e-12, eog=150e-6, eeg=40e-6)
        ica.fit(mneObj, picks=picks, decim=3, reject=reject)#, reject=dict())
        ica.plot_components()
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

    def plotPSDTopo(self, mneObj):
        layout = mne.channels.read_layout('EEG1005')
        mneObj.plot_psd_topo(tmax=30., fmin=5., fmax=60., n_fft=128, layout=layout)
        layout.plot()

    def plotSensors(self, mneObj):
        mneObj.plot_sensors(kind='3d', ch_type='eeg', show_names=True)

if __name__ == '__main__':
    path = os.path.dirname(os.path.abspath(__file__)) +  "/../../../captured_data/test_data/"
    util = MNEUtil()
    awakeData = EEGTableFileUtil().readFile(path + "awake_full.csv")
    drowsyData = EEGTableFileUtil().readFile(path + "drowsy_full.csv")
    #epochs = util.createMNEEpochsObject(awakeData, drowsyData)
    #epochs.plot(block=True)
    raw = util.createMNEObjectFromDto(awakeData)
#    util.ICA(raw)
