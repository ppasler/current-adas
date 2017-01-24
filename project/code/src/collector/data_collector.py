#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 30.05.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

from signal_window import RectangularSignalWindow


class DataCollector(object):
    '''
    collects EEG signals and passes them
    has 2 windows for which overlap 
       
    ``win 1: x x x x|x x x x|x x x x`` 
      
    ``win 2: x x|x x x x|x x x x|x x``
    
    '''

    def __init__(self, datasource, collectedQueue, fields):
        '''
        :param datasource: object which provides EmotivPackage by calling dequeu(). By default the Emotiv class is used
        :param list fields: list of key which are taken from the EmotivData
        '''
        self.datasource = datasource
        self.collectedQueue = collectedQueue
        self.fields = fields
        self.collect = True;

    def _getData(self):
        pass

    def _filter(self, data):
        '''filter dict and take only wanted fields from data
        :param data: whole raw data
        
        :return: filtered data set
        '''
        return {key: data[key] for key in self.fields if key in data}

    def _addData(self, data):
        for window in self.windows:
            window.addData(data)

    def close(self):
        self.collect = False

class EEGDataCollector(DataCollector):
    '''
    collects EEG signals and passes them
    has 2 windows for which overlap 
       
    ``win 1: x x x x|x x x x|x x x x`` 
      
    ``win 2: x x|x x x x|x x x x|x x``
    
    '''

    def __init__(self, datasource, collectedQueue, fields, windowSize, windowCount, sampleRate):
        '''
        :param datasource: object which provides EmotivPackage by calling dequeu(). By default the Emotiv class is used
        :param list fields: list of key which are taken from the EmotivData
        :param int windowSize: size of one collector
        :param int windowCount: number of windows
        '''
        DataCollector.__init__(self, datasource, collectedQueue, fields)
        self._buildSignalWindows(windowSize, windowCount, sampleRate)

    def _calcWindowSize(self, windowSize, samplingRate):
        return windowSize * samplingRate

    def _buildSignalWindows(self, windowSize, windowCount, samplingRate):
        windowSize = self._calcWindowSize(windowSize, samplingRate)
        self.windows = []
        for _ in range(windowCount):
            window = RectangularSignalWindow(self.collectedQueue, windowSize, self.fields)
            self.windows.append(window)

        self.windows[0].index = windowSize / 2

    def collectData(self):
        '''collect data and only take sensor data (ignoring timestamp, gyro_x, gyro_y properties)'''
        print("%s: starting data collection" % self.__class__.__name__)
        while self.collect:
            data = self._getData()
            filteredData = self._filter(data)
            self._addData(filteredData)
        print("%s: closing data collection" % self.__class__.__name__)
        self.datasource.close()

    def _getData(self):
        return self.datasource.dequeue().sensors

class DummyDataCollector(DataCollector):

    def __init__(self, datasource, collectedQueue, fields):
        DataCollector.__init__(self, datasource, collectedQueue, fields)

    def collectData(self):
        '''collect data and only take sensor data (ignoring timestamp, gyro_x, gyro_y properties)'''
        print("%s: starting data collection" % self.__class__.__name__)
        while self.collect:
            if self.datasource.hasMore:
                data = self._getData()
                filteredData = self._filter(data)
                self.collectedQueue.put(filteredData)
            else:
                self.collect = False
        print("%s: closing data collection" % self.__class__.__name__)
        self.datasource.close()

    def _getData(self):
        return self.datasource.dequeue()