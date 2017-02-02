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
from output.drowsiness_monitor import DrowsinessMonitor
sys.path.append(join(dirname(__file__), '..'))

from collector.data_collector import EEGDataCollector
from config.config import ConfigProvider
from posdbos_factory import PoSDBoSFactory
from source.dummy_data_source import DummyPacketSource


scriptPath = os.path.dirname(os.path.abspath(__file__))

class PoSDBoSTestFactory(PoSDBoSFactory):

    @staticmethod
    def getForTesting():
        self = PoSDBoSTestFactory

        posdbos= self._get()
        posdbos.nn = self.createNeuralNetwork()
        posdbos.dm = DrowsinessMonitor()

        collectorConfig = ConfigProvider().getCollectorConfig()
        fields = collectorConfig.get("fields")
        windowSeconds = collectorConfig.get("windowSeconds")
        windowCount = collectorConfig.get("windowCount")
        samplingRate = 128
        posdbos.dc = self.createTestDataCollector(posdbos.collectedQueue, fields, windowSeconds, samplingRate, windowCount)
        posdbos.dp = self.createDataProcessor(posdbos.collectedQueue, posdbos.extractedQueue)
        return posdbos

    @staticmethod
    def createTestProcessor(collectedQueue, extractedQueue):
        return PoSDBoSFactory.createDataProcessor(collectedQueue, extractedQueue)

    @staticmethod
    def createTestDataCollector(collectedQueue, fields, windowSeconds, samplingRate, windowCount):
        datasource = DummyPacketSource()
        datasource.convert()
        return EEGDataCollector(datasource, collectedQueue, fields, windowSeconds, windowCount, samplingRate)