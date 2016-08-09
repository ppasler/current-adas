#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 10.05.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

import os
import time

from util.eeg_table_util import EEGTableFileUtil


scriptPath = os.path.dirname(os.path.abspath(__file__))

class EEGTablePacket(object):
    '''Object for EEG data :see: EmotivPacket
    '''
    
    def __init__(self, data):
        self.sensors = data
        self.gyro_x = data["X"]["value"]
        self.gyro_y = data["Y"]["value"]
        self.old_model = True

class EEGTableConverter(object):
    
    def __init__(self, filePath=None, infinite=True):
        '''
        Reads data from ./../../examples/example_4096.csv and builds the data structure
        '''
        self.reader = EEGTableFileUtil()
        self.filepath = filePath
        self.infinite = infinite
        self.hasMore = False
        if filePath == None:
            self.filepath = scriptPath + "/../../examples/example_4096.csv"
            #self.filepath = scriptPath + "/../../../captured_data/janis/2016-07-12-11-15_EEG_1.csv"
        self.data = None
        self.index = 0

    def convert(self):
        self._readHeader()
        self._readRawData()

        self.data = self._buildDataStructure()

    def _readHeader(self):
        self.header = self.reader.readHeader(self.filepath)
        
        fields = self.header[:]
        fields.remove("Timestamp")
        fields.remove("Unknown")
        self.fields = filter(lambda x: not (x.startswith("Q")), fields)

    def _readRawData(self):
        self.rawData = self.reader.readData(self.filepath)
        self.len = len(self.rawData)
        if self.len > 0:
            self.hasMore = True
        print "Using %d dummy datasets" % self.len

    def dequeue(self):
        pass

    def _getNextIndex(self):
        self.index += 1
        if self.index >= len(self.data) and not self.infinite:
            self.hasMore = False
        self.index %= self.len

    def close(self):
        pass

class EEGTableToPacketConverter(EEGTableConverter):
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
        Reads data from ./../../examples/example_4096.csv and builds the data structure
        '''
        EEGTableConverter.__init__(self, filePath, infinite)

    def _buildDataStructure(self):
        data = []

        for raw in self.rawData:
            data.append(self._buildRow(raw))

        return data

    def _buildRow(self, row):
        ret = {}
        for h in self.fields:
            value = row[self.header.index(h)]
            quality = row[self.header.index("Q" + h)]
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

class EEGTableToWindowConverter(EEGTableConverter):
    '''
    Util for EPOC dummy data 
    
    Converts CSV style data to a window object

    | CSV
    | ``Timestamp;         F3;   X; ... QF3``
    | ``1459760953.863; -58.0;  -1; ... 6.0``
    | ``...           ;  ... ; ...; ... ...``
    | ``1459760955.863;  69.0;  -1; ...15.0``

     
    | window
    | ``{``
    |    ``"Timestamp": [1459760953.863, ... 1459760955.863]``
    |    ``"F3" :{``
    |        ``"value":   [-58.0, ..., 69.0],``
    |        ``"quality": [6.0, ..., 15.0]``
    |    ``}``
    |    ``...``
    | ``}``
    '''

    def __init__(self, filePath=None, infinite=True, windowSize=None, windowCount=None):
        '''
        Reads data from ./../../examples/example_4096.csv and builds the data structure
        '''
        EEGTableConverter.__init__(self, filePath, infinite)
        self.windowSize = windowSize


    def _buildDataStructure(self): # pragma: no cover
        if self.windowSize == None:
            self.windowSize = self.len

        data = []
        for start in range(0, len(self.rawData), self.windowSize / 2):
            end = start + self.windowSize
            if end <= len(self.rawData):
                data.append(self._buildWindow(start, end))

        return data

    def _buildWindow(self, start, end):
        window = {}
        for field in self.fields:
            value = self.rawData[start:end, self.header.index(field)]
            quality = self.rawData[start:end, self.header.index("Q" + field)]
            window[field] = {"value": value, "quality": quality}
        return window

    def dequeue(self):
        '''get the current dummy data window
        :return: data window
        :rtype: np.array 
        '''
        row = self.data[self.index]
        self._getNextIndex()
        return row