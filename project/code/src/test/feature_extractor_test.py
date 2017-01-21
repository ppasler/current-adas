#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 02.07.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

from base_test import *  # @UnusedWildImport

import threading
from time import sleep

from window.data_collector import EEGDataCollector
from feature_extractor import FeatureExtractor
from util.eeg_data_source import EEGTablePacketSource


WINDOW_SIZE = 4
FIELDS = ["F3", "F4"]

class TestFeatureExtractor(BaseTest):


    # TODO test queue and threading
    def setUp(self):
        collector = self._initCollector()
        self.extractor = FeatureExtractor(collector)
        self.extractor.handleDataSet = self.handleDataSet
        self.handleDatasetCalled = 0 

    def handleDataSet(self, data):
        self.extractor.inputQueue.put(data)
        self.handleDatasetCalled += 1

    def _initCollector(self):
        source = EEGTablePacketSource()
        source.convert()
        collector = EEGDataCollector(source, FIELDS, WINDOW_SIZE)
        dataHandler = lambda x: x
        collector.setHandler(dataHandler)
        return collector

    def _getTotalQueueSize(self):
        return sum([self.extractor.inputQueue.qsize(), 
             self.extractor.outputQueue.qsize(), 
             self.extractor.extractQueue.qsize()])

    def test_run(self):
        eThread = threading.Thread(target=self.extractor.start)
        eThread.start()

        sleep(0.1)
        self.extractor.close()
        eThread.join()

        totalEntries = self._getTotalQueueSize() 
        self.assertTrue(self.handleDatasetCalled > 0)
        self.assertEqual(self.handleDatasetCalled, totalEntries)

    @unittest.skip("changes too often")
    def test_extractFeatures(self):
        pass

if __name__ == '__main__':
    unittest.main()