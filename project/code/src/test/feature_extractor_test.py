#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import unittest

from feature_extractor import ProcessingChain


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

class ProcessingChainTest(unittest.TestCase):

    def setUp(self):
        self.processor = ProcessingChain()

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












    
