#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 20.01.2017

:author: Paul Pasler
:organization: Reutlingen University
'''

from base_test import *  # @UnusedWildImport
from util.eeg_data_source import EEGTablePacketSource, EEGTableWindowSource, \
    EEGTableDataSource


class TestEEGTableDataSource(BaseTest):

    def setUp(self):
        self.source = EEGTableDataSource()
        self.source.convert()

    def test_defaults(self):
        self.assertNotEqual(self.source.filepath, None)
        self.assertTrue(self.source.infinite)

    def test_hasQuality(self):
        self.source._hasQuality()
        self.assertTrue(self.source.hasQuality)

        self.source.header = [head for head in self.source.header if not head.startswith("Q")]
        self.source._hasQuality()
        self.assertFalse(self.source.hasQuality)

class TestEEGTablePacketSource(BaseTest):

    def setUp(self):
        self.source = EEGTablePacketSource()
        self.source.convert()

    def test_dequeue(self):
        data = self.source.dequeue() 
        self.assertEquals(len(data.sensors), 17)
        self.assertTrue("X" in data.sensors.keys())
        self.assertTrue("quality" in data.sensors["X"].keys())

class TestEEGTableWindowSource(BaseTest):

    def setUp(self):
        self.source = EEGTableWindowSource()
        self.source.convert()

    def test_dequeue(self):
        data = self.source.dequeue() 

        self.assertEquals(len(data), 16)
        self.assertTrue("X" in data.keys())
        self.assertTrue("quality" in data["X"].keys())

if __name__ == '__main__':
    unittest.main()
