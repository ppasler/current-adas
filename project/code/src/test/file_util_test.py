#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 20.01.2017

:author: Paul Pasler
:organization: Reutlingen University
'''

from base_test import *  # @UnusedWildImport

from numpy import array_equal
from util.csv_util import TIMESTAMP_STRING
from util.file_util import FileUtil
from util.mne_util import MNEUtil


class TestFileUtil(BaseTest):

    def setUp(self):
        self.util = FileUtil()

    def _readData(self):
        return self.util.getDto(self.getData1024())

    def test_isCSVFile(self):
        self.assertTrue(self.util.isCSVFile("path/to/sth.csv"))

        self.assertFalse(self.util.isCSVFile("path/.csv/sth.txt"))
        self.assertFalse(self.util.isCSVFile("path/to/sth.raw.fif"))
        self.assertFalse(self.util.isCSVFile("path/to/sth.ica.fif"))

    def test_getDto(self):
        dto = self.util.getDto(self.getData32())

    def test_convertMNEToTableDto(self):
        dto = self._readData()
        mneObj = MNEUtil().createMNEObjectFromEEGDto(dto)
        dto2 = self.util.convertMNEToTableDto(mneObj)

        self.assertListEqual([TIMESTAMP_STRING] + dto.getEEGHeader(), dto2.getHeader())
        array_equal(dto.getEEGData(), dto2.getData())
        self.assertEqual(dto.filePath, dto2.filePath)
        self.assertTrue(dto2.hasEEGData)


if __name__ == '__main__':
    unittest.main()