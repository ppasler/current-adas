#!/usr/bin/python


from emokit.emotiv import Emotiv
from window.rectangular_signal_window import RectangularSignalWindow
import gevent

class DataCollector(object):
    '''
    collects EEG signals and passes them
    has 2 windows for which overlap 
       
    win 1:  x x x x|x x x x|x x x x
    win 2:  x x|x x x x|x x x x|x x
    
    '''

    def __init__(self, datasource=None, fields=[], windowSize=32, windowCount=2):
        '''
        @param datasource: object which provides EmotivPackage by calling dequeu()
        @param fields: list of key which are taken from the EmotivData
        @param windowSize: size of one window  
        '''
        self.datasource = datasource    
        if datasource == None:
            self.setDefaultDataSource()
        self.fields = fields
        self.windowSize = windowSize
        self.collect = True;
        self._buildWindows(windowSize, windowCount)
        
    def setDefaultDataSource(self):
        emotiv = Emotiv(display_output=False)
        gevent.spawn(emotiv.setup)
        gevent.sleep(0)
        self.datasource = emotiv
    
    def _buildWindows(self, windowSize, windowCount):
        self.windows = (RectangularSignalWindow(windowSize), RectangularSignalWindow(windowSize))
        [self.windows[0].addValue({}) for _ in range(windowSize/2)]
        for window in self.windows:
            window.registerObserver(self)
    
    def filter(self, data):
        '''filter dict and take only wanted fields from data
        @param data: whole raw data
        
        @return: filtered data set
        '''
        return {x: data[x] for x in self.fields}
    
    def collectData(self):
        '''collect data and only take sensor data (ignoring timestamp, gyor_x, gyro_y properties)'''
        while self.collect:
            data = self.datasource.dequeue().sensors
            filteredData = self.filter(data)
            self.addValue(filteredData)
        print "closing data source"     
        self.datasource.close()
    
    def close(self):
        self.collect = False
        
    def notify(self, data):
        '''handle data row'''
        #TODO handle it
        
    def addValue(self, value):
        for window in self.windows:
            window.addValue(value)

    

if __name__ == "__main__":
    emotiv = Emotiv(display_output=False)
    gevent.spawn(emotiv.setup)
    gevent.sleep(0)

    dc = DataCollector(emotiv, ["X", "F3"])
    dc.collectData()
    

