#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 02.07.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

from base_test import * # @UnusedWildImport

from Queue import Queue

from collector.signal_window import RectangularSignalWindow


WINDOW_SIZE = 4
INIT_WINDOW = {"X": {'quality': [], 'value': []}}

def _fillValues(window, count, start=0):
    for i in range(start, count):
        window.addData({"X": {"value" : i, "quality": i**2}})

def _fillWindowFull(window):
    _fillValues(window, WINDOW_SIZE)

class TestRectanglarSignalWindow(BaseTest):

    def setUp(self):
        self.collectedQueue = Queue()
        self.window = RectangularSignalWindow(self.collectedQueue, WINDOW_SIZE, ["X"])

    def test_windowsFilled(self):
        self.assertEquals(self.window.window, INIT_WINDOW)
        
        _fillValues(self.window, WINDOW_SIZE / 2)
        self.assertEquals(self.window.window, {"X": {'quality': [0, 1], 'value': [0, 1]}}) 
        
        _fillValues(self.window, WINDOW_SIZE, WINDOW_SIZE / 2)
        self.assertEquals(self.window.window, INIT_WINDOW) 
        self.assertEquals(self.collectedQueue.qsize(), 1)

if __name__ == '__main__':
    unittest.main()