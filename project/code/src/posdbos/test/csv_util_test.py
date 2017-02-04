#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 20.01.2017

:author: Paul Pasler
:organization: Reutlingen University
'''

from base_test import *  # @UnusedWildImport

from os.path import isfile
from numpy.testing.utils import assert_array_equal

from posdbos.util.csv_util import CSVUtil


class CSVUtilTest(BaseTest):

    def setUp(self):
        self.reader = CSVUtil()

    def test_readData(self):
        file_path = self.getData32CSV()
        self.reader.readData(file_path)

    def test_readHeader(self):
        file_path = self.getData32CSV()
        self.reader.readHeader(file_path)

    def testreadEEGFile(self):
        file_path = self.getData32CSV()
        self.reader.readEEGFile(file_path)

    def test_writeFile(self):
        filePath = self.PATH + "test.csv"
        header= ["Timestamp", "B", "C"]
        data = np.array([[1, 1.123456789, 2], [2, -4.123456789, 6], [3, 7.123456789, 99.123]])
        self.reader.writeFile(filePath, data, header)
        
        if isfile(filePath):
            read = self.reader.readEEGFile(filePath)

            for i in range(len(data)):
                for j in range(len(data[i])):
                    self.assertAlmostEqual(data[i, j], read.data[i, j], delta= 0.001)

        self.removeFile(filePath)

    def test_writeStructredFile(self):
        filePath = self.PATH + "test_structured.csv"
        data = {
            "A": {
                "value": [1, 2, 3],
                "quality": [-1, -1, -1]
            },
            "B": {
                "value": [4, 5, 6],
                "quality": [-2, -2, -2]
            },
            "C": {
                "value": [7, 8, 9],
                "quality": [-3, -3, -3]
            }
        }
        self.reader.writeStructredFile(filePath, data)
        
        if isfile(filePath):
            read = self.reader.readEEGFile(filePath)
            for key, values in data.iteritems():
                assert_array_equal(values["value"], read.getColumn(key))
        self.removeFile(filePath)

    @unittest.skip("There should be no empty values")
    def test_readEEGFile_NaNValues(self):
        eegData = self.reader.readEEGFile(self.PATH + "example_32_empty.csv")
        emptyCol = eegData.getColumn("Y")
        self.assertTrue(np.isnan(emptyCol).any())

        nonEmptyCol = eegData.getColumn("F3")
        self.assertFalse(np.isnan(nonEmptyCol).any())

    def test_readEEGFile_SeparatorFallback(self):
        eegData = self.reader.readEEGFile(self.getData32CSV())
        semicolonData = eegData.getColumn("F3")

        eegData = self.reader.readEEGFile(self.PATH + "example_32_comma.csv")
        commaData = eegData.getColumn("F3")

        self.assertTrue((semicolonData == commaData).all())

    @unittest.skip("delete Z-Column leads to memory error")
    def test_readEEGFile_newStyle(self):
        _ = self.reader.readEEGFile(self.PATH + "example_1024_new.csv")

    def test_readEEGFile(self):
        self.eegData = self.reader.readEEGFile(self.getData32CSV())
        self.assertTrue(self.eegData.hasEEGData)
        self.assertFalse(self.eegData.hasECGData)

    def test_readECGFile(self):
        self.ecgData = self.reader.readECGFile(self.PATH + "example_4096_ecg.csv")
        self.assertFalse(self.ecgData.hasEEGData)
        self.assertTrue(self.ecgData.hasECGData)

    def test_transformTimestamp_ecg(self):
        header = ["Timestamp", "ECG"]
        data = np.array([["05/12/2016 13:58:59.407","3798"],
                         ["05/12/2016 13:58:59.408","3798"],
                         ["05/12/2016 13:58:59.409","3798"],
                         ["05/12/2016 13:58:59.410","3798"],
                         ["05/12/2016 13:58:59.411","3798"]])
        ecgData = self.reader.transformTimestamp(header, data)
        self.assertAlmostEquals(float(ecgData[0][0]), 1480942739., delta=1.)

    def test_transformTimestamp_eeg(self):
        header = ["Timestamp", "F3", "X"]
        data = np.array([["2016-12-19 08:18:38.415000","-3200","0"],
                         ["2016-12-19 08:18:38.423000","-3171","0"],
                         ["2016-12-19 08:18:38.430000","-3184","0"],
                         ["2016-12-19 08:18:38.438000","-3176","0"],
                         ["2016-12-19 08:18:38.446000","-3172","0"]])
        eegData = self.reader.transformTimestamp(header, data)
        self.assertAlmostEquals(float(eegData[0][0]), 1482131918., delta=1.)


if __name__ == '__main__':
    unittest.main()