#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 20.01.2017

:author: Paul Pasler
:organization: Reutlingen University
'''

from base_test import * # @UnusedWildImport

from util.eeg_util import EEGUtil
from util.file_util import FileUtil


class TestEEGUtil(BaseTest):

    def setUp(self):
        self.util = EEGUtil()

    def test__getSliceParams(self):
        for _, freqRange in self.util.channel_ranges.iteritems():
            self.assertEqual(type(self.util._getSliceParam(freqRange)[0]), int)

    def test_getChannels_short(self):
        data = [1, 2, 3, 4, 5, 6, 7, 8]

        channels = self.util.getChannels(data)
        self.assertTrue(len(channels) == 5)
        self.assertTrue(len(channels["delta"]) > 0)
        self.assertTrue(len(channels["theta"]) > 0)
        
        self.assertTrue(len(channels["alpha"]) == 0)

    def test_getChannels(self):
        fft = self.TEST_DATA_12000Hz

        channels = self.util.getChannels(fft)
        flattenChannels = np.hstack(channels.values())
        self.assertTrue(all([x in fft for x in flattenChannels]))
        
        self.assertTrue(len(flattenChannels) <= len(fft))

    def test_getSingleChannels(self):
        fft = self.TEST_DATA_12000Hz
        channels = self.util.getChannels(fft)

        delta = self.util.getDeltaChannel(fft)
        # TODO delta range from 0.5 to 4Hz, actual range from 1 - 4Hz
        self.assertEqual(len(delta), 3)
        self.assertTrue(all([x in channels["delta"] for x in delta]))
               
        theta = self.util.getThetaChannel(fft)
        self.assertEqual(len(theta), 4)
        self.assertTrue(all([x in channels["theta"] for x in theta]))
                
        alpha = self.util.getAlphaChannel(fft)
        self.assertEqual(len(alpha), 5)
        self.assertTrue(all([x in channels["alpha"] for x in alpha]))
                
        beta = self.util.getBetaChannel(fft)
        self.assertEqual(len(beta), 17)
        self.assertTrue(all([x in channels["beta"] for x in beta]))
          
        gamma = self.util.getGammaChannel(fft)
        self.assertEqual(len(gamma), len(range(*self.util.channel_ranges["gamma"])))
        self.assertTrue(all([x in channels["gamma"] for x in gamma]))

    def test_getWaves(self):
        eegData = FileUtil().getDto(self.PATH + "example_32.csv")
        eeg = eegData.getColumn("F3")
        nEeg = len(eeg)
        waves = self.util.getWaves(eeg, eegData.getSamplingRate())
        
        self.assertEqual(len(waves), 5)
        for _, wave in waves.iteritems():
            self.assertEqual(len(wave), nEeg)

    def test_getSingleWaves(self):
        eegData = FileUtil().getDto(self.PATH + "example_32.csv")
        eeg = eegData.getColumn("F3")
        nEeg = len(eeg)
        samplingRate = eegData.getSamplingRate()
        waves = self.util.getWaves(eeg, samplingRate)

        delta = self.util.getDeltaWaves(eeg, samplingRate)
        self.assertEqual(len(delta), nEeg)
        self.assertTrue(all([x in waves["delta"] for x in delta]))

        theta = self.util.getThetaWaves(eeg, samplingRate)
        self.assertEqual(len(theta), nEeg)
        self.assertTrue(all([x in waves["theta"] for x in theta]))

        alpha = self.util.getAlphaWaves(eeg, samplingRate)
        self.assertEqual(len(alpha), nEeg)
        self.assertTrue(all([x in waves["alpha"] for x in alpha]))

        beta = self.util.getBetaWaves(eeg, samplingRate)
        self.assertEqual(len(beta), nEeg)
        self.assertTrue(all([x in waves["alpha"] for x in alpha]))
          
        gamma = self.util.getGammaWaves(eeg, samplingRate)
        self.assertEqual(len(gamma), nEeg)
        self.assertTrue(all([x in waves["gamma"] for x in gamma]))


if __name__ == '__main__':
    unittest.main()