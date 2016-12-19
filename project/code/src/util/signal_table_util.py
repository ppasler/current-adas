#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 10.05.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

import os
import re

from numpy import genfromtxt, delete, shape, savetxt, transpose, array

from config.config import ConfigProvider
from util.date_converter import DateConverter


DEFAULT_DELIMITER = ";" # default delimiter for CSV file
TIMESTAMP_STRING = "Timestamp" # key which specifies the unix timestamp of the data

EMOKIT_TIME_PATTERN = "%Y-%m-%d %H:%M:%S.%f"
BIOHARNESS_TIME_PATTERN = '%d/%m/%Y %H:%M:%S.%f'


class TableDto(object):
    '''
    Representation of Signal table data
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



class EEGTableDto(TableDto):
    '''
    Representation of EEG table data
    '''

    def __init__(self, header=None, data=None, filePath=""):
        super(EEGTableDto, self).__init__(header, data, filePath)

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

    def __repr__(self):
        return "EEGTableDto from '%s' shape %s\nheader %s" % (self.filePath, shape(self.data), self.header)


class ECGTableDto(TableDto):
    '''
    Representation of ECG table data
    '''

    def __init__(self, header=None, data=None, filePath=""):
        super(ECGTableDto, self).__init__(header, data, filePath)

    def getECGHeader(self):
        return self.header[1]

    def getECGData(self):
        return array([self.getColumn("ECG")])

    def __repr__(self):
        return "ECGTableDto from '%s' shape %s\nheader %s" % (self.filePath, shape(self.data), self.header)


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
            zIndex = header.index("Z")
            header.remove("Z")
            data = delete(data, zIndex, 1)

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
        return EEGTableDto(header, data.astype(float), filePath)

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
        return ECGTableDto(header, data.astype(float), filePath)

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
    