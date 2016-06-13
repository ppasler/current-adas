#!/usr/bin/python


from time import sleep

import gevent

from emokit.emotiv import Emotiv
from window.rectangular_signal_window import RectangularSignalWindow
from client import EEGClient


class DataCollector(object):
    '''
    collects EEG signals and passes them
    has 2 windows for which overlap 
       
    ``win 1: x x x x|x x x x|x x x x`` 
      
    ``win 2: x x|x x x x|x x x x|x x``
    
    '''

    def __init__(self, datasource=None, fields=[], windowSize=128, windowCount=2, interval=0):
        '''
        :param datasource: object which provides EmotivPackage by calling dequeu(). By default the Emotiv class is used
        :param list fields: list of key which are taken from the EmotivData
        :param int windowSize: size of one window (default 128)
        :param int windowCount: number of windows (default 2)
        '''
        self.datasource = datasource    
        if datasource == None:
            self._setDefaultDataSource()
        self.fields = fields
        self._buildSignalWindows(windowSize, windowCount)
        self.collect = True;
        self.interval = interval
        
    def _setDefaultDataSource(self): # pragma: no cover
        '''Set Emotiv as default source and starts it inside a gevent context'''
        emotiv = Emotiv(display_output=False)
        gevent.spawn(emotiv.setup)
        gevent.sleep(0)
        self.datasource = emotiv
        print "using default datasource: " + emotiv.__class__.__name__
    
    def _buildSignalWindows(self, windowSize, windowCount):
        #TODO windowCount
        self.windows = []
        for _ in range(windowCount):
            window = RectangularSignalWindow(windowSize, self.fields)
            self.windows.append(window)
            
        self.windows[0].index = windowSize / 2
        
        for window in self.windows:
            window.registerObserver(self)
    
    def setHandler(self, dataHandler):
        self.dataHandler = dataHandler
      
    def collectData(self):
        '''collect data and only take sensor data (ignoring timestamp, gyro_x, gyro_y properties)'''
        print("%s: starting data collection" % self.__class__.__name__)     
        while self.collect:
            data = self.datasource.dequeue().sensors
            filteredData = self.filter(data)
            self._addData(filteredData)
            sleep(self.interval)
        print("%s: closing data collection" % self.__class__.__name__)     
        self.datasource.close()
    
    def filter(self, data):
        '''filter dict and take only wanted fields from data
        :param data: whole raw data
        
        :return: filtered data set
        '''
        return {x: data[x] for x in self.fields}

    def _addData(self, data):
        for window in self.windows:
            window.addData(data)
        
    def notify(self, data):
        '''handle data row'''
        self.dataHandler(data)
        
    def close(self):
        self.collect = False

    

if __name__ == "__main__": # pragma: no cover
    #emotiv = Emotiv(display_output=False)
    #gevent.spawn(emotiv.setup)
    #gevent.sleep(0)

    client = EEGClient("localhost", 9000)

    dc = DataCollector(client, ["X", "F3"])
    handler = lambda x: x
    dc.setHandler(handler)
    dc.collectData()
    sleep(2)
    dc.close()
    

