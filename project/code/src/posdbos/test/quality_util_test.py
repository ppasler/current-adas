#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 20.01.2017

:author: Paul Pasler
:organization: Reutlingen University
'''

from base_test import * # @UnusedWildImport

from posdbos.util.quality_util import QualityUtil


class TestQualityUtil(BaseTest):

    def setUp(self):
        self.util = QualityUtil()

    def test_replaceOutliners_withNaN(self):
        value = np.NaN
        testList = np.array([-10.0, -4, -3, -2, 0, 4, 5, 6, 10])
        self.assertEqual(self.countOcc(testList, value), 0)
        procList = self.util.replaceOutliners(testList, value, -3, 5)
        self.assertEqual(np.count_nonzero(np.isnan(procList)), 4)

    def test_replaceOutliners_withValue(self):
        value = -99
        testList = np.array([-10, -4, -3, -2, 0, 4, 5, 6, 10])
        self.assertEqual(self.countOcc(testList, value), 0)
        procList = self.util.replaceOutliners(testList, value, -3, 5)
        self.assertEqual(self.countOcc(procList, value), 4)

    def test_replaceOutliners_withoutValue(self):
        testList = np.array([-10, -4, -3, -2, 0, 4, 5, 6, 10])
        self.assertEqual(self.countOcc(testList, -3), 1)
        self.assertEqual(self.countOcc(testList, 5), 1)
        
        procList = self.util.replaceOutliners(testList, None, -3, 5)

        self.assertEqual(self.countOcc(procList, -3), 3)
        self.assertEqual(self.countOcc(procList, 5), 3)

    def test_isInvalidData(self):
        maxNaNValues = self.util.maxNaNValues
        windowSeconds = self.util.windowSeconds
        for length in range(maxNaNValues+1):
            testList = self._getNaNList(length)
            self.assertFalse(self.util.isInvalidData(testList))

        base = (maxNaNValues * windowSeconds) + windowSeconds
        for length in range(base + 1, base + 4):
            testList = self._getNaNList(length)
            self.assertTrue(self.util.isInvalidData(testList))

    def _getNaNList(self, length):
        return np.array([np.NaN]*length)

    def test_countOutliners(self):
        testList = np.array([-10.0, -4, -3, -2, 0, 4, 5, 6, 10])
        self.assertEqual(self.util.countOutliners(testList, -3, 5), 4)

    def test_countOutliners_defaultThreshold(self):
        lb = self.util.lowerBound
        ub = self.util.upperBound
        testList = np.array([lb-1, lb, lb+1, -2, 0, 4, ub-1, ub, ub+1])
        self.assertEqual(self.util.countOutliners(testList), 2)

    def test_countOutliners_noOccurence(self):
        testList = np.array([-10.0, -4, -3, -2, 0, 4, 5, 6, 10])
        self.assertEqual(self.util.countOutliners(testList, -11, 11), 0)

    def test_replaceBadQuality(self):
        value = 99
        testList = np.array([-10, -4, -3, -2, 0, 2, 4, 5, 6, 10])
        qualList = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        
        procList = self.util.replaceBadQuality(testList, qualList, value, 4)
        self.assertEqual(len(qualList), len(procList))
        self.assertEqual(self.countOcc(procList, value), 4)

    def test_replaceBadQuality_withNaN(self):
        value = np.NaN
        testList = np.array([-10.0, -4, -3, -2, 0, 2, 4, 5, 6, 10])
        qualList = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        
        procList = self.util.replaceBadQuality(testList, qualList, value, 4)
        self.assertEqual(len(qualList), len(procList))
        self.assertEqual(np.count_nonzero(np.isnan(procList)), 4)

    def test_replaceBadQuality_differentLengthError(self):
        value = np.NaN
        testList = np.array([-10.0, -4, -3, -2, 0, 2, 4, 5, 6, 10])
        qualList = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8])
        
        with self.assertRaises(ValueError):
            _ = self.util.replaceBadQuality(testList, qualList, value, 4)

    def test_countBadQuality(self):
        testList = np.array([-10.0, -4, -3, -2, 0, 2, 4, 5, 6, 10])
        qualList = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        
        count = self.util.countBadQuality(testList, qualList, 4)
        self.assertEqual(len(qualList), len(testList))
        self.assertEqual(count, 4)

    def test_countBadQuality_defaultThreshold(self):
        testList = np.array([-10.0, -4, -3, -2, 0, 2, 4, 5, 6, 10])
        minQuality = self.util.minQuality
        qualList = np.array([0, minQuality-1, minQuality, minQuality+1, 15, 15, 15, 15, 15, 15])
        
        count = self.util.countBadQuality(testList, qualList)
        self.assertEqual(len(qualList), len(testList))
        self.assertEqual(count, 1)

    def test_zeros(self):
        countZeros = self.util.countZeros(self.TEST_DATA_ZERO)
        self.assertEqual(countZeros, 10)
        self.assertNotEqual(countZeros, len(self.TEST_DATA_ZERO))
    
    def test_nans(self):
        countNans = self.util.countNans(self.TEST_DATA_NAN)
        self.assertEqual(countNans, 4)
        self.assertEqual(countNans, len(self.TEST_DATA_NAN))

    def test_nans_mixed(self):
        countNans = self.util.countNans(self.TEST_DATA_MIXED)
        self.assertEqual(countNans, 2)
        self.assertNotEqual(countNans, len(self.TEST_DATA_MIXED))

    #TODO make this flexible to maxSeqLength change
    @unittest.skip("fix leading zero is replaced")
    def test_replaceZeroSequences(self):
        zeros = np.array([0.0, -5.0, 0.0, 0, 2.0, 0.0, 0.0, 0.0, 3.5, 0, 0, 0, 0, 0, 1.0, 1.0, 1.0, 1.0, 1.0, 0, 0, 0, 0, 0, 0])
        l = self.util.replaceZeroSequences(zeros)
        self.assertNotEquals(self.util.countZeros(zeros), self.util.countZeros(l))
        self.assertEquals(self.util.countZeros(l), 6)
        self.assertEquals(self.util.countNans(l), 16)

    #TODO make this flexible to maxSeqLength change
    def test_replaceAnySequences(self):
        zeros = np.array([0, 0.0, 0.0, 0, 0, 2.0, 0, 2.0, 1.0, 1.0, 1.0, 1.0, 1.0])
        l = self.util.replaceSequences(zeros)
        self.assertNotEquals(self.util.countZeros(zeros), self.util.countZeros(l))
        self.assertEquals(self.util.countZeros(l), 1)
        self.assertEquals(self.util.countNans(l), 10)

    def test_countAnySequences(self):
        a = np.array([0, 0.0, 0.0, 0, 2.0, 0, 2.0, 1.0, 1.0, 1.0, 1.0, 1.0])
        l = self.util.countSequences(a)
        self.assertEquals(l, 1)

if __name__ == '__main__':
    unittest.main()