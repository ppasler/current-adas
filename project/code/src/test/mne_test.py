#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 19.09.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

import sys, os
import unittest

import mne
import numpy as np

from config.config import ConfigProvider
from util.eeg_table_util import EEGTableFileUtil
from util.mne_util import MNEUtil


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

PATH = os.path.dirname(os.path.abspath(__file__)) +  "/../../examples/"

class MNEUtilTest(unittest.TestCase):

    def setUp(self):
        self.mne = MNEUtil()
        self.config = ConfigProvider().getEmotivConfig()
        self.eegData = EEGTableFileUtil().readFile(PATH + "example_1024.csv")

    def test_createInfo(self):
        channels = self.config.get("eegFields")
        samplingRate = self.config.get("samplingRate")

        info = self.mne._createInfo(channels, "testFile")
        self.assertEquals(info["sfreq"], samplingRate)
        self.assertEquals(info["nchan"], len(channels))
        self.assertItemsEqual(info["ch_names"], channels)

    def test_rawCreation(self):
        self.mne.createRawObject(self.eegData)

    def test_getChannels(self):
        channels = ["AF3", "F3"]
        raw = self.mne.createRawObject(self.eegData)
        print raw.pick_channels(channels)

    def test_removeArtifacts(self):
        mneObj = self.mne.createRawObject(self.eegData)
        print mneObj.info
        self.mne.removeArtifacts(mneObj)

def testRawObject():
    # http://martinos.org/mne/stable/auto_tutorials/plot_creating_data_structures.html#creating-raw-objects
    # Generate some random data
    data = np.random.randn(5, 1000)
    # Initialize an info structure
    info = mne.create_info(
        ch_names=['MEG1', 'MEG2', 'EEG1', 'EEG2', 'EOG'],
        ch_types=['grad', 'grad', 'eeg', 'eeg', 'eog'],
        sfreq=100
    )
    
    custom_raw = mne.io.RawArray(data, info)
    print custom_raw

if __name__ == '__main__':
    unittest.main()
