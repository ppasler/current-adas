#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 20.01.2017

:author: Paul Pasler
:organization: Reutlingen University
'''

from base_test import *  # @UnusedWildImport

from numpy.testing.utils import assert_array_equal
from posdbos.util.table_dto import TableDto


class TestTableDto(BaseTest):

    def setUp(self):
        self.header = ["Timestamp", "X", "Y", "AF3", "F3", "ECG"]
        self.data = np.array([
            [1456820379.00, 1, 2, 3, 9, 0],
            [1456820379.25, 1, 2, 4, 9, 1],
            [1456820379.50, 1, 2, 5, 9, 0],
            [1456820379.75, 1, 2, 6, 9, 1],
            [1456820380.00, 1, 2, 7, 9, 0],
            [1456820380.25, 1, 2, 8, 9, 1],
            [1456820380.50, 1, 2, 9, 9, 0],
            [1456820380.75, 1, 2, 10, 9, 1],
            [1456820381.00, 1, 2, 11, 9, 0]
        ])
        self.eegData = TableDto(self.header, self.data)

    def test_getSamplingRate(self):
        # 9 values within 2 seconds = sampling rate 4.5
        self.assertTrue(self.eegData.getSamplingRate() == 4.5)

    def test_getColumn(self):
        for i, header in enumerate(self.header[1:3]):
            column = self.eegData.getColumn(header)
            # make sure data columns only contain X:1, Y:2
            self.assertTrue(self.countOcc(column, i+1) == len(self.data))

    def test_getColumn_withOffset(self):
        offset = 3
        column = self.eegData.getColumn("AF3", offset)
        self.assertTrue(len(column) == len(self.data)-offset)
        assert_array_equal(column, [6, 7, 8, 9, 10, 11])

    def test_getColumn_withOffsetAndLimit(self):
        offset = 3
        limit = 7
        column = self.eegData.getColumn("AF3", offset, limit)
        self.assertTrue(len(column) == limit-offset)
        assert_array_equal(column, [6, 7, 8, 9])

    def test_getColumn_withOffsetAndLength(self):
        offset = 2
        length = 5
        column = self.eegData.getColumn("AF3", offset, length=length)
        self.assertTrue(len(column) == length)
        assert_array_equal(column, [5, 6, 7, 8, 9])

    def test_getColumn_withOffsetAndLimitAndLength(self):
        offset = 1
        limit = 7
        # length is ignored in this case
        length = 3
        column = self.eegData.getColumn("AF3", offset, limit, length=length)
        self.assertTrue(len(column) == limit-offset)
        assert_array_equal(column, [4, 5, 6, 7, 8, 9])

    def test_getTimeIndex(self):
        self.assertTrue(self.eegData.getTimeIndex(1456820379.00) == 0)
        self.assertTrue(self.eegData.getTimeIndex(1456820379.75) == 3)
        self.assertTrue(self.eegData.getTimeIndex(1456820381) == 8)

    def test_getTimeIndex_notExactly(self):
        self.assertTrue(self.eegData.getTimeIndex(1456820379.00) == 0)
        self.assertTrue(self.eegData.getTimeIndex(1456820379.01) == 1)
        self.assertTrue(self.eegData.getTimeIndex(1456820379.5) == 2)
        self.assertTrue(self.eegData.getTimeIndex(1456820379.51) == 3)
        self.assertTrue(self.eegData.getTimeIndex(1456820379.74) == 3)
        self.assertTrue(self.eegData.getTimeIndex(1456820379.75) == 3)
        self.assertTrue(self.eegData.getTimeIndex(1456820379.76) == 4)
        self.assertTrue(self.eegData.getTimeIndex(1456820381) == 8)

    def test_getTimeIndex_outOfRange(self):
        with self.assertRaises(ValueError):
            self.eegData.getTimeIndex(1456820378.00)

        with self.assertRaises(ValueError):
            self.eegData.getTimeIndex(1456820382.00)

    def test_getColumnByTime(self):
        column = self.eegData.getColumnByTime("AF3", 1456820379.00, 1456820379.75)
        assert_array_equal(column, [3, 4, 5])

        column2 = self.eegData.getColumnByTime("AF3", 1456820379.00, 1456820381)
        assert_array_equal(column2, [3, 4, 5, 6, 7, 8, 9, 10])

    def test_getColumnByTime_notExactly(self):
        column = self.eegData.getColumnByTime("AF3", 1456820379.00, 1456820379.75)
        assert_array_equal(column, [3, 4, 5])
        
        column2 = self.eegData.getColumnByTime("AF3", 1456820379.01, 1456820379.75)
        assert_array_equal(column2, [4, 5])

        column3 = self.eegData.getColumnByTime("AF3", 1456820379.00, 1456820379.74)
        assert_array_equal(column3, [3, 4, 5])

        column4 = self.eegData.getColumnByTime("AF3", 1456820379.00, 1456820379.76)
        assert_array_equal(column4, [3, 4, 5, 6]) 


    def test_getColumnByTime_outOfRange(self):
        with self.assertRaises(ValueError):
            self.eegData.getColumnByTime("AF3", 1456820378.00, 1456820379.75)

        with self.assertRaises(ValueError):
            self.eegData.getColumnByTime("AF3", 1456820379.00, 1456820382.0)

    def test__switchTime(self):
        x, y = 1, 2
        a, b = self.eegData._switchTime(x, y)
        self.assertEqual(x, b)
        self.assertEqual(y, a)

    def test__timeInData(self):
        data = self.eegData.getColumn("Timestamp")
        self.assertTrue(self.eegData._timeInData(data, 1456820379.75))
        self.assertFalse(self.eegData._timeInData(data, 1456820378))
        self.assertFalse(self.eegData._timeInData(data, 1456820382))

    def test_getValueCount(self):
        count = self.eegData.getValueCount()
        self.assertEquals(count, 9)

    def test_getEEGHeader(self):
        self.assertListEqual(self.eegData.getEEGHeader(), ["AF3", "F3"])

    def test_getEEGData(self):
        self.assertEquals(len(self.eegData.getEEGData()), 2)

    def test_getECGHeader(self):
        self.assertEqual(self.eegData.getECGHeader(), "ECG")

    def test_getECGData(self):
        self.assertEquals(len(self.eegData.getECGData()), 1)

    def test_setDataTypes(self):
        self.assertTrue(self.eegData.hasEEGData)
        self.assertFalse(self.eegData.hasEEGQuality)
        self.assertTrue(self.eegData.hasECGData)

if __name__ == '__main__':
    unittest.main()