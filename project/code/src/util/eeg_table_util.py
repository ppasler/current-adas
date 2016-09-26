#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 10.05.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

import os

from numpy import genfromtxt, delete, shape, savetxt, transpose, array
from config.config import ConfigProvider


DEFAULT_DELIMITER = ";" # default delimiter for CSV file
TIMESTAMP_STRING = "Timestamp" # key which specifies the unix timestamp of the data

class EEGTableDto(object):
    '''
    Representation of EEG table data
    '''

    def __init__(self, header=None, data=None, filePath=""):
        '''
        table data with header, data and the filepath
        
        :param header:
        :param data:
        :param filePath:
        '''
        self.filePath = filePath
        self.header = header
        self.data = data
        if data is not None:
            self.len = len(data)

    def setHeader(self, header):  # pragma: no cover
        self.header = header

    def setData(self, data):  # pragma: no cover
        self.data = data
        self.len = len(data)

    def getHeader(self):  # pragma: no cover
        return self.header

    def getData(self):  # pragma: no cover
        return self.data

    def getEEGHeader(self):
        eegFields = ConfigProvider().getEmotivConfig().get("eegFields")
        return [head for head in self.header if head in eegFields]

    def getEEGData(self):
        eegFields = self.getEEGHeader()
        # TODO make me nice
        eegData = []
        for eegField in eegFields:
            eegData.append(self.getColumn(eegField))
        return array(eegData)

    def getTimeIndex(self, fromTime):
        '''
        get the index for the given fromTime
        if fromTime < min(timestamp) return 0
        if fromTime > max(timestamp) return len(data)
        
        :param    float   fromTime:    time as unix timestamp 
        
        :return   int     the index of the given fromTime 
        '''
        data = self.getColumn(TIMESTAMP_STRING)
        if not self._timeInData(data, fromTime):
            raise ValueError('could not find %f in data' % fromTime)
        
        for i, time in enumerate(data):
            if time >= fromTime:
                return i

    def getTime(self, offset=0, limit=-1, length=-1):
        return self.getColumn(TIMESTAMP_STRING, offset, limit, length)

    def getQuality(self, columnName, offset=0, limit=-1, length=-1):
        return self.getColumn("Q" + columnName, offset, limit, length)

    def getColumn(self, columnName, offset=0, limit=-1, length=-1):
        '''
        get dataset from a certain column, either from offset to limit or till length
        if only column_name is specified, it returns the whole column
        if offset and length are both defined, length will be ignored
        
        :param     string column_name:   the name of the column
        :param     int    offset:        startindex of dataset
        :param     int    limit:         endpoint of dataset
        :param     int    length:        length of dataset
        
        :return: dataset for given column
        :rtype: array
        '''
        
        if columnName not in self.header:
            return None

        if limit == -1:
            if  length == -1:
                limit = self.len
            else:
                limit = offset+length

        index = self.header.index(columnName)
        return self.data[:, index][offset:limit]      

    def getColumnByTime(self, columnName, fromTime, toTime):
        '''
        get dataset from a certain column, for a time interval (fromTime -> toTime)
             
        :param string    columnName:   the name of the column 
        :param float     fromTime:     start time of dataset as unix timestamp   
        :param float     toTime:       start time of dataset as unix timestamp
        
        :return: dataset for given column
        :rtype: array 
        
        :raise: ValueError if time could not be found in dataset 
        '''
        fromIndex, toIndex = -1, -1

        if fromTime > toTime:
            fromTime, toTime = self._switchTime(fromTime, toTime)
        
        data = self.getColumn(TIMESTAMP_STRING)
        
        if not self._timeInData(data, fromTime):
            raise ValueError('could not find %f in data' % fromTime)

        if not self._timeInData(data, toTime):
            raise ValueError('could not find %f in data' % toTime)

        for i, time in enumerate(data):
            if time >= fromTime and fromIndex == -1:
                fromIndex = i
            if time >= toTime:
                toIndex = i
                break

        return self.getColumn(columnName, fromIndex, toIndex)


    def getDuration(self):
        '''
        get the duration for the current data
        
        :return: duration
        :rtype: long

        '''
        data = self.getTime()
        duration = data[self.len - 1] - data[0]
        return duration

    def getSamplingRate(self):
        '''
        calcs the samplerate for the whole dataset based on the timestamp column   
        
        :return: samplerate
        :rtype: int

        '''
        duration = self.getDuration()
        return self.len / duration  

    def getStartTime(self):
        '''
        get the first value from the timestamp column

        :return: start time
        :rtype: long

        '''
        return self.getTime()[0]

    def getEndTime(self):
        '''
        get the last value from the timestamp column
        
        :return: end time
        :rtype: long

        '''
        return self.getTime()[self.len-1]

    def getValueCount(self):
        return len(self.getColumn(self.header[0]))

    def _switchTime(self, time1, time2):
        return time2, time1

    def _timeInData(self, data, time):
        return (min(data) <= time <= max(data))

    def __repr__(self):
        return "EEGTableDto from '%s' shape %s\nheader %s" % (self.filePath, shape(self.data), self.header)

class EEGTableFileUtil(object):
    '''
    This class reads EEGTables created by emotiv.py
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
        data = delete(genfromtxt(filePath, dtype=float, delimiter=self.delimiter), 0, 0)
        return data

    def readFile(self, filePath="", delimiter=DEFAULT_DELIMITER):
        '''
        reads the given file
        
        
        :param string filePath:
        :param string delimiter:
        
        :return: eeg data
        :rtype: EEGTabelUtil
        '''
        if filePath == "":
            return None

        header = self.readHeader(filePath)
        data = self.readData(filePath)

        return EEGTableDto(header, data, filePath)

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
    e = EEGTableFileUtil()
    #eeg_data = e.readFile("example_full.csv")
    scriptPath = os.path.dirname(os.path.abspath(__file__))
    eeg_data = e.readFile(scriptPath + "/../../examples/example_32.csv")
    
    print eeg_data.data
    from_index = eeg_data.getTimeIndex(1456820379.22)
    to_index = eeg_data.getTimeIndex(1456820379.27)
    print eeg_data.getColumn("F4", from_index, to_index)
    eeg_data.getTimeIndex(1456820379.23)