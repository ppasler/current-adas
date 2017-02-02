#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 20.01.2017

:author: Paul Pasler
:organization: Reutlingen University
'''

from base_test import *  # @UnusedWildImport

from numpy.testing.utils import assert_array_equal
from posdbos.util.fft_util import FFTUtil


class TestFFTUtil(BaseTest):

    def setUp(self):
        self.util = FFTUtil()

    def test__removeMirrored(self):
        testList1 = np.array([0, 1, 2, 3, 4, 4, 3, 2, 1])
        mirrList = self.util._removeMirrored(testList1, len(testList1))
        self.assertEqual(len(mirrList), 5)

        testList2 = np.array([0, 1, 2, 3, 4, 3, 2, 1, 0])
        mirrList = self.util._removeMirrored(testList2, len(testList2))
        self.assertEqual(len(mirrList), 5)

    def test__process(self):
        testList = np.array([1, 2, -3, -4])
        procList = self.util._process(testList, len(testList))
        self.assertEqual(len(testList), len(procList))
        # absolute;     normalize 0,1;          **2
        # [1, 2, 3, 4]; [0.25, 0.5, 0.75, 1];   [0.0625, 0.25, 0.5625, 1] 
        assert_array_equal(procList, [0.0625, 0.25, 0.5625, 1])

    def test__doubleValues(self):
        # odd: first entry is not doubled
        testOddList = np.array([17, 3, 4, 5, 6])
        doubOddList = self.util._doubleValues(np.copy(testOddList))
        self.assertEqual(len(doubOddList), len(testOddList))
        self.assertTrue(all([x*2 in doubOddList for i, x in enumerate(testOddList) if 0 < i]))

        # even: first and last entry is not doubled
        testEvenList = np.array([17, 3, 4, 5, 6, 17])
        doubEvenList = self.util._doubleValues(np.copy(testEvenList))
        self.assertEqual(len(doubEvenList), len(testEvenList))
        self.assertTrue(all([x*2 in doubEvenList for i, x in enumerate(testEvenList) if 0 < i < len(testEvenList)-1]))

    def testFft(self):
        # 128 pts from a 12.000Hz tone with a sample rate of 44.100
        data = self.TEST_DATA_12000Hz
        samplingRate = 44100

        fft = self.util.fft(data)

        n = float(len(data))
        nUniquePts = np.ceil((n+1)/2.0)
        
        maxIndex = np.argmax(fft)

        # calc frequency array
        freqArray = np.arange(0, nUniquePts, 1.0) * (samplingRate / n);

        # should be around 12000
        self.assertTrue(11800 < freqArray[maxIndex] < 12200)

if __name__ == '__main__':
    unittest.main()