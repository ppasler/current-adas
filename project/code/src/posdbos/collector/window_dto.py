#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 05.02.2017

:author: Paul Pasler
:organization: Reutlingen University
'''

from numpy import empty, NaN, isnan, array_equal

class WindowDto(object):

    def __init__(self, windowSize, header):
        self.windowSize = windowSize
        self.header = header
        self._initWindow()

    def _initWindow(self):
        self.data = {}
        for key in self.header:
            self.data[key] = {"value": [], "quality": []}

    def getData(self):
        return self.data

    def addData(self, data):
        for key, date in data.iteritems():
            field = self.data[key]
            field["value"].append(date["value"])
            field["quality"].append(date["quality"])

    def __eq__(self, other):
        if (self is None) or (other is None):
            return False 
        if type(self) != type(other):
            return False
        if self.header != other.header:
            return False
        return array_equal(self.data, other.data)

class XWindowDto(object):

    def __init__(self, header, windowSize):
        self.windowSize = windowSize
        self.header = header
        self._initWindow()

    def _initWindow(self):
        self.data = empty((len(self.header), self.windowSize))
        self.data[:] = NaN

    def _isFull(self):
        return not all(isnan(self.data[len(self.data)-1])) 