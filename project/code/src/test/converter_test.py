#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 08.08.2016

:author: Paul Pasler
:organization: Reutlingen University
'''
import sys, os
import unittest

from util.eeg_data_source import EEGTablePacketSource, EEGTableWindowSource


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

FILE_PATH = os.path.dirname(os.path.abspath(__file__)) + "/../../examples/example_32.csv"

class TestEEGTableToPacketConverter(unittest.TestCase):

    def setUp(self):
        self.converter = EEGTablePacketSource(FILE_PATH, False)

    def test_convert_sunshine(self):
        self.assertFalse(self.converter.hasMore)
        self.converter.convert()
        self.assertTrue(self.converter.hasMore)
        for _ in range(0, len(self.converter.data)):
            self.converter.dequeue()
        self.assertFalse(self.converter.hasMore)

class TestEEGTableToWindowConverter(unittest.TestCase):

    def setUp(self):
        self.converter = EEGTableWindowSource(FILE_PATH, False, 16)

    def test_convert_sunshine(self):
        self.assertFalse(self.converter.hasMore)
        self.converter.convert()
        self.assertTrue(self.converter.hasMore)
        for _ in range(0, len(self.converter.data)):
            self.converter.dequeue()
        self.assertFalse(self.converter.hasMore)


if __name__ == "__main__":
    unittest.main()