#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 03.01.2017

:author: Paul Pasler
:organization: Reutlingen University
'''
from numpy import array, arange, zeros

from config.config import ConfigProvider


TIMESTAMP_STRING = "Timestamp" # key which specifies the unix timestamp of the data
ECG_HEADER = "ECG"
TIME_START = 558345300

class TableDto(object):
    '''
    Representation of Signal table data
    '''

    def __init__(self, header=None, data=None, filePath="", samplingRate=None):
        '''
        table data with header, data and the filepath
        
        :param header:
        :param data:
        :param filePath:
        '''
        self.filePath = filePath
        self.setHeader(header)
        self.setData(data)
        if TIMESTAMP_STRING not in header:
            self._createTimeData(samplingRate)
        self._setDataTypes()
        self.setSamplingRate(samplingRate)

    def setHeader(self, header):  # pragma: no cover
        self.header = header

    def setData(self, data):  # pragma: no cover
        self.data = data
        if data is not None:
            self.len = len(data)

    def _setDataTypes(self):  # pragma: no cover
        self.hasEEGData = self._containsEEGData()
        self.hasEEGQuality = self._containsEEGQuality()
        self.hasECGData = self._containsECGData()

    def _createTimeData(self, samplingRate):
        stop = TIME_START + (len(self) / samplingRate)
        timeData = arange(TIME_START, stop, 1./samplingRate)
        self.addRow(TIMESTAMP_STRING, timeData)

    def addRow(self, name, row):
        self.header.insert(0, name)

        data = zeros((len(self), len(self.header)))
        data[:,0] = row
        data[:,1:] = self.data
        self.data = data


    def _containsEEGData(self):
        return len(self.getEEGHeader()) > 0

    def _containsEEGQuality(self):
        return len(self.getQualityHeader()) > 0

    def _containsECGData(self):
        return ECG_HEADER in self.header

    def setSamplingRate(self, samplingRate=None):
        if samplingRate is not None:
            self.samplingRate = samplingRate
        else:
            self.samplingRate = self._calcSamplingRate()

    def _calcSamplingRate(self):
        '''
        calcs the samplerate for the whole dataset based on the timestamp column   
        
        :return: samplerate
        :rtype: float

        '''
        try:
            duration = self.getDuration()
            return self.len / duration
        except:
            return 0.0

    def getHeader(self):  # pragma: no cover
        return self.header

    def getData(self):  # pragma: no cover
        return self.data

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

    def getColumns(self, columnNames):
        data = []
        for columnName in columnNames:
            data.append(self.getColumn(columnName))
        return array(data)

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
        return self.samplingRate

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

    def __len__(self):
        return self.getValueCount()

    def _switchTime(self, time1, time2):
        return time2, time1

    def _timeInData(self, data, time):
        return (min(data) <= time <= max(data))

    def __repr__(self):
        return "TableDto from '%s' shape %s\nheader %s" % (self.filePath, self.data.shape, self.header)


    def getEEGHeader(self):
        eegFields = ConfigProvider().getEmotivConfig().get("eegFields")
        return [head for head in self.header if head in eegFields]

    def getEEGData(self):
        if self.hasEEGData:
            eegFields = self.getEEGHeader()
            return self.getColumns(eegFields)
        return None

    def getQualityHeader(self):
        return ["Q"+head for head in self.getEEGHeader() if "Q"+head in self.header]

    def getQualityData(self):
        if self.hasEEGQuality:
            eegQualFields = self.getQualityHeader()
            return self.getColumns(eegQualFields)
        return None

    def getQuality(self, eegQualField):
        return self.getColumn(eegQualField)


    def getECGHeader(self):
        if self.hasECGData:
            return ECG_HEADER
        return None

    def getECGData(self):
        if self.hasECGData:
            return array([self.getColumn(ECG_HEADER)])
        return None