#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 19.09.2016

:author: Paul Pasler
:organization: Reutlingen University
'''
import mne
from mne.preprocessing.ica import ICA, corrmap
from mne.preprocessing import read_ica
from scipy import signal
from numpy import swapaxes

from config.config import ConfigProvider
from util.signal_table_util import TableFileUtil
from util.table_dto import TableDto


DEFAULT_SAMPLE_LENGTH = 1

class MNEUtil():

    def __init__(self):
        self.config = ConfigProvider()

    def createMNEObjectFromCSV(self, filePath):
        eegData = TableFileUtil().readEEGFile(filePath)
        return self.createMNEObjectFromEEGDto(eegData)

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
        info["description"] = filename
        return info

    def _createEEGInfo(self, channelNames, filename, samplingRate):
        channelTypes = ["eeg"] * len(channelNames)
        montage = mne.channels.read_montage("standard_1020")
        info = mne.create_info(channelNames, samplingRate, channelTypes, montage)
        info["description"] =  filename
        return info

    def convertMNEToTableDto(self, mneObj):
        header = mneObj.ch_names
        data = swapaxes(mneObj._data, 0, 1)
        filePath = mneObj.info["description"]
        samplingRate = mneObj.info['sfreq']
        return TableDto(header, data, filePath, samplingRate)

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
        if "ecg" in ecgRaw:
            return self._addChannel(eegRaw, ecgRaw)

    def addEOGChannel(self, eegRaw, eogRaw):
        if "eog" in eogRaw:
            return self._addChannel(eegRaw, eogRaw)

    def _addChannel(self, eegRaw, otherRaw):
        otherRaw = self.adjustSampleRate(eegRaw, otherRaw)
        otherRaw = self.adjustLength(eegRaw, otherRaw)

        return eegRaw.add_channels([otherRaw], force_update_info=True)

    def adjustSampleRate(self, eegRaw, otherRaw):
        eegSFreq = eegRaw.info['sfreq']
        otherSFreq = otherRaw.info['sfreq']
        if eegSFreq != otherSFreq:
            otherRaw = otherRaw.resample(eegSFreq, npad='auto')
        return otherRaw

    def adjustLength(self, eegRaw, otherRaw):
        eegNTimes = eegRaw.n_times
        otherNTimes = otherRaw.n_times
        if eegNTimes != otherNTimes:
            eegSFreq = eegRaw.info['sfreq']
            tMax = (eegRaw.n_times - 1) / eegSFreq
            otherRaw = otherRaw.crop(0, tMax)
        return otherRaw

    def markBadChannels(self, raw, channels):
        raw.info['bads'] = channels

    def interpolateBadChannels(self, raw):
        return raw.interpolate_bads()

    def createPicks(self, mneObj):
        return mne.pick_types(mneObj.info, meg=False, eeg=True, eog=False, stim=False, exclude='bads')

    def bandpassFilterData(self, mneObj):
        highFreq = self.config.getProcessingConfig().get("upperFreq")
        lowFreq = self.config.getProcessingConfig().get("lowerFreq")
        return self.filterData(mneObj, lowFreq, highFreq)

    def filterData(self, mneObj, lowFreq, highFreq):
        return mneObj.filter(lowFreq, highFreq, filter_length="auto", l_trans_bandwidth="auto", 
                             h_trans_bandwidth="auto", phase='zero', fir_window="hamming")

    def getEEGCannels(self, mneObj):
        return mneObj.copy().pick_types(meg=False, eeg=True)

    def getChannels(self, mneObj, channels):
        return mneObj.copy().pick_channels(channels)

    def cropChannels(self, mneObj, tmin, tmax):
        return mneObj.copy().crop(tmin, tmax-1)

    def dropChannels(self, mneObj, channels):
        return mneObj.copy().drop_channels(channels)

    def ICA(self, mneObj, icCount=None):
        picks = self.createPicks(mneObj)
        reject = dict(eeg=300)

        if icCount is None:
            icCount = len(picks)
        ica = ICA(n_components=icCount, method='fastica')
        ica.fit(mneObj, picks=picks, reject=reject)
        # ica.plot_components()
        return ica

    def labelArtefact(self, templateICA, templateIC, icas, label):
        template = (0, templateIC)
        icas = [templateICA] + icas
        print icas
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

    def plotRaw(self, mneObj, title=None, show=False):
        scalings = dict(eeg=300, eog=10, ecg=100)
        color = dict(eeg="k", eog="b", ecg="r")
        if title is None:
            title = mneObj.info["description"]
        n_channels = len(mneObj.ch_names)
        return mneObj.plot(show=show, scalings=scalings, color=color, title=title, duration=60.0, n_channels=n_channels)

    def save(self, mneObj, filepath=None):
        if filepath is None:
            filepath = mneObj.info["description"].replace(".csv", "")
        filepath += ".raw.fif"
        mneObj.save(filepath, overwrite=True)
        return filepath

    def load(self, filepath):
        '''A file with extension .raw.fif'''
        raw = mne.io.read_raw_fif(filepath, add_eeg_ref=False, preload=True)
        return raw

    def saveICA(self, ica, filepath):
        extension = ".ica.fif"
        if not filepath.endswith(extension):
            filepath += extension
        ica.save(filepath)
        return filepath

    def loadICA(self, filepath):
        '''A file with extension .ica.fif'''
        return read_ica(filepath)

if __name__ == '__main__':
    util = MNEUtil()