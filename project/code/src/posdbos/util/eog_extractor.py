#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 05.01.2017

:author: Paul Pasler
:organization: Reutlingen University
'''

import os

from numpy import mean

from posdbos.util.mne_util import MNEUtil
from posdbos.util.file_util import FileUtil
from mne.viz.utils import plt_show

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
        self.mneUtil = MNEUtil()
        self.fileUtil = FileUtil()
        self.eogChans = [2]
        self.templateICA = self.fileUtil.loadICA(TEMPLATE_ICA_PATH + "blink_.ica.fif")
        #self._plot()#print "load ICA ", "template", self.templateICA.get_components().shape

    def _plot(self):
        self.templateRaw = self.fileUtil.load(TEMPLATE_ICA_PATH + "blink_.raw.fif")
        self.templateICA.plot_components(show=False)
        self.templateICA.plot_sources(self.templateRaw, show=False)
        plt_show()

    def labelEOGChannel(self, icas):
        for eogChan in self.eogChans:
            self.mneUtil.labelArtefact(self.templateICA, eogChan, icas, BLINK_LABEL)

    def getEOGChannel(self, raw, ica, eogInds = None):
        eogInds = self._getEOGIndex(ica, eogInds)

        eog = raw.copy()
        eog = ica.get_sources(eog)

        eogChan = mean(raw._data[eogInds], axis=0)

        dropNames = self._createDropNames(ica, [0])
        eog.drop_channels(dropNames)

        raw._data[0] = eogChan
        nameDict = {self._getICAName(0): "EOG"}
        eog.rename_channels(nameDict)

        typeDict = {"EOG": "eog"}
        eog.set_channel_types(typeDict)

        return eog

    def _getEOGIndex(self, ica, eogInds):
        if eogInds is None:
            print "has EOG channel %s" % str(ica.labels_)
            eogInds = ica.labels_[BLINK_LABEL]
        return eogInds

    def _createDropNames(self, ica, eogInds):
        ind = range(ica.n_components_)
        return [self._getICAName(i) for i in ind if i not in eogInds]

    def _getICAName(self, number):
        # TODO remove '+ 1' after #3889
        return 'ICA %03d' % (number + 1)

    def removeEOGChannel(self, raw, ica, eogInd = None):
        eogInd = self._getEOGIndex(ica, eogInd)
        return ica.apply(raw, exclude=eogInd)