#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 30.05.2016

:author: Paul Pasler
:organization: Reutlingen University
'''
import os
from os.path import join, dirname
import sys
sys.path.append(join(dirname(__file__), '..'))

from collector.data_collector import EEGDataCollector
from config.config import ConfigProvider
from extractor.feature_extractor import FeatureExtractor
from posdbos_factory import PoSDBoSFactory
from source.dummy_data_source import DummyPacketSource


scriptPath = os.path.dirname(os.path.abspath(__file__))

class PoSDBoSTestFactory(PoSDBoSFactory):

    @staticmethod
    def getForTesting():
        self = PoSDBoSTestFactory

        posdbos= self._get()
        posdbos.nn = self.createNeuralNetwork()
        posdbos.fe = self.createTestFeatureExtractor(posdbos.collectedQueue, posdbos.processedQueue, posdbos.extractedQueue)

        return posdbos

    @staticmethod
    def createTestFeatureExtractor(collectedQueue, processedQueue, extractedQueue):
        collectorConfig = ConfigProvider().getCollectorConfig()
        fields = collectorConfig.get("fields")
        windowCount = collectorConfig.get("windowCount")
        samplingRate = 128
        collector = PoSDBoSTestFactory.createTestDataCollector(collectedQueue, fields, windowCount, samplingRate)
        processor = PoSDBoSFactory.createDataProcessor(collectedQueue, processedQueue)
        return FeatureExtractor(collector, processor, collectedQueue, processedQueue, extractedQueue)

    @staticmethod
    def createTestDataCollector(collectedQueue, fields, windowSize, samplingRate):
        collectorConfig = ConfigProvider().getCollectorConfig()
        windowCount = collectorConfig.get("windowCount") 
        datasource = DummyPacketSource()
        datasource.convert()
        return EEGDataCollector(datasource, collectedQueue, fields, windowSize, windowCount, samplingRate)