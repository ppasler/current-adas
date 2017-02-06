#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 10.05.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

import os
import time
import logging
from numpy import array

from posdbos.util.file_util import FileUtil
from posdbos.collector.data_collector import EEGDataCollector
from posdbos.collector.window_dto import WindowDto

scriptPath = os.path.dirname(os.path.abspath(__file__))

class EEGTablePacket(object):
    '''Object for EEG data :see: EmotivPacket
    '''
    # TODO fix me
    def __init__(self, data):
        self.sensors = data
        if "X" in data:
            self.gyro_x = data["X"]["value"]
            self.gyro_y = data["Y"]["value"]
        self.old_model = True

class DummyDataSource(object):
    
    def __init__(self, filePath=None, infinite=True):
        '''
        Reads data from filePath or ./../../data/dummy_4096.csv and builds the data structure
        '''
        self.fileUtil = FileUtil()
        self.filepath = filePath
        self.infinite = infinite
        self.hasMore = False
        if filePath == None:
            self.filepath = scriptPath + "/../../../data/dummy_4096.csv"
        self.data = None
        self.index = 0

    def convert(self):
        dto = self.fileUtil.getDto(self.filepath)
        self._readHeader(dto)
        self._readRawData(dto)
        self.samplingRate = dto.getSamplingRate()

        self.data = self._buildDataStructure()

    def _readHeader(self, dto):
        self.header = dto.getHeader()
        self.fields = dto.getEEGHeader() + dto.getGyroHeader()
        self._hasQuality()

    def _hasQuality(self):
        self.hasQuality = all([(("Q" + field) in self.header) for field in self.fields])

    def _readRawData(self, dto):
        self.rawData = dto.getData()
        self.len = len(self.rawData)
        if self.len > 0:
            self.hasMore = True
        logging.info("%s: Using %d dummy datasets" % (self.__class__.__name__, self.len))

    def dequeue(self):
        pass

    def _getNextIndex(self):
        self.index += 1
        if self.index >= len(self.data) and not self.infinite:
            self.hasMore = False
        self.index %= self.len

    def _buildDataStructure(self):
        pass

    def close(self):
        pass

    def stop(self):
        pass

class DummyPacketSource(DummyDataSource):
    '''
    Util for EPOC dummy data 
    
    Converts CSV style data to a emotiv object

    | CSV
    | ``Timestamp;         F3;   X; ... QF3``
    | ``1459760953.863; -58.0;  -1; ... 6.0``
     
    | emotiv
    | ``{``
    |    ``"Timestamp": 1459760953.863,``
    |    ``"F3" :{``
    |        ``"value":   -58.0,``
    |        ``"quality": 6.0,``
    |    ``}``
    |    ``...``
    | ``}``
    '''
    
    def __init__(self, filePath=None, infinite=True):
        '''
        Reads data from ./../../example/example_4096.csv and builds the data structure
        '''
        DummyDataSource.__init__(self, filePath, infinite)

    def _buildDataStructure(self):
        data = []

        for raw in self.rawData:
            data.append(self._buildRow(raw))

        return data

    def _buildRow(self, row):
        ret = {}
        for h in self.fields:
            value = row[self.header.index(h)]
            if self.hasQuality:
                quality = row[self.header.index("Q" + h)]
            else:
                quality = 0
            ret[h] = {
                "value": value,
                "quality": int(quality)
            }
        return EEGTablePacket(ret)

    def dequeue(self):
        '''get the current dummy data row
        :return: data row
        :rtype: EEGTablePacket 
        '''
        row = self.data[self.index]
        self._getNextIndex()
        row.sensors["Timestamp"] = time.time()
        return row

    def close(self):
        pass

class DummyWindowSource(DummyDataSource):
    '''
    Util for EPOC dummy data 
    
    Converts CSV style data to a collector object

    | CSV
    | ``Timestamp;         F3;   X; ... QF3``
    | ``1459760953.863; -58.0;  -1; ... 6.0``
    | ``...           ;  ... ; ...; ... ...``
    | ``1459760955.863;  69.0;  -1; ...15.0``

     
    | collector
    | ``{``
    |    ``"Timestamp": [1459760953.863, ... 1459760955.863]``
    |    ``"F3" :{``
    |        ``"value":   [-58.0, ..., 69.0],``
    |        ``"quality": [6.0, ..., 15.0]``
    |    ``}``
    |    ``...``
    | ``}``
    '''

    def __init__(self, filePath=None, infinite=True, windowSeconds=None, windowCount=None):
        '''
        Reads data from ./../../example/example_4096.csv and builds the data structure
        '''
        DummyDataSource.__init__(self, filePath, infinite)
        self.windowCount = windowCount
        self.windowSeconds = windowSeconds

    def _buildDataStructure(self): # pragma: no cover
        if self.windowSeconds is None:
            self.windowSize = self.len
        else:
            self.windowSize = EEGDataCollector.calcWindowSize(self.windowSeconds, self.samplingRate)

        windowRatio = EEGDataCollector.calcWindowRatio(self.windowSize, self.windowCount)

        data = []
        for start in range(0, len(self.rawData), windowRatio):
            end = start + self.windowSize
            if end <= len(self.rawData):
                data.append(self._buildWindow(start, end))

        return data

    def _buildWindow(self, start, end):
        window = {}
        for field in self.fields:
            value = self.rawData[start:end, self.header.index(field)]
            if self.hasQuality:
                quality = self.rawData[start:end, self.header.index("Q" + field)]
            else:
                quality = array([0]*(end-start))
            window[field] = {"value": value, "quality": quality}
        dto = WindowDto(self.windowSize, self.fields)
        dto.data = window
        return dto

    def dequeue(self):
        '''get the current dummy data collector
        :return: data collector
        :rtype: np.array 
        '''
        row = self.data[self.index]
        self._getNextIndex()
        return row