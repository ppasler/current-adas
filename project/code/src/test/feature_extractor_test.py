#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 02.07.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

from base_test import * # @UnusedWildImport

from Queue import Queue

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

class TestProcessingChain(BaseTest):

    # TODO test queue and threading
    def setUp(self):
        inputQueue = Queue()
        outputQueue = Queue()
        self.processor = DataProcessor(inputQueue, outputQueue)

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