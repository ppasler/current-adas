#!/usr/bin/python

import unittest
from window.rectangular_signal_window import RectangularSignalWindow

WINDOW_SIZE = 4


class DataCollector(unittest.TestCase):

    def setUp(self):
        self.window = RectangularSignalWindow(WINDOW_SIZE)

    def notify(self, data):
        self.notifyCalled += 1

    def _fillValues(self, count, start=0):
        for i in range(start, count):
            self.window.addValue(i)

    def _fillWindowFull(self):
        self._fillValues(WINDOW_SIZE)

    def test_windowsFilled(self):        
        self.assertEquals(self.window.window, [])
        
        self._fillValues(WINDOW_SIZE / 2)
        self.assertEquals(self.window.window, [0, 1]) 
        
        self._fillValues(WINDOW_SIZE, WINDOW_SIZE / 2)
        self.assertEquals(self.window.window, []) 

    def test__register(self):
        self.notifyCalled = 0
        win = self.window
        win.registerObserver(self)
        self._fillWindowFull()
        self.assertEqual(self.notifyCalled, 1)

    def test__unregister(self):
        self.notifyCalled = 0
        win = self.window
        win.registerObserver(self)
        self._fillWindowFull()
        self.assertEqual(self.notifyCalled, 1)
                
        win.unregisterObserver(self)
        self._fillWindowFull()
        self.assertEqual(self.notifyCalled, 1) 
        
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












    
