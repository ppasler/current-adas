#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 20.01.2017

:author: Paul Pasler
:organization: Reutlingen University
'''

from base_test import *  # @UnusedWildImport

from Queue import Queue

from data_collector import DummyDataCollector
from data_processor import DataProcessor


class TestDataProcessor(BaseTest):

    def setUp(self):
        self.inputQueue = Queue()
        self.outputQueue = Queue()
        self.processor = DataProcessor(self.inputQueue, self.outputQueue)
        self._fillQueue()

    def _addData(self, data):
        self.inputQueue.put(data)

    def _fillQueue(self):
        dc = DummyDataCollector()
        dc.setHandler(self._addData)
        dc.collectData()

    def test_run(self):
        inpSize = self.inputQueue.qsize()
        self.assertEqual(self.outputQueue.qsize(), 0)
        self.processor.processData()

        self.assertEqual(self.inputQueue.qsize(), 0)
        self.assertEqual(self.outputQueue.qsize(), inpSize)


if __name__ == '__main__':
    unittest.main()