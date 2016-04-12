#!/usr/bin/python

import unittest
from window.rectangular_signal_window import RectangularSignalWindow

WINDOW_SIZE = 4


class SignalWindowTest(unittest.TestCase):

    def setUp(self):
        self.window = RectangularSignalWindow(WINDOW_SIZE, ["X"])

    def notify(self, data):
        self.notifyCalled += 1

    def _fillValues(self, count, start=0):
        for i in range(start, count):
            self.window.addData({"X": {"value" : i, "quality": i**2}})

    def _fillWindowFull(self):
        self._fillValues(WINDOW_SIZE)

    def test_windowsFilled(self):        
        self.assertEquals(self.window.window, {"X": {'quality': [], 'value': []}})
        
        self._fillValues(WINDOW_SIZE / 2)
        self.assertEquals(self.window.window, {"X": {'quality': [0, 1], 'value': [0, 1]}}) 
        
        self._fillValues(WINDOW_SIZE, WINDOW_SIZE / 2)
        self.assertEquals(self.window.window, {"X": {'quality': [], 'value': []}}) 

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
        
    
if __name__ == '__main__':
    unittest.main()












    
