#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 19.09.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

from base_test import * # @UnusedWildImport

import mne

from config.config import ConfigProvider
from posdbos.util.file_util import FileUtil
from posdbos.util.mne_util import MNEUtil


class MNEUtilTest(BaseTest):

    def setUp(self):
        self.mne = MNEUtil()
        self.config = ConfigProvider().getEmotivConfig()
        self.eegData = self._readData()

    def _readData(self):
        return FileUtil().getDto(self.getData1024CSV())

    def _createTestData(self):
        header = ["F3", "F4", "AF3", "AF4"]
        data = np.random.rand(4,512)
        filePath = "test"
        return self.mne.createMNEObject(data, header, filePath, 128)


    def test_createMNEObjectFromDto_creation(self):
        self.mne.createMNEObjectFromEEGDto(self.eegData)

    def test_createMNEObject_creation(self):
        self.mne.createMNEObject(self.eegData.getEEGData(), self.eegData.getEEGHeader(), self.eegData.filePath, self.eegData.getSamplingRate())

    def test_createMNEObjectFromDto_getChannels(self):
        channels = ["AF3", "F3"]
        raw = self.mne.createMNEObjectFromEEGDto(self.eegData)
        chanObj = self.mne.getChannels(raw, channels)
        self.assertEqual(chanObj.info["nchan"], len(channels))

    def test__createInfo_creation(self):
        channels = self.config.get("eegFields")
        samplingRate = self.config.get("samplingRate")

        info = self.mne._createEEGInfo(channels, "testFile", 128)
        self.assertEquals(info["sfreq"], samplingRate)
        self.assertEquals(info["nchan"], len(channels))
        self.assertItemsEqual(info["ch_names"], channels)

    @unittest.skip("work in progress")
    def test_createMNEEpochsObject(self):
        epochs = self.mne.createMNEEpochsObject(self.eegData, 1)
        self.assertEqual(len(epochs.get_data()), 15)

    def test__createEventsArray_overlapping(self):
        raw = self._createTestData()
        event_id = dict(drowsy=1)
        events1 = self.mne._createEventsArray(raw, 1, False)
        epochs1 = mne.Epochs(raw, events=events1, event_id=event_id, tmin=0.0, tmax=0.99, add_eeg_ref=True)
        
        events2 = self.mne._createEventsArray(raw, 1)
        epochs2 = mne.Epochs(raw, events=events2, event_id=event_id, tmin=0.0, tmax=0.99, add_eeg_ref=True)

        for i in range(0, len(events1)):
            data1 = epochs1[i].get_data()
            data2 = epochs2[i*2].get_data()
            self.assertTrue((data1 == data2).all())

    @unittest.skip("todo")
    def test_ICA(self):
        raw = self.mne.createMNEObjectFromEEGDto(self.eegData)
        print self.mne.ICA(raw)

if __name__ == '__main__':
    unittest.main()
