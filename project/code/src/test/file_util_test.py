#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 20.01.2017

:author: Paul Pasler
:organization: Reutlingen University
'''

from base_test import *  # @UnusedWildImport

from numpy.testing.utils import assert_array_equal

from util.csv_util import TIMESTAMP_STRING
from util.file_util import FileUtil
from util.mne_util import MNEUtil


class TestFileUtil(BaseTest):

    def setUp(self):
        self.util = FileUtil()
        self.dto = self._readData()
        self.mneObj = self._getMNEObject(self.dto)

    def _getMNEObject(self, dto):
        return MNEUtil().createMNEObjectFromEEGDto(dto)

    def _readData(self):
        return self.util.getDto(self.getData1024CSV())

    def test_isCSVFile(self):
        self.assertTrue(self.util.isCSVFile("path/to/sth.csv"))

        self.assertFalse(self.util.isCSVFile("path/.csv/sth.txt"))
        self.assertFalse(self.util.isCSVFile("path/to/sth.raw.fif"))
        self.assertFalse(self.util.isCSVFile("path/to/sth.ica.fif"))

    def test_getDto(self):
        dto = self.util.getDto(self.getData1024CSV())
        dto2 = self.util.getDto(self.getData1024FIF())

        self.assertAlmostEqual(dto.samplingRate, dto2.samplingRate, delta=0.1)
        assert_array_equal(dto.getEEGHeader(), dto2.getEEGHeader())
        assert_array_equal(dto.getEEGData(), dto2.getEEGData())

    def test_convertMNEToTableDto(self):
        dto2 = self.util.convertMNEToTableDto(self.mneObj)

        self.assertListEqual([TIMESTAMP_STRING] + self.dto.getEEGHeader(), dto2.getHeader())
        assert_array_equal(self.dto.getEEGData(), dto2.getEEGData())
        self.assertEqual(self.dto.filePath, dto2.filePath)
        self.assertTrue(dto2.hasEEGData)

    def test_getMNEFileName_given(self):
        filePath = "path/to/sth"
        mneFilePath = self.util.getMNEFileName(self.mneObj, filePath)
        self.assertEqual(filePath +  ".raw.fif", mneFilePath)

    def test_getMNEFileName_givenCSV(self):
        filePath = "path/to/sth"
        mneFilePath = self.util.getMNEFileName(self.mneObj, filePath + ".csv")
        self.assertEqual(filePath +  ".raw.fif", mneFilePath)

    def test_getMNEFileName_givenCSVmiddle(self):
        filePath = "path/.csv/sth"
        mneFilePath = self.util.getMNEFileName(self.mneObj, filePath)
        self.assertEqual(filePath +  ".raw.fif", mneFilePath)

    def test_getMNEFileName_extension(self):
        filePath = "path/to/sth"
        self.mneObj.info["description"] = filePath
        mneFilePath = self.util.getMNEFileName(self.mneObj, None)
        self.assertEqual(filePath +  ".raw.fif", mneFilePath)

    def test_getMNEFileName_CSV(self):
        filePath = "path/to/sth"
        self.mneObj.info["description"] = filePath +  ".csv"
        mneFilePath = self.util.getMNEFileName(self.mneObj, None)
        self.assertEqual(filePath +  ".raw.fif", mneFilePath)

if __name__ == '__main__':
    unittest.main()