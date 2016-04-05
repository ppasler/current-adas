#!/usr/bin/python


from emokit.emotiv import Emotiv
from simple_signal_window import SimpleSignalWindow

emotiv = None

class DataCollector(object):
    '''
    collects EEG signals and passes them
    has 2 windows for which overlap 
    
    win 1:  x x x x|x x x x|x x x x
    win 2:  x x|x x x x|x x x x|x x

    '''

    def __init__(self, windowSize=32):
        self.windows = (SimpleSignalWindow(windowSize), SimpleSignalWindow(windowSize))
        [self.windows[0].addValue(0) for _ in range(windowSize/2)]
        for window in self.windows:
            window.registerObserver(self)
        
    def notify(self, data):
        '''handle data row'''
        
    def addValue(self, value):
        for window in self.windows:
            window.addValue(value)

    

if __name__ == "__main__":
    dc = DataCollector()
    
    #emotiv = Emotiv(display_output=False)
    #emotiv.setup()
