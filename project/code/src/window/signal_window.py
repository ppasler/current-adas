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
        self.window = [] 

        
    def registerObserver(self, observer):
        self.observer.append(observer)
        
    def unregisterObserver(self, observer):
        if observer in self.observer:
            self.observer.remove(observer)
    
    @abc.abstractmethod
    def notifyObserver(self, data):
        pass
    
    def isFull(self):
        return len(self.window) >= self.windowSize
    
    @abc.abstractmethod
    def addValue(self, value):
        pass
    
    def __repr__(self):
        return "%s: { windowSize = %d, numValue = %d }" % (self.__class__.__name__, self.windowSize, len(self.window))
            
