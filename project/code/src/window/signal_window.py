'''
Created on 11.04.2016

@author: Paul Pasler
'''

import abc

class SignalWindow:
    __metaclass__ = abc.ABCMeta


    def __init__(self, windowSize):
        self.observer = []
        self.windowSize = windowSize
        self.window = {}
        self.index = 0

        
    def registerObserver(self, observer):
        self.observer.append(observer)
        
    def unregisterObserver(self, observer):
        if observer in self.observer:
            self.observer.remove(observer)
    
    @abc.abstractmethod
    def notifyObserver(self, data):
        '''returns data like this      
        {
            "X": {
                "value":     [1, 2, 3],
                "quality":   [1, 2, 3]  
            },
            "F3": {
                "value":     [1, 2, 3],
                "quality":   [1, 2, 3]  
            }, ...
        }
        
        '''
        pass
    
    def isFull(self):
        return self.index >= self.windowSize
    
    @abc.abstractmethod
    def addData(self, data):
        '''expects data like this      
        {
            "X": {
                "value":     1,
                "quality":   2  
            },
            "F3": {
                "value":     3,
                "quality":   4  
            }, ...
        }
        
        @param data: dict
        '''
        pass
    
    def __repr__(self):  # pragma: no cover
        return "%s: { windowSize = %d, numValue = %d }" % (self.__class__.__name__, self.windowSize, self.index)
            
