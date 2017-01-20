#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 20.01.2017

:author: Paul Pasler
:organization: Reutlingen University
'''

from base_test import * # @UnusedWildImport

from util.eeg_data_source import EEGTablePacketSource


class TestEEGTablePacketSource(BaseTest):

    def setUp(self):
        self.util = EEGTablePacketSource()
        self.util.convert()

    def test_dequeue(self):
        data = self.util.dequeue() 
        self.assertEquals(len(data.sensors), 17)
        self.assertTrue("X" in data.sensors.keys())
        self.assertTrue("quality" in data.sensors["X"].keys())


if __name__ == '__main__':
    unittest.main()
