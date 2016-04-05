#!/usr/bin/python

import unittest
import numpy as np
import matplotlib.pyplot as plt
import os.path

from data_collector import DataCollector

WINDOW_SIZE = 4


class TestSignalUtil(unittest.TestCase):

    def setUp(self):
        self.collector = DataCollector(WINDOW_SIZE)

    def notify(self, data):
        self.notifyCalled += 1

    def _fillValues(self, count, start=0):
        for i in range(start, count):
            self.collector.addValue(i)

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

    def test__register(self):
        self.notifyCalled = 0
        win1, win2 = self.collector.windows
        win1.registerObserver(self)
        win2.registerObserver(self)
        self._fillValues(WINDOW_SIZE)
        self.assertEqual(self.notifyCalled, 2)

    def test__unregister(self):
        self.notifyCalled = 0
        win1, win2 = self.collector.windows
        win1.registerObserver(self)
        win2.registerObserver(self)
        self._fillValues(WINDOW_SIZE)
        self.assertEqual(self.notifyCalled, 2)
                
        win2.unregisterObserver(self)
        self._fillValues(WINDOW_SIZE)
        self.assertEqual(self.notifyCalled, 3) 
        
    
if __name__ == '__main__':
    unittest.main()












    
