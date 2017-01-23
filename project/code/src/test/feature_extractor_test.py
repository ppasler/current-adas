#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 02.07.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

from Queue import Queue
import threading
from time import sleep

from base_test import *  # @UnusedWildImport
from collector.data_collector import EEGDataCollector
from extractor.feature_extractor import FeatureExtractor
from processor.data_processor import DataProcessor
from processor.eeg_processor import EEGProcessor
from processor.gyro_processor import GyroProcessor
from util.eeg_data_source import EEGTablePacketSource


WINDOW_SIZE = 4
FIELDS = ["F3", "F4"]

class TestFeatureExtractor(BaseTest):

    # TODO test queue and threading
    def setUp(self):
        self._initQueues()
        collector = self._initCollector()
        processor = self._initDataProcessor()
        self.extractor = FeatureExtractor(collector, processor, self.collectedQueue, self.processedQueue, self.extractedQueue)
        self.extractor.handleDataSet = self.handleDataSet
        self.handleDatasetCalled = 0 

    def _initQueues(self):
        self.collectedQueue = Queue()
        self.processedQueue = Queue()
        self.extractedQueue = Queue()

    def handleDataSet(self, data):
        self.extractor.collectedQueue.put(data)
        self.handleDatasetCalled += 1

    def _initCollector(self):
        source = EEGTablePacketSource()
        source.convert()
        collector = EEGDataCollector(source, FIELDS, WINDOW_SIZE)
        dataHandler = lambda x: x
        collector.setHandler(dataHandler)
        return collector

    def _initDataProcessor(self):
        return DataProcessor(self.collectedQueue, self.processedQueue, EEGProcessor(), GyroProcessor())


    def _getTotalQueueSize(self):
        return sum([self.collectedQueue.qsize(), 
             self.processedQueue.qsize(), 
             self.extractedQueue.qsize()])

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