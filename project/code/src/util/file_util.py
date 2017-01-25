#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 19.01.2017

:author: Paul Pasler
:organization: Reutlingen University
'''
import re
from mne.io import read_raw_fif
from mne.preprocessing import read_ica
from numpy import swapaxes, copy

from util.csv_util import CSVUtil
from util.table_dto import TableDto


CSV_EXTENSION = ".csv"
RAW_EXTENSION = ".raw.fif"
ICA_EXTENSION = ".ica.fif"

class FileUtil(object):

    def getDto(self, filePath):
        if self.isCSVFile(filePath):
            return self.getDtoFromCsv(filePath)
        else:
            return self.getDtoFromFif(filePath)

    def getDtoFromCsv(self, filePath):
        return CSVUtil().readEEGFile(filePath)

    def getDtoFromFif(self, filePath):
        mneObj = self.load(filePath)
        return self.convertMNEToTableDto(mneObj)

    def getECGDto(self, filePath):
        return CSVUtil().readECGFile(filePath)

    def convertMNEToTableDto(self, mneObj):
        header = mneObj.ch_names
        data = swapaxes(mneObj._data, 0, 1)
        filePath = mneObj.info["description"]
        samplingRate = mneObj.info['sfreq']
        return TableDto(header, data, filePath, samplingRate)

    def isCSVFile(self, filePath):
        return filePath.endswith(CSV_EXTENSION)

    def saveCSV(self, filePath, data, header):
        CSVUtil().writeFile(filePath, data, header)

    def save(self, mneObj, filepath=None):
        filepath = self.getMNEFileName(mneObj, filepath)
        mneObj.save(filepath, overwrite=True)
        return filepath

    def load(self, filepath):
        '''A file with extension .raw.fif'''
        raw = read_raw_fif(filepath, add_eeg_ref=False, preload=True)
        return raw

    def saveICA(self, ica, filepath):
        filepath = self.addExtension(ICA_EXTENSION, filepath)
        ica.save(filepath)
        return filepath

    def loadICA(self, filepath):
        '''A file with extension .ica.fif'''
        return read_ica(filepath)

    def getMNEFileName(self, mneObj, filePath):
        if filePath is None:
            filePath = mneObj.info["description"]
        filePath = re.sub(CSV_EXTENSION +  "$", "", filePath)
        filePath = self.addExtension(RAW_EXTENSION, filePath)
        return filePath

    def addExtension(self, extension, filePath):
        if not filePath.endswith(extension):
            filePath += extension
        return filePath

    def getPartialDto(self, dto, start, end):
        data = dto.getPartialData(start, end)
        header = copy(dto.header)
        return TableDto(header, data, dto.filePath, dto.samplingRate)