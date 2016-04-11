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

    def __init__(self, datasource, windowSize=32):
        self.collect = True;
        self.datasource = datasource
        self.windows = (RectangularSignalWindow(windowSize), RectangularSignalWindow(windowSize))
        [self.windows[0].addValue(0) for _ in range(windowSize/2)]
        for window in self.windows:
            window.registerObserver(self)
    
    def collectData(self):
        while self.collect:
            self.addValue(self.datasource.dequeue())
        
    def notify(self, data):
        '''handle data row'''
        
    def addValue(self, value):
        for window in self.windows:
            window.addValue(value)

    

if __name__ == "__main__":
    emotiv = Emotiv(display_output=False)
    gevent.spawn(emotiv.setup)
    gevent.sleep(0)

    dc = DataCollector(emotiv)
    dc.collectData()
    

