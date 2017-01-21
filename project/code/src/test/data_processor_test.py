#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 20.01.2017

:author: Paul Pasler
:organization: Reutlingen University
'''

from base_test import *  # @UnusedWildImport

from Queue import Queue

from window.data_collector import DummyDataCollector
from data_processor import DataProcessor

WINDOW_SIZE = 4
TEST_DATA = {
                'X': {
                    'quality': [0, 1],
                    'value': [21.0, 22.0]
                },
                'F3': {
                    'quality': [0, 12],
                    'value': [-50.0, -55.0]
                }
            }

class TestDataProcessor(BaseTest):

    def setUp(self):
        self.inputQueue = Queue()
        self.outputQueue = Queue()
        self.processor = DataProcessor(self.inputQueue, self.outputQueue)

    def _addData(self, data):
        self.inputQueue.put(data)

    def _fillQueue(self):
        dc = DummyDataCollector()
        dc.setHandler(self._addData)
        dc.collectData()

    def test_run(self):
        self._fillQueue()

        inpSize = self.inputQueue.qsize()
        self.assertEqual(self.outputQueue.qsize(), 0)

        self.processor.processData()

        self.assertEqual(self.inputQueue.qsize(), 0)
        self.assertEqual(self.outputQueue.qsize(), inpSize)

    def test_process(self):
        self.processor.process(TEST_DATA)

    def test_splitData(self):
        eegData, gyroData = self.processor.splitData(TEST_DATA)
        intersect = set(eegData) & set(gyroData)
        self.assertTrue(len(intersect) == 0)
        self.assertTrue("F3" in eegData)
        self.assertTrue("X" in gyroData)

if __name__ == '__main__':
    unittest.main()