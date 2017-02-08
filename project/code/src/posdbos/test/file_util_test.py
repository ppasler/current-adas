#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 20.01.2017

:author: Paul Pasler
:organization: Reutlingen University
'''

from base_test import *  # @UnusedWildImport

from numpy.testing.utils import assert_array_equal

from posdbos.util.csv_util import TIMESTAMP_STRING
from posdbos.util.file_util import FileUtil
from posdbos.util.mne_util import MNEUtil


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

    def test_getDto_dtoinput(self):
        dto = self.util.getDto(self.getData1024CSV())
        dto2 = self.util.getDto(dto)

        self.assertTrue(dto is dto2)
        self.assertAlmostEqual(dto.samplingRate, dto2.samplingRate, delta=0.1)
        assert_array_equal(dto.getEEGHeader(), dto2.getEEGHeader())
        assert_array_equal(dto.getEEGData(), dto2.getEEGData())

    def test_convertMNEToTableDto(self):
        dto2 = self.util.convertMNEToTableDto(self.mneObj)

        self.assertListEqual([TIMESTAMP_STRING] + self.dto.getEEGHeader() + self.dto.getGyroHeader(), dto2.getHeader())
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

    def test_getPartialDto(self):
        end = len(self.dto) / 2
        copyDto = self.util.getPartialDto(self.dto, 0, end)

        self.assertFalse(self.dto is copyDto)
        self.assertFalse(self.dto.header is copyDto.header)
        assert_array_equal(self.dto.header, copyDto.header)
        self.assertTrue(self.dto.filePath == copyDto.filePath)
        self.assertTrue(self.dto.samplingRate == copyDto.samplingRate)

        partData = copyDto.data
        fullData = self.dto.data

        self.assertFalse(fullData is partData)
        assert_array_equal(fullData[0:end,:], partData)
        self.assertEqual(len(partData), end)
        self.assertTrue(fullData.shape[0] > partData.shape[0])
        self.assertTrue(fullData.shape[1] == partData.shape[1])

if __name__ == '__main__':
    unittest.main()