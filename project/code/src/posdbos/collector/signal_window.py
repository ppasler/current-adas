#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 11.04.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

from posdbos.collector.window_dto import WindowDto

class SignalWindow(object):

    def __init__(self, collectedQueue, windowSize, fields):
        self.collectedQueue = collectedQueue
        self.windowSize = windowSize
        self.fields = fields
        self.index = 0

        self._createDto()

    def _createDto(self):
        self.dto = WindowDto(self.windowSize, self.fields)

    def _resetWindow(self):
        self.index = 0
        self._createDto()

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
        self.dto.addData(data)
        self.index += 1
        
        if self.isFull():
            data = self._doWindowFunction(self.dto)
            self.collectedQueue.put(data)
            self._resetWindow()

    def isFull(self):
        return self.index >= self.windowSize

    def _doWindowFunction(self, data):
        pass

    def __repr__(self):  # pragma: no cover
        return "%s: { windowSize = %d, numValue = %d }" % (self.__class__.__name__, self.windowSize, self.index)
    
class RectangularSignalWindow(SignalWindow):
    '''
    Interface for collector function
    '''
    
    def __init__(self, collectedQueue, windowSize, fields):
        super(RectangularSignalWindow, self).__init__(collectedQueue, windowSize, fields)

    def _doWindowFunction(self, data):
        '''Simple collector rectangular function '''
        return data