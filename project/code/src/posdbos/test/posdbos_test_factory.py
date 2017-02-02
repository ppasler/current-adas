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
from posdbos.output.drowsiness_monitor import DrowsinessMonitor
sys.path.append(join(dirname(__file__), '..'))

from posdbos.collector.data_collector import EEGDataCollector
from config.config import ConfigProvider
from posdbos.factory import PoSDBoSFactory
from posdbos.source.dummy_data_source import DummyPacketSource


scriptPath = os.path.dirname(os.path.abspath(__file__))

class TestFactory(PoSDBoSFactory):

    @staticmethod
    def getForTesting():
        self = TestFactory

        app = self._get()
        app.nn = self.createNeuralNetwork()
        app.dm = DrowsinessMonitor()

        collectorConfig = ConfigProvider().getCollectorConfig()
        fields = collectorConfig.get("fields")
        windowSeconds = collectorConfig.get("windowSeconds")
        windowCount = collectorConfig.get("windowCount")
        samplingRate = 128
        app.dc = self.createTestDataCollector(app.collectedQueue, fields, windowSeconds, samplingRate, windowCount)
        app.dp = self.createDataProcessor(app.collectedQueue, app.extractedQueue)
        return app

    @staticmethod
    def createTestProcessor(collectedQueue, extractedQueue):
        return PoSDBoSFactory.createDataProcessor(collectedQueue, extractedQueue)

    @staticmethod
    def createTestDataCollector(collectedQueue, fields, windowSeconds, samplingRate, windowCount):
        datasource = DummyPacketSource()
        datasource.convert()
        return EEGDataCollector(datasource, collectedQueue, fields, windowSeconds, windowCount, samplingRate)