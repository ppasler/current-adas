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
from numpy import array_equal
from numpy.testing.utils import assert_array_equal


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

PATH = os.path.dirname(os.path.abspath(__file__)) +  "/../../examples/"

def readData():
    return EEGTableFileUtil().readFile(PATH + "example_1024.csv")


class MNEUtilTest(unittest.TestCase):

    def setUp(self):
        self.mne = MNEUtil()
        self.config = ConfigProvider().getEmotivConfig()
        self.eegData = readData()

    def test_createInfo(self):
        channels = self.config.get("eegFields")
        samplingRate = self.config.get("samplingRate")

        info = self.mne._createInfo(channels, "testFile")
        self.assertEquals(info["sfreq"], samplingRate)
        self.assertEquals(info["nchan"], len(channels))
        self.assertItemsEqual(info["ch_names"], channels)

    def test_rawCreation(self):
        self.mne.createMNEObject(self.eegData)

    def test_convertMNEToEEGTableDto(self):
        mneObj = self.mne.createMNEObject(self.eegData)
        eegData2 = self.mne.convertMNEToEEGTableDto(mneObj)
        self.assertListEqual(self.eegData.getEEGHeader(), eegData2.getHeader())
        array_equal(self.eegData.getEEGData(), eegData2.getData())
        self.assertEqual(self.eegData.filePath, eegData2.filePath)

    def test__createMNEEpochsObject(self):
        self.mne._createMNEEpochsObject(self.eegData.getEEGData(), self.eegData.getEEGHeader(), "../test.csv")

    @unittest.skip("error")
    def test_createMNEEpochsObject(self):
        awakeData = self.eegData
        drowsyData = readData()

        epochData = self.mne.createMNEEpochsObject(awakeData, drowsyData)
        self.assertEqual(len(epochData["awake"]), 15)
        self.assertEqual(len(epochData["drowsy"]), 15)

    def test_getChannels(self):
        channels = ["AF3", "F3"]
        raw = self.mne.createMNEObject(self.eegData)
        chanObj = self.mne.getChannels(raw, channels)
        self.assertEqual(chanObj.info["nchan"], len(channels))

    @unittest.skip("todo")
    def test_ICA(self):
        raw = self.mne.createMNEObject(self.eegData)
        print self.mne.ICA(raw)

    def test_EventArray(self):
        raw = self.mne.createMNEObject(self.eegData)
        ev_arr1 = mne.make_fixed_length_events(raw, 1, duration=0.5)
        ev_arr2 = self.mne._createEventsArray(self.eegData.getValueCount()/128)
        assert_array_equal(ev_arr1, ev_arr2)

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
