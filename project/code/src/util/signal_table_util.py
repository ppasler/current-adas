#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 10.05.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

import os
import re

from numpy import genfromtxt, delete, savetxt, transpose

from util.date_converter import DateConverter
from table_dto import TableDto

DEFAULT_DELIMITER = ";" # default delimiter for CSV file
TIMESTAMP_STRING = "Timestamp" # key which specifies the unix timestamp of the data

EMOKIT_TIME_PATTERN = "%Y-%m-%d %H:%M:%S.%f"
BIOHARNESS_TIME_PATTERN = '%d/%m/%Y %H:%M:%S.%f'

class TableFileUtil(object):
    '''
    This class reads *.csv files and creates SignalTable
    '''
    
    def __init__(self):
        self.delimiter = DEFAULT_DELIMITER

    def readHeader(self, filePath):
        '''
        Reads the first row of the table to create a list of header values
        by default the delimiter for the csv table is ";"
        if ";" is not found the delimiter is set to ",", which ist needed to readData the right way
        
        :param string:   filePath
        :param string:   delimiter   
        
        :return: header column
        :rtype: list
        '''
        with open(filePath, 'rb') as f:
            headerLine = f.readline().strip()
            if self.delimiter not in headerLine:
                self.delimiter = ","
            header = headerLine.split(self.delimiter)

        return header

    def _isNewFile(self, header):
        return any(" Value" in s for s in header)

    def _modifyHeader(self, header):
        header = [channel.replace(" Value", "") for channel in header]
        header = [self._replaceQuality(channel) for channel in header]
        return header

    def _replaceQuality(self, channel):
        regex = re.compile(r"^(.*) Quality$", re.IGNORECASE)
        match = regex.search(channel)
        if match is not None:
            return "Q" + match.group(1)
        return channel

    def readData(self, filePath):
        '''
        reads all rows of the table (except the first on) to create a 2D array of eeg values
        by default the delimiter for the csv table is ";"
        
        [
         ["timestamp_1", "val_1_1" ... "v_1_n"],
         ["timestamp_2", "val_2_1" ... "v_2_n"],
                ...
         ["timestamp_m", "val_m_1" ... "v_m_n"],
        ]
        
        :param string   filePath:
        :param string   delimiter:

        :return: data columns
        :rtype: array
        '''
        data = genfromtxt(filePath, delimiter=self.delimiter, dtype=str, skip_header=1)

        return data

    def readFile(self, filePath="", delimiter=DEFAULT_DELIMITER):
        if filePath == "":
            return None
        self.delimiter = delimiter

        header = self.readHeader(filePath)
        data = self.readData(filePath)

        if self._isNewFile(header):
            header = self._modifyHeader(header)
            # TODO causes memory error
            # zIndex = header.index("Z")
            # header.remove("Z")
            # data = delete(data, zIndex, 1)

        return header, data

    def readEEGFile(self, filePath="", delimiter=DEFAULT_DELIMITER):
        '''
        reads the given EEG file
        
        
        :param string filePath:
        :param string delimiter:
        
        :return: eeg data
        :rtype: EEGTabelUtil
        '''
        if filePath == "":
            return None

        header, data = self.readFile(filePath, delimiter)

        data = self.transformTimestamp(header, data)
        return TableDto(header, data.astype(float), filePath)

    def readECGFile(self, filePath="", delimiter=DEFAULT_DELIMITER):
        '''
        reads the given ECG file
        
        
        :param string filePath:
        :param string delimiter:
        
        :return: ecg data
        :rtype: ECGTabelUtil
        '''
        if filePath == "":
            return None

        header, data = self.readFile(filePath, delimiter)
        header[0] = TIMESTAMP_STRING
        header[1] = "ECG"

        data = self.transformTimestamp(header, data)
        return TableDto(header, data.astype(float), filePath)

    def transformTimestamp(self, header, data):
        if TIMESTAMP_STRING in header: 
            timestampIndex = header.index(TIMESTAMP_STRING)
            timestampColumn = data[:, timestampIndex]
            firstElement = timestampColumn[0]
    
            if not self._isFloat(firstElement):
                dateConverter = self._getConverter(firstElement)
                timestampColumn = [dateConverter.convertDate(dateString) for dateString in timestampColumn]
                data[:,0] = timestampColumn

        return data

    def _isFloat(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def _getConverter(self, dateString):
        dateConverter = DateConverter(EMOKIT_TIME_PATTERN, 1)
        if dateConverter.matchesDatePattern(dateString):
            return dateConverter
        dateConverter.setPattern(BIOHARNESS_TIME_PATTERN)
        return dateConverter

    def writeFile(self, filePath, data, header, delimiter=DEFAULT_DELIMITER):
        savetxt(filePath, data, delimiter=delimiter, header=delimiter.join(header), fmt="%0.3f", comments="")

    def writeStructredFile(self, filePath, data):
        header = []
        structData = []
        for i, (key, val) in enumerate(data.iteritems()):
            header.insert(i, key)
            header.append("Q"+key)
            
            values = val["value"]
            quality = val["quality"]
            structData.insert(i, values)
            structData.append(quality)

        self.writeFile(filePath, transpose(structData), header)

if __name__ == "__main__": # pragma: no cover
    e = TableFileUtil()
    
    scriptPath = os.path.dirname(os.path.abspath(__file__))
    eeg_data = e.readEEGFile("../../examples/example_1024_new.csv", ",")
    eeg_data2 = e.readEEGFile("../../examples/example_1024.csv", ";")
    ecg_data = e.readECGFile("../../examples/example_4096_ecg.csv", ",")
    print eeg_data.getData()[:,0]
    print eeg_data2.getData()[:,0]
    print ecg_data.getData()[:,0]
#    print ecg_data.getECGData()
#    print ecg_data.header
    