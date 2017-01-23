#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 11.04.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

from copy import deepcopy

class SignalWindow(object):

    def __init__(self, collectedQueue, windowSize, fields):
        self.collectedQueue = collectedQueue
        self.windowSize = windowSize
        self.fields = fields
        self.window = {}
        self.index = 0

    def _resetWindow(self):
        self.index = 0
        self.window = deepcopy(self.initWindow)

    def _initWindow(self, fields):
        self.initWindow = {}
        for key in fields:
            self.initWindow[key] = {"value": [], "quality": []}

    def addData(self, data):
        '''
        expects data like this      
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
        
        :param dict data: 
        '''
        #TODO potential bottleneck
        self._addDataToWindow(data)
        self.index += 1
        
        if self.isFull():
            data = self.window.copy()
            self._resetWindow()
            self.collectedQueue.put(data)

    def _addDataToWindow(self, data):   
        for key, date in data.iteritems():
            field = self.window[key]
            field["value"].append(date["value"])
            field["quality"].append(date["quality"])

    def isFull(self):
        return self.index >= self.windowSize

    def __repr__(self):  # pragma: no cover
        return "%s: { windowSize = %d, numValue = %d }" % (self.__class__.__name__, self.windowSize, self.index)
    
class RectangularSignalWindow(SignalWindow):
    '''
    Interface for collector function
    '''
    
    def __init__(self, collectedQueue, windowSize, fields):
        super(RectangularSignalWindow, self).__init__(collectedQueue, windowSize, fields)
        self._initWindow(fields)
        self._resetWindow()

    def _doWindowFunction(self, data):
        '''Simple collector rectangular function '''
        return data