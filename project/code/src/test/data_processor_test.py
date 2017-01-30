#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 20.01.2017

:author: Paul Pasler
:organization: Reutlingen University
'''

from base_test import *  # @UnusedWildImport

from Queue import Queue
from numpy.testing.utils import assert_allclose
from numpy import NaN

from collector.data_collector import DummyDataCollector
from source.dummy_data_source import DummyWindowSource
from test.posdbos_test_factory import PoSDBoSTestFactory
from config.config import ConfigProvider
from processor.eeg_processor import SignalProcessor
from util.quality_util import QualityUtil


WINDOW_SECONDS = 4
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

class TestDataProcessor(BaseTest):

    def setUp(self):
        self.fields = TEST_DATA.keys()
        self.collectedQueue = Queue()
        self.processedQueue = Queue()

        self.processor = PoSDBoSTestFactory.createDataProcessor(self.collectedQueue, self.processedQueue)

    def _addData(self, data):
        self.collectedQueue.put(data)

    def _fillQueue(self):
        datasource = DummyWindowSource(self.getData1024CSV(), False, 1, 2)
        datasource.convert()
        dc = DummyDataCollector(datasource, self.collectedQueue, self.fields)
        dc.collectData()

    def test_run(self):
        self._fillQueue()

        inpSize = self.collectedQueue.qsize()
        self.assertEqual(self.processedQueue.qsize(), 0)

        self.processor.processData()

        self.assertEqual(self.collectedQueue.qsize(), 0)
        self.assertEqual(self.processedQueue.qsize(), inpSize)

    def test_process(self):
        self.processor.process(TEST_DATA)

    def test_splitData(self):
        eegData, gyroData = self.processor.splitData(TEST_DATA)
        intersect = set(eegData) & set(gyroData)
        self.assertTrue(len(intersect) == 0)
        self.assertTrue("F3" in eegData)
        self.assertTrue("X" in gyroData)

class TestSignalProcessor(BaseTest):

    def setUp(self):
        self.chain = SignalProcessor()
        self.qualUtil = QualityUtil()
        config = ConfigProvider().getProcessingConfig()
        self.upperBound = config.get("upperBound")
        self.lowerBound = config.get("lowerBound")
        self.minQuality = config.get("minQual")
        self.maxNaNValues = config.get("maxNaNValues")

    def _checkValidData(self, data, invalid):
        self.assertEqual(invalid, self.maxNaNValues < np.count_nonzero(np.isnan(data)))

    def test_process_sunshine(self):
        data = [self.lowerBound, self.lowerBound / 2.0, 0, self.upperBound / 2.0, self.upperBound]
        qual = [15, 15, 15, 15, 15]

        proc, invalidData = self.chain.process(data, qual)
        self._checkValidData(proc, invalidData)
        assert_allclose(proc, [-1.0, -0.5, 0, 0.5, 1])

    @unittest.skip("unused")
    def test_process_badQuality(self):
        data = [-2.0, -1.0, 0, 1.0, 2.0]
        qual = [15, 0, self.minQuality-1, self.minQuality, self.minQuality+1]

        proc, invalidData = self.chain.process(data, qual)
        self._checkValidData(proc, invalidData)
        np.assert_allclose(proc, [-1.0, NaN, NaN, 0.5, 1])

    @unittest.skip("unused")
    def test_process_replaceSequences(self):
        data = [1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 4.0]
        qual = [15, 15,15, 15, 15, 15, 15]

        proc, invalidData = self.chain.process(data, qual)
        self._checkValidData(proc, invalidData)
        np.assert_allclose(proc, [NaN, NaN, NaN, NaN, NaN, 0.5, 1.0])

    def test_process_replaceOutliners(self):
        data = [-5000, self.lowerBound-1, self.lowerBound, self.lowerBound+1, self.upperBound-1, self.upperBound, self.upperBound+1, 5000]
        qual = [15, 15, 15, 15, 15, 15, 15, 15]

        proc, invalidData = self.chain.process(data, qual)
        self._checkValidData(proc, invalidData)
        self.assertEquals(np.count_nonzero(proc), 4)

    def test_checkValid(self):
        maxNaNValues = self.maxNaNValues
        for length in range(0, maxNaNValues+1):
            data = self._getNaNList(length)
            qual = [15]*length
            _, invalidData = self.chain.process(data, qual)
            self.assertFalse(invalidData, "length %d" % length)
        
        for length in range(maxNaNValues+1, maxNaNValues+5):
            data = self._getNaNList(length)
            qual = [15]*length
            _, invalidData = self.chain.process(data, qual)
            self.assertTrue(invalidData, "length %d" % length)

    def _getNaNList(self, length):
        return np.array([NaN]*length)

if __name__ == '__main__':
    unittest.main()