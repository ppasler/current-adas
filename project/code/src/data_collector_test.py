#!/usr/bin/python

import unittest
import numpy as np
import matplotlib.pyplot as plt
import os.path

from data_collector import DataCollector

WINDOW_SIZE = 4


class DataCollectorTest(unittest.TestCase):

    def setUp(self):
        self.collector = DataCollector(DummyDataSource(), WINDOW_SIZE)

    def notify(self, data):
        self.notifyCalled += 1

    def _fillValues(self, count, start=0):
        for i in range(start, count):
            self.collector.addValue(i)

    def _fillWindowFull(self):
        self._fillValues(WINDOW_SIZE)

    def test_windowsFilled(self):        
        win1 = self.collector.windows[0]
        win2 = self.collector.windows[1]
        self.assertEquals(win1.window, [0, 0])
        self.assertEquals(win2.window, [])
        
        self._fillValues(WINDOW_SIZE / 2)
        self.assertEquals(win1.window, [])
        self.assertEquals(win2.window, [0, 1]) 
        
        self._fillValues(WINDOW_SIZE, WINDOW_SIZE / 2)
        self.assertEquals(win1.window, [2, 3])
        self.assertEquals(win2.window, []) 

        
class DummyDataSource(object):
    
    def __init__(self):
        self.data = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.len = len(self.data)
        self.index = -1;

    def dequeue(self):
        self.index = (self.index+1) % self.len
        return self.data[self.index]
    
if __name__ == '__main__':
    unittest.main()












    
