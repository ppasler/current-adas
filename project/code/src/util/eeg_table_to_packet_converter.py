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

class EEGTableToPacketUtil(object):
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
    
    def __init__(self, filePath=None):
        '''
        Reads data from ./../../examples/example_4096.csv and builds the data structure
        '''
        self.reader = EEGTableFileUtil()
        self.filepath = filePath
        if filePath == None:
            self.filepath = scriptPath + "/../../examples/example_4096.csv"
            #self.filepath = scriptPath + "/../../../captured_data/janis/2016-07-12-11-15_EEG_1.csv"
        self.index = 0
        self._buildDataStructure()
        print "Using %d dummy datasets" % self.len

        
    def _readRawData(self):       
        rawData = self.reader.readData(self.filepath)
        self.len = len(rawData)
        return rawData

    def _readHeader(self):
        self.header = self.reader.readHeader(self.filepath)
        
        fields = self.header[:]
        fields.remove("Timestamp")
        fields.remove("Unknown")
        self.fields = filter(lambda x: not (x.startswith("Q")), fields)

    def _buildDataStructure(self):
        self._readHeader()
        rawData = self._readRawData()

        data = []
        
        for raw in rawData:
            data.append(self._buildRow(raw))
        
        self.data = data   
                
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
        row.sensors["Timestamp"] = time.time()
        self.index = (self.index + 1) % self.len
        return row

    def close(self):
        pass


    # TODO extract me
    def _buildFullDataStructure(self): # pragma: no cover
        self._readHeader()
        rawData = self._readRawData()

        data = {}
        for key in self.fields:
            data[key] = {"value": [], "quality": []}
        
        for raw in rawData:
            self._buildFullRow(raw, data)
        
        return data

    # TODO extract me
    def _buildFullRow(self, row, data): # pragma: no cover
        for h in self.fields:
            value = row[self.header.index(h)]
            quality = row[self.header.index("Q" + h)]
            data[h]["value"].append(value)
            data[h]["quality"].append(quality)

class EEGTablePacket(object):
    '''Object for EEG data :see: EmotivPacket
    '''
    
    def __init__(self, data):
        self.sensors = data
        self.gyro_x = data["X"]["value"]
        self.gyro_y = data["Y"]["value"]
        self.old_model = True