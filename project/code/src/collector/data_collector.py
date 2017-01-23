#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 30.05.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

from rectangular_signal_window import RectangularSignalWindow


class DataCollector(object):
    '''
    collects EEG signals and passes them
    has 2 windows for which overlap 
       
    ``win 1: x x x x|x x x x|x x x x`` 
      
    ``win 2: x x|x x x x|x x x x|x x``
    
    '''

    def __init__(self, datasource, fields=[], windowSize=128, windowCount=2):
        '''
        :param datasource: object which provides EmotivPackage by calling dequeu(). By default the Emotiv class is used
        :param list fields: list of key which are taken from the EmotivData
        :param int windowSize: size of one collector (default 128)
        :param int windowCount: number of windows (default 2)
        '''
        self.datasource = datasource
        self.fields = fields
        self.collect = True;

    def setHandler(self, dataHandler):
        self.dataHandler = dataHandler

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
        
    def notify(self, data):
        '''handle data row'''
        self.dataHandler(data)
        
    def close(self):
        self.collect = False

class EEGDataCollector(DataCollector):
    '''
    collects EEG signals and passes them
    has 2 windows for which overlap 
       
    ``win 1: x x x x|x x x x|x x x x`` 
      
    ``win 2: x x|x x x x|x x x x|x x``
    
    '''

    def __init__(self, datasource, fields=[], windowSize=128, windowCount=2):
        '''
        :param datasource: object which provides EmotivPackage by calling dequeu(). By default the Emotiv class is used
        :param list fields: list of key which are taken from the EmotivData
        :param int windowSize: size of one collector (default 128)
        :param int windowCount: number of windows (default 2)
        '''
        DataCollector.__init__(self, datasource, fields, windowSize, windowCount)
        self._buildSignalWindows(windowSize, windowCount)

    def _buildSignalWindows(self, windowSize, windowCount):
        #TODO windowCount
        self.windows = []
        for _ in range(windowCount):
            window = RectangularSignalWindow(windowSize, self.fields)
            self.windows.append(window)
            
        self.windows[0].index = windowSize / 2
        
        for window in self.windows:
            window.registerObserver(self)

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

    def __init__(self, datasource, fields=[], windowSize=128, windowCount=2):
        DataCollector.__init__(self, datasource, fields, windowSize, windowCount)

    def collectData(self):
        '''collect data and only take sensor data (ignoring timestamp, gyro_x, gyro_y properties)'''
        print("%s: starting data collection" % self.__class__.__name__)
        while self.collect:
            if self.datasource.hasMore:
                data = self._getData()
                filteredData = self._filter(data)
                self.notify(filteredData)
            else:
                self.collect = False
        print("%s: closing data collection" % self.__class__.__name__)
        self.datasource.close()

    def _getData(self):
        return self.datasource.dequeue()