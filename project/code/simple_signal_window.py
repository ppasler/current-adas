'''
Created on 05.04.2016

@author: Paul Pasler
'''

class SimpleSignalWindow():
    '''
    Interface for window function
    '''
    
    def __init__(self, windowSize):
        self.windowSize = windowSize
        self.window = []
        self.observer = [] 
    
    def registerObserver(self, observer):
        self.observer.append(observer)
        
    def unregisterObserver(self, observer):
        if observer in self.observer:
            self.observer.remove(observer)
            
    def notifyObserver(self, data):
        data = self.doWindowFunction(data)
        for observer in self.observer:
            observer.notify(data)
    
    def doWindowFunction(self, data):
        return data
    
    def isFull(self):
        return len(self.window) >= self.windowSize
        
    def addValue(self, value):
        self.window.append(value)
        if self.isFull():
            data = self.window[:]
            self.window = []
            self.notifyObserver(data)
            
    def __repr__(self):
        return "SimpleSignalWindow with windowSize %d and %d values" % (self.windowSize, len(self.window))
        