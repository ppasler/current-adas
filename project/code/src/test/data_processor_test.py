#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 20.01.2017

:author: Paul Pasler
:organization: Reutlingen University
'''

from base_test import *  # @UnusedWildImport

from Queue import Queue

from collector.data_collector import DummyDataCollector
from util.eeg_data_source import EEGTableWindowSource
from test.posdbos_test_factory import PoSDBoSTestFactory


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
        self.fields = TEST_DATA.keys()
        self.collectedQueue = Queue()
        self.processedQueue = Queue()

        self.processor = PoSDBoSTestFactory.createDataProcessor(self.collectedQueue, self.processedQueue)

    def _addData(self, data):
        self.collectedQueue.put(data)

    def _fillQueue(self):
        datasource = EEGTableWindowSource(self.getData1024CSV(), False, 1, 2)
        datasource.convert()
        dc = DummyDataCollector(datasource, self.collectedQueue, self.fields)
        dc.collectData()

    def test_run(self):
        self._fillQueue()

        inpSize = self.collectedQueue.qsize()
        self.assertEqual(self.processedQueue.qsize(), 0)

        self.processor.processData()

        self.assertEqual(self.collectedQueue.qsize(), 0)
        self.assertEqual(self.processedQueue.qsize(), inpSize)

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