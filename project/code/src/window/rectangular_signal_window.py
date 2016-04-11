'''
Created on 05.04.2016

@author: Paul Pasler
'''
from window.signal_window import SignalWindow

class RectangularSignalWindow(SignalWindow):
    '''
    Interface for window function
    '''
    
    def __init__(self, windowSize):
        super(RectangularSignalWindow, self).__init__(windowSize)
            
    def notifyObserver(self, data):
        data = self._doWindowFunction(data)
        for observer in self.observer:
            observer.notify(data)
    
    def _doWindowFunction(self, data):
        '''Simple window rectangular function '''
        return data
    
    def addValue(self, value):
        self.window.append(value)
        if self.isFull():
            data = self.window[:]
            self.window = []
            self.notifyObserver(data)
            
