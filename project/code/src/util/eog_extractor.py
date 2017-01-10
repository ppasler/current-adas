#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 05.01.2017

:author: Paul Pasler
:organization: Reutlingen University
'''

import os

from config.config import ConfigProvider
from util.mne_util import MNEUtil


scriptPath = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_ICA_PATH = scriptPath + "/../../data/"

BLINK_LABEL = "blinks"

FRONTAL_SENSORS = ["AF3", "F7", "F3", "FC5", "FC6", "F4", "F8", "AF4"]
BAD_CHANNELS = ["T7", "P7", "O1", "O2", "P8", "T8"]

class EOGExtractor(object):
    '''
    Class to extract EOG signal from EEG
    '''

    def __init__(self):
        self.util = MNEUtil()
        self.eogChan = 2
        self.templateRaw = self.util.load(TEMPLATE_ICA_PATH + "blink.raw.fif")
        self.templateICA = self.util.loadICA(TEMPLATE_ICA_PATH + "blink.ica.fif")
        # TODO remove after merge #3886
        self.templateICA.labels_ = dict()
        #plotICA(self.templateRaw, self.templateICA)

    def labelEOGChannel(self, icas):
        self.util.labelArtefact(self.templateICA, self.eogChan, icas, BLINK_LABEL)

    def getEOGChannel(self, raw, ica, eogInd = None):
        eogInd = self._getEOGIndex(ica, eogInd)

        eog = raw.copy()
        eog = ica.get_sources(eog)

        dropNames = self._createDropNames(ica, eogInd)
        eog.drop_channels(dropNames)

        nameDict = {self._getICAName(eogInd[0]): "EOG"}
        eog.rename_channels(nameDict)
        
        typeDict = {"EOG": "eog"}
        eog.set_channel_types(typeDict)
        #eog.plot(show=False, scalings=dict(eog=10), title=" eog")
        return eog

    def _getEOGIndex(self, ica, eogInd):
        if eogInd is None:
            eogInd = ica.labels_[BLINK_LABEL]
        return eogInd

    def _createDropNames(self, ica, eogInd):
        ind = range(ica.n_components_)
        return [self._getICAName(i) for i in ind if i not in eogInd]

    def _getICAName(self, number):
        # TODO remove '+ 1' after #3889
        return 'ICA %03d' % (number + 1)

    def removeEOGChannel(self, raw, ica, eogInd = None):
        eogInd = self._getEOGIndex(ica, eogInd)
        return ica.apply(raw, exclude=eogInd)
        

def plotICA(raw, ica):
    picks=None
    ica.plot_components(inst=raw, colorbar=True, show=False, picks=picks)
    ica.plot_sources(raw, show=False, picks=picks)
    #ica.plot_properties(raw, picks=0, psd_args={'fmax': 35.})

def createICAList():
    util = MNEUtil()
    icas_from_other_data = list()
    raw_from_other_data = list()
    probands = ConfigProvider().getExperimentConfig().get("probands")
    for proband in probands:
        filePath = "E:/thesis/experiment/" + proband + "/EEG"
        raw = util.load(filePath + ".raw.fif")
        ica = util.ICA(raw)
        raw_from_other_data.append(raw)
        icas_from_other_data.append(ica)
    return raw_from_other_data, icas_from_other_data

def saveICAList(icas):
    util = MNEUtil()
    probands = ConfigProvider().getExperimentConfig().get("probands")
    for i, proband in enumerate(probands):
        filePath = "E:/thesis/experiment/" + proband + "/EEG"
        util.saveICA(icas[i], filePath)

def loadICAList():
    util = MNEUtil()
    icas_from_other_data = list()
    raw_from_other_data = list()
    probands = ConfigProvider().getExperimentConfig().get("probands")
    for proband in probands:
        filePath = "E:/thesis/experiment/" + proband + "/EEG"
        raw = util.load(filePath + ".raw.fif")
        ica = util.loadICA(filePath + ".ica.fif")

        raw_from_other_data.append(raw)
        icas_from_other_data.append(ica)
    return raw_from_other_data, icas_from_other_data

def excludeAndPlotRaw(raw, ica, exclude, title=""):
    raw1 = raw.copy()
    ica.apply(raw1, exclude=exclude)
    raw.plot(show=False, scalings=dict(eeg=300), title=title + " raw")
    raw1.plot(show=False, scalings=dict(eeg=300), title=title + " eog")


if __name__ == '__main__':
    from mne.viz.utils import plt_show
    util = MNEUtil()

    extractor = EOGExtractor()
    raws, icas = createICAList()
    extractor.labelEOGChannel(icas)
    raw, ica = raws[1], icas[1]

    eogRaw = extractor.getEOGChannel(raw, ica)
    raw = extractor.removeEOGChannel(raw, ica)
    util.addEOGChannel(raw, eogRaw)
    util.plotRaw(raw)
    plt_show()

    #s = raw_input("save: ")
    #if s == "y":
    #    saveICAList(icas)
