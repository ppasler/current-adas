#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 20.01.2017

:author: Paul Pasler
:organization: Reutlingen University
'''

from math import sqrt, ceil

from numpy.testing.utils import assert_array_equal
from scipy.io import wavfile
from scipy.signal.filter_design import freqz

from base_test import *  # @UnusedWildImport
from config.config import ConfigProvider
from posdbos.util.fft_util import FFTUtil
from posdbos.util.signal_util import SignalUtil


class TestSignalUtil(BaseTest):

    def setUp(self):
        self.util = SignalUtil()

    def test_normalize(self):
        testList = np.array([0, -5, 1, 10])
        normList = self.util.normalize(testList)
        self.assertEqual(len(testList), len(normList))
        self.assertTrue(max(normList) <= 1)
        self.assertTrue(min(normList) >= -1)

    def test_normalize_value(self):
        norm = ConfigProvider().getProcessingConfig().get("normalize")
        testList = np.array([0, -5, 1, 10])
        normList = self.util.normalize(testList, norm)
        self.assertEqual(len(testList), len(normList))
        self.assertItemsEqual(normList, testList / norm)

    def test_normalize_zero(self):
        testList = np.array([0, 0, 0, 0])
        normList = self.util.normalize(testList)
        self.assertEqual(len(testList), len(normList))
        self.assertTrue(max(normList) <= 1)
        self.assertTrue(min(normList) >= -1)
        assert_array_equal(testList, normList)

    def test_normalize_NaN(self):
        testList = np.array([np.NaN, -2, -1, 0, np.NaN, 1, 2, np.NaN])
        normList = self.util.normalize(testList)
        self.assertEqual(len(testList), len(normList))
        self.assertTrue(np.nanmax(normList) <= 1)
        self.assertTrue(np.nanmin(normList) >= -1)

    def test_energy(self):
        testList = np.array([1, 2, 3, 4])
        energy = self.util.energy(testList)
        self.assertEqual(energy, 30)

    def test_maximum(self):
        testList = np.array([-5, 1, 2, 3, 4])
        maximum = self.util.maximum(testList)
        self.assertEqual(maximum, 4)

    def test_minimum(self):
        testList = np.array([-5, 1, 2, 3, 6])
        minimum = self.util.minimum(testList)
        self.assertEqual(minimum, -5)

    def test_mean(self):
        testList = np.array([0, 1, 2, 3, 4])
        mean = self.util.mean(testList)
        self.assertEqual(mean, 2)
    
    def test_var(self):
        testList = np.array([0, 1, 2, 3, 4])
        var = self.util.var(testList)
        self.assertEqual(var, 2)

    def test_std(self):
        testList = np.array([0, 1, 2, 3, 4])
        std = self.util.std(testList)
        self.assertEqual(std, sqrt(self.util.var(testList)))

    def test_zcr(self):
        testList = np.array([1, -1, 1, -1, 1])
        zcr = self.util.zcr(testList)
        self.assertEqual(zcr, 4)

    def test_zcr_zeros(self):
        testList = np.array([0, 0, 0, 0, 0])
        zcr = self.util.zcr(testList)
        self.assertEqual(zcr, 0)

        testList = np.array([1, 0, -1, 0, 1, 0, -1])
        zcr = self.util.zcr(testList)
        self.assertEqual(zcr, 3)

    def test_zcr_zeroChanges(self):
        testList = np.array([1, 1, 1, 1, 1])
        zcr = self.util.zcr(testList)
        self.assertEqual(zcr, 0)

        testList = np.array([-1, -1, -1, -1, -1])
        zcr = self.util.zcr(testList)
        self.assertEqual(zcr, 0)

    def test_nan_onOtherFunctions(self):
        norm = self.util.normalize(self.TEST_DATA_NAN)
        self.assertItemsEqual(np.isnan(norm), np.isnan(self.TEST_DATA_NAN))
        maxi = self.util.maximum(self.TEST_DATA_NAN)
        self.assertTrue(np.isnan(maxi))
        mini = self.util.minimum(self.TEST_DATA_NAN)
        self.assertTrue(np.isnan(mini))
        mean = self.util.mean(self.TEST_DATA_NAN)
        self.assertTrue(np.isnan(mean))
        var = self.util.var(self.TEST_DATA_NAN)
        self.assertTrue(np.isnan(var))
        std = self.util.std(self.TEST_DATA_NAN)
        self.assertTrue(np.isnan(std))
        energy = self.util.energy(self.TEST_DATA_NAN)
        self.assertTrue(np.isnan(energy))
        zcr = self.util.zcr(self.TEST_DATA_NAN)
        self.assertTrue(np.isnan(zcr))

    def test_mixed_onOtherFunctions(self):
        norm = self.util.normalize(self.TEST_DATA_MIXED)
        self.assertItemsEqual(np.isnan(norm), np.isnan(self.TEST_DATA_MIXED))
        maxi = self.util.maximum(self.TEST_DATA_MIXED)
        self.assertEquals(maxi, 1.0)
        mini = self.util.minimum(self.TEST_DATA_MIXED)
        self.assertEquals(mini, 0.0)
        mean = self.util.mean(self.TEST_DATA_MIXED)
        self.assertEquals(mean, 0.5)
        var = self.util.var(self.TEST_DATA_MIXED)
        self.assertEquals(var, 0.25)
        std = self.util.std(self.TEST_DATA_MIXED)
        self.assertEquals(std, 0.5)
        energy = self.util.energy(self.TEST_DATA_MIXED)
        self.assertEquals(energy, 2.0)
        zcr = self.util.zcr(self.TEST_DATA_MIXED)
        self.assertEquals(zcr, 0)


class TestFrequencyFilter(BaseTest):

    def setUp(self):
        self.util = SignalUtil()
        self._setSignalParams()
        
    def _setSignalParams(self, offset=0, length=-1):
        self.samplingRate, self.data= self._readSoundFile(offset=offset, length=length)
        self.n = len(self.data)
        self.nUniquePts = ceil((self.n+1)/2.0)

        self.freqArray = np.arange(0, self.nUniquePts, 1.0) * (self.samplingRate / self.n)
    
    def test_butterBandpass(self):
        samplingRate = 32
        i = samplingRate / 4
        b, a = self.util.butterBandpass(i-1, i+1, samplingRate)
        _, h = freqz(b, a, worN=samplingRate*4)
        h = abs(h)
        self.assertEqual(np.argmax(h), len(h)/2)
        self.assertAlmostEqual(max(h), 1, delta=0.1)
        self.assertAlmostEqual(h[0], 0, delta=0.01)
        self.assertAlmostEqual(h[len(h)-1], 0, delta=0.01)


    def test_butterBandpass_egde(self):
        # no signal allowed
        b, a = self.util.butterBandpass(5, 5, 16)
        _, h = freqz(b, a, worN=32)
        self.assertEquals(np.count_nonzero(abs(h)), 0)
        
        # everything gets through (except 0)
        b, a = self.util.butterBandpass(0, 8, 16)
        _, h = freqz(b, a, worN=16)
        self.assertAlmostEqual(sum(abs(h)), len(h)-1, delta = 1)
        
        b, a = self.util.butterBandpass(0.5, 8, 16)
        _, h = freqz(b, a, worN=16)
        self.assertAlmostEqual(sum(abs(h)), len(h)-1, delta = 1)
        
        b, a = self.util.butterBandpass(-1, 9, 16)
        _, h = freqz(b, a, worN=16)
        self.assertAlmostEqual(sum(abs(h)), len(h)-1, delta = 1)

    def test_butterBandpassFilter(self):
        x = [1, -1, 1, -1]
        _ = self.util.butterBandpassFilter(x, 1, 2, 10)
    
    def _readSoundFile(self, fileName='12000hz.wav', offset=0, length=-1):
        samplingRate, data = wavfile.read(self.PATH + fileName)
        if len(data.shape) == 2:
            data = data[:,0]
        
        if(length > -1):
            data = data[offset:offset+length]
        
        data = self.util.normalize(data)
        return samplingRate, data

    def _getMaxFrequency(self, data, freqArray):
        fft = FFTUtil().fft(data)
        return freqArray[np.argmax(fft)]

    def test_butterBandpassFilter_original(self):
        freqMax = self._getMaxFrequency(self.data, self.freqArray)
        self.assertAlmostEqual(freqMax, 12000.0, delta= 1000)

    def test_butterBandpassFilter_filterNoCut(self):
        cut = self.util.butterBandpassFilter(self.data, 1000, self.samplingRate/2-1000, self.samplingRate)
        freqMax = self._getMaxFrequency(cut, self.freqArray)
        self.assertAlmostEqual(freqMax, 12000.0, delta= 1000)

    def test_butterBandpassFilter_filterAroundMax(self):
        cut = self.util.butterBandpassFilter(self.data, 11000, 13000, self.samplingRate)
        freqMax = self._getMaxFrequency(cut, self.freqArray)
        self.assertAlmostEqual(freqMax, 12000.0, delta= 1000)
    
    def test_butterBandpassFilter_filterAboveMax(self):
        cut = self.util.butterBandpassFilter(self.data, 0, 2000, self.samplingRate)
        freqMax = self._getMaxFrequency(cut, self.freqArray)
        self.assertNotEqual(freqMax, 12000.0)
        self.assertAlmostEqual(freqMax, 1000.0, delta= 1000)
        
    def test_butterBandpassFilter_filterBeyondMax(self):
        cut = self.util.butterBandpassFilter(self.data, self.samplingRate/2-2000, self.samplingRate/2, self.samplingRate)
        freqMax = self._getMaxFrequency(cut, self.freqArray)
        self.assertNotEqual(freqMax, 12000.0)
        self.assertAlmostEqual(freqMax, self.samplingRate/2-1000, delta= 1000)

    def test_butterBandpassFilter_short(self):
        self._setSignalParams(length=4)
        freqMax = self._getMaxFrequency(self.data, self.freqArray)
        self.assertAlmostEqual(freqMax, 12000.0, delta= 1000)
        
        cut = self.util.butterBandpassFilter(self.data, 1000, self.samplingRate/2-1000, self.samplingRate)
        freqMax = self._getMaxFrequency(cut, self.freqArray)
        self.assertAlmostEqual(freqMax, 12000.0, delta= 1000)

    def test_butterBandpassFilter_originalAndShort(self):
        cutOrig = self.util.butterBandpassFilter(self.data, 1000, self.samplingRate/2-1000, self.samplingRate)
        freqMaxOrig = self._getMaxFrequency(self.data, self.freqArray)
        
        self._setSignalParams(length=4)
        cutShort = self.util.butterBandpassFilter(self.data, 1000, self.samplingRate/2-1000, self.samplingRate)
        freqMaxShort = self._getMaxFrequency(self.data, self.freqArray)
        
        self.assertAlmostEqual(freqMaxShort, freqMaxOrig, delta=1000)
        
        for i in range(len(cutShort)):
            self.assertAlmostEqual(cutOrig[i], cutShort[i], delta=0.02)


if __name__ == '__main__':
    unittest.main()