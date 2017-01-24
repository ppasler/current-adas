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
from util.eeg_data_source import EEGTablePacketSource
from test.posdbos_test_factory import PoSDBoSTestFactory


WINDOW_SIZE = 4
FIELDS = ["F3", "F4", "X", "Y"]

class DataCollectorTest(BaseTest):

    def setUp(self):
        self.collectedQueue = Queue()
        self.collector = PoSDBoSTestFactory.createTestDataCollector(self.collectedQueue, FIELDS, WINDOW_SIZE)

    def _fillValues(self, count):
        data = self.collector.datasource.data
        fields = self.collector.fields
        for i in range(count):
            row = data[i].sensors
            fData = {x: row[x] for x in fields}
            self.collector._addData(fData)

    def _fillWindowFull(self):
        self._fillValues(WINDOW_SIZE)

    def getInitWindow(self):
        d = {}
        for key in FIELDS:
            d[key] = {"value": [], "quality": []} 
        return d

    def test_windowsFilled(self):
        initWindow = self.getInitWindow()
                
        win1 = self.collector.windows[0]
        win2 = self.collector.windows[1]
        
        self.assertEquals(win1.index, WINDOW_SIZE / 2)
        self.assertEquals(win1.window, initWindow)
        self.assertEquals(win2.index, 0)
        self.assertEquals(win2.window, initWindow)
        
        self._fillValues(WINDOW_SIZE / 2)
        self.assertEquals(win1.window, initWindow)
        self.assertEquals(win1.index, 0) 
        self.assertEquals(win2.index, WINDOW_SIZE / 2)
        self.assertEquals(win2.window["X"], {'quality': [0, 0], 'value': [24.0, 24.0]})

        self._fillValues(WINDOW_SIZE / 2)
        self.assertEquals(win1.index, 2) 
        self.assertEquals(win2.window, initWindow) 

    def test_addData(self):
        self.assertEqual(self.collectedQueue.qsize(), 0)

        # stop populating after 1 round
        collectorThread = threading.Thread(target=self.collector.collectData)
        collectorThread.start()

        sleep(0.1)
        self.collector.close()
        collectorThread.join()

        self.assertTrue(self.collectedQueue.qsize() > 0)

    def test_filter(self):
        fields = ["F3", "X"]
        self.collector.fields = fields
        
        data = self.collector.datasource.data;
        
        filteredData = self.collector._filter(data[0].sensors)
        
        self.assertEqual(len(filteredData), len(fields))
        self.assertTrue(set(filteredData.keys()).issubset(set(fields)))
        self.assertTrue(set(filteredData.keys()).issuperset(set(fields)))

if __name__ == '__main__':
    unittest.main()