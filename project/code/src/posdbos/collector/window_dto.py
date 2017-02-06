#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 05.02.2017

:author: Paul Pasler
:organization: Reutlingen University
'''

from numpy import empty, NaN, isnan, array_equal, array
from copy import deepcopy


class WindowDto(object):

    def __init__(self, windowSize, header):
        self.windowSize = windowSize
        self.header = header
        self._initWindow()

    def _initWindow(self):
        self.data = {}
        for key in self.header:
            self.data[key] = {"value": [], "quality": []}

    def getHeader(self):
        return self.header

    def setData(self, data):
        self.data = data
        self.header = data.keys()

    def getData(self):
        return self.data

    def getChannel(self, key):
        return self.getValue(key), self.getQuality(key)

    def getField(self, key, field):
        return array(self.data[key][field])

    def getValue(self, key):
        return self.getField(key, "value")

    def getQuality(self, key):
        return self.getField(key, "quality")

    def addNewField(self, key, field, value):
        self.data[key][field] = value

    def addData(self, data):
        for key, date in data.iteritems():
            field = self.data[key]
            field["value"].append(date["value"])
            field["quality"].append(date["quality"])

    def filter(self, fields):
        self.setData({key: self.data[key] for key in fields if key in self.data})

    def copy(self):
        header = self.header[:]
        dto = WindowDto(self.windowSize, header)
        dto.data = deepcopy(self.data)
        return dto

    def __iter__(self):
        return self.data.keys().__iter__()

    def __len__(self):
        return len(self.data)

    def __getitem__(self, key):
        return self.data[key]

    def __contains__(self, key):
        return key in self.data

    def __eq__(self, other):
        if other is None:
            return False 
        if type(self) != type(other):
            return False
        if self.header != other.header:
            return False
        return array_equal(self.data, other.data)

    def shape(self):
        return (len(self), len(self.header))

    def __repr__(self):
        return "%s %s: %s" % (self.__class__.__name__, (self.shape()), str(self.header))

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