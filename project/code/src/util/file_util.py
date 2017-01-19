#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 19.01.2017

:author: Paul Pasler
:organization: Reutlingen University
'''

CSV_EXTENSION = ".csv"
RAW_EXTENSION = ".raw.fif"
ICA_EXTENSION = ".ica.fif"

class FileUtil(object):

    def getDtoFromCsv(self, tableFileUtil, filePath):
        return tableFileUtil.readEEGFile(filePath)

    def getDtoFromFif(self, mneUtil, filePath):
        mneObj = mneUtil.load(filePath)
        return mneUtil.convertMNEToTableDto(mneObj)

    def isCSVFile(self, filePath):
        return filePath.endswith(CSV_EXTENSION)

    def getMNEFileName(self, filePath, mneObj):
        if filePath is None:
            filePath = mneObj.info["description"].replace(CSV_EXTENSION, "")
        filePath = self.addExtension(RAW_EXTENSION, filePath)
        return filePath

    def addExtension(self, extension, filePath):
        if not filePath.endswith(extension):
            filePath += extension
        return filePath