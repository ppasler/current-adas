#!/usr/bin/python

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import threading
from time import sleep
import unittest

from data_collector import DataCollector


WINDOW_SIZE = 4
FIELDS = ["A", "B", "C"]

class DataCollectorTest(unittest.TestCase):

    def setUp(self):
        self.collector = DataCollector(DummyDataSource(WINDOW_SIZE), 
                                       FIELDS, 
                                       WINDOW_SIZE)
        dataHandler = lambda x: x
        self.collector.setHandler(dataHandler)
        self.notifyCalled = 0

    def notify(self, data):
        self.notifyCalled += 1

    def _fillValues(self, count):
        data = self.collector.datasource.data
        for i in range(count):
            self.collector._addData(data[i].sensors)

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
        self.assertEquals(win2.window["A"], {'quality': ['A_0', 'A_1'], 'value': ['A_0', 'A_1']})

        
        self._fillValues(WINDOW_SIZE / 2)
        self.assertEquals(win1.index, 2) 
        self.assertEquals(win2.window, initWindow) 

    def test_addData(self):
        win1, win2 = self.collector.windows
        win1.registerObserver(self)
        win2.registerObserver(self)
        
        self.assertEqual(self.notifyCalled, 0)
        
        # stop populating after 1 round
        collectorThread = threading.Thread(target=self.collector.collectData)
        collectorThread.start()
        
        sleep(0.1)
        self.collector.close()
        collectorThread.join()

        self.assertTrue(self.notifyCalled > 0)
    
    def test_filter(self):
        fields = ["A", "C"]
        self.collector.fields = fields
        
        data = self.collector.datasource.data;
        
        filteredData = self.collector.filter(data[0].sensors)
        
        self.assertEqual(len(filteredData), len(fields))
        self.assertTrue(set(filteredData.keys()).issubset(set(fields)))
        self.assertTrue(set(filteredData.keys()).issuperset(set(fields)))

        
class DummyDataSource(object):
    
    def __init__(self, length, infinite=False):
        self.data = self._buildData(length)
        self.infinite = infinite
        self.len = len(self.data)
        self.index = -1;

    def _buildData(self, length):
        ret = []
        for i in range(length):
            d = {}
            for c in FIELDS:
                d[c] = {"value": c + "_" + str(i), "quality": c + "_" + str(i**2)} 
            ret.append(DummyPacket(d))
        return ret

    def dequeue(self):
        self.index = (self.index+1) % self.len
        return self.data[self.index]

    def close(self):
        pass

class DummyPacket(object):
    def __init__(self, data):
        self.sensors = data

    
if __name__ == '__main__':
    unittest.main()












    
