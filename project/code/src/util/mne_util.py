#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 19.09.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

import numpy as np
import mne
from mne.preprocessing.ica import ICA, corrmap
from mne.viz.utils import plt_show
from scipy import signal
from config.config import ConfigProvider
from util.signal_table_util import TableFileUtil, EEGTableDto


DEFAULT_SAMPLE_LENGTH = 1

class MNEUtil():

    def __init__(self):
        self.config = ConfigProvider()

    def createMNEObjectFromEEGDto(self, eegDto):
        return self.createMNEObject(eegDto.getEEGData(), eegDto.getEEGHeader(), eegDto.filePath, eegDto.getSamplingRate())

    def createMNEObject(self, data, header, filePath, samplingRate):
        info = self._createEEGInfo(header, filePath, samplingRate)
        return mne.io.RawArray(data, info)

    def createMNEObjectFromECGDto(self, ecgDto, resampleFac=None):
        info = self._createECGInfo(ecgDto.getECGHeader(), ecgDto.filePath, ecgDto.getSamplingRate())
        ecgData = ecgDto.getECGData()
        if resampleFac is not None:
            ecgData = signal.resample(ecgData, resampleFac)
        return mne.io.RawArray(ecgData, info)

    def _createECGInfo(self, channelName, filename, samplingRate):
        channelTypes = ["ecg"]
        info = mne.create_info([channelName], samplingRate, channelTypes)
        info["description"] = "PoSDBoS"
        info["filename"] = filename
        return info

    def _createEEGInfo(self, channelNames, filename, samplingRate):
        channelTypes = ["eeg"] * len(channelNames)
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
        raw = self.createMNEObjectFromEEGDto(eegData)
        events = self._createEventsArray(raw, clazz)
        return mne.Epochs(raw, events=events, tmin=0.0, tmax=0.99, add_eeg_ref=True)

    def _createEventsArray(self, raw, clazz, overlapping=True):
        duration = 1
        if overlapping:
            duration=0.5
        return mne.make_fixed_length_events(raw, clazz, duration=duration)

    def addECGChannel(self, eegRaw, ecgRaw):
        sFreq = eegRaw.info['sfreq']
        tMax = (eegRaw.n_times - 1) / sFreq

        ecgRaw = ecgRaw.resample(sFreq, npad='auto').crop(0, tMax)

        return eegRaw.add_channels([ecgRaw])

    def filterData(self, mneObj, upperFreq, lowerFreq):
        return mneObj.filter(upperFreq, lowerFreq, l_trans_bandwidth=0.5, h_trans_bandwidth=0.5,
               filter_length="10s", phase='zero-double', fir_window="hamming")

    def createPicks(self, mneObj):
        return mne.pick_types(mneObj.info, meg=False, eeg=True, eog=False, stim=False, exclude='bads')

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
        ica = ICA(n_components=14, method='fastica')

        picks = self.createPicks(mneObj)
        reject = dict(eeg=300)
        ica.fit(mneObj, picks=picks, reject=reject)
        # ica.plot_components()
        return ica

    def labelArtefact(self, templateICA, templateIC, icas, label):
        template = (0, templateIC)
        icas = [templateICA] + icas

        return corrmap(icas, template=template, threshold=0.85, label=label, show=False, ch_type='eeg', verbose=True)

    def plotCorrmaps(self, icas):
        n_components = icas[0].n_components_
        for i in range(len(icas)):
            for j in range(n_components):
                template = (i, j)
                fig_template, fig_detected = corrmap(icas, template=template, label="blinks",
                                                 show=False, ch_type='eeg', verbose=True)
                print i, j, fig_template, fig_detected

    def plotPSDTopo(self, mneObj):
        layout = mne.channels.read_layout('EEG1005')
        mneObj.plot_psd_topo(tmax=30., fmin=5., fmax=60., n_fft=128, layout=layout)
        layout.plot()

    def plotSensors(self, mneObj):
        mneObj.plot_sensors(kind='3d', ch_type='eeg', show_names=True)

if __name__ == '__main__':
    util = MNEUtil()
    sFreq = 100.

    eegFileName = "test_EEG.csv"
    eegData = TableFileUtil().readEEGFile(eegFileName)
    eegRaw = util.createMNEObjectFromEEGDto(eegData).resample(sFreq, npad='auto')

    ecgFileName = "test_ECG.csv"
    ecgData = TableFileUtil().readECGFile(ecgFileName)
    ecgRaw = util.createMNEObjectFromECGDto(ecgData)

    util.addECGChannel(eegRaw, ecgRaw)

    eegRaw.plot(show=False, title="Raw data", scalings=dict(eeg=300, ecg=500), duration=60.0, start=1000.0, n_channels=15)

    plt_show()

