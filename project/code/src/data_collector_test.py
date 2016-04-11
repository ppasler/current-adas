#!/usr/bin/python

import unittest
import numpy as np
import matplotlib.pyplot as plt
import os.path

from string import ascii_uppercase

from data_collector import DataCollector

WINDOW_SIZE = 4


class DataCollectorTest(unittest.TestCase):

    def setUp(self):
        self.collector = DataCollector(DummyDataSource(WINDOW_SIZE), list(ascii_uppercase), WINDOW_SIZE)
        self.notifyCalled = 0

    def notify(self, data):
        self.notifyCalled += 1

    def _fillValues(self, count):
        data = self.collector.datasource.data
        for i in range(count):
            self.collector.addValue(data[i])

    def _fillWindowFull(self):
        self._fillValues(WINDOW_SIZE)

    def test_windowsFilled(self):        
        win1 = self.collector.windows[0]
        win2 = self.collector.windows[1]
        self.assertEquals(win1.window, [{}, {}])
        self.assertEquals(win2.window, [])
        
        self._fillValues(WINDOW_SIZE / 2)
        self.assertEquals(win1.window, [])
        self.assertEquals(len(win2.window), 2) 
        
        self._fillValues(WINDOW_SIZE / 2)
        self.assertEquals(len(win1.window), 2) 
        self.assertEquals(win2.window, []) 

    def test_addValue(self):
        win1, win2 = self.collector.windows
        win1.registerObserver(self)
        win2.registerObserver(self)
        
        self.assertEqual(self.notifyCalled, 0)
        
        # stop populating after 1 round
        try:
            self.collector.collectData()
        except RuntimeError:
            pass
        
        self.assertEqual(self.notifyCalled, 2)
    
    def test_filter(self):
        fields = ["A", "S", "X"]
        self.collector.fields = fields
        
        data = self.collector.datasource.data;
        
        filteredData = self.collector.filter(data[0].sensors)
        
        self.assertEqual(len(filteredData), len(fields))
        self.assertTrue(set(filteredData.keys()).issubset(set(fields)))
        self.assertTrue(set(filteredData.keys()).issuperset(set(fields)))

        
class DummyDataSource(object):
    
    def __init__(self, length, infinite=False):
        self.data = self._buildData(length)
        self.infinite = infinite
        self.len = len(self.data)
        self.index = -1;

    def _buildData(self, length):
        ret = []
        abc = ascii_uppercase
        for i in range(length):
            d = {}
            for c in abc:
                d[c] = c + "_" + str(i)
            ret.append(DummyPacket(d))    
        return ret

    def dequeue(self):
        self.index = (self.index+1)
        if self.infinite:
            self.index %= self.len
        elif self.index >= self.len:
            raise RuntimeError("Empty Source")
        
        return self.data[self.index]


class DummyPacket(object):
    def __init__(self, data):
        self.sensors = data

    
if __name__ == '__main__':
    unittest.main()












    
