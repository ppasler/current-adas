#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 02.07.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

from base_test import *  # @UnusedWildImport

from Queue import Queue
import threading
from time import sleep

from posdbos_factory import PoSDBoSFactory


WINDOW_SIZE = 4
FIELDS = ["F3", "F4"]

class TestFeatureExtractor(BaseTest):

    # TODO test queue and threading
    def setUp(self):
        self._initQueues()
        self.extractor = PoSDBoSFactory.createTestFeatureExtractor(self.collectedQueue, self.processedQueue, self.extractedQueue)

    def _initQueues(self):
        self.collectedQueue = Queue()
        self.processedQueue = Queue()
        self.extractedQueue = Queue()

    def _getTotalQueueSize(self):
        return sum([self.collectedQueue.qsize(), 
             self.processedQueue.qsize(), 
             self.extractedQueue.qsize()])

    def test_run(self):
        eThread = threading.Thread(target=self.extractor.start)
        eThread.start()

        self.assertEqual(self._getTotalQueueSize(), 0)

        sleep(0.1)
        self.extractor.close()
        eThread.join()

        totalEntries = self._getTotalQueueSize() 
        self.assertNotEqual(totalEntries, 0)
        self.assertNotEqual(self.extractedQueue, 0)

    @unittest.skip("changes too often")
    def test_extractFeatures(self):
        pass

if __name__ == '__main__':
    unittest.main()