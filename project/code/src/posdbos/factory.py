#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 30.05.2016

:author: Paul Pasler
:organization: Reutlingen University
'''
from Queue import Queue

from config.config import ConfigProvider
from posdbos.classificator.neural_network import NeuralNetwork
from posdbos.collector.data_collector import DummyDataCollector, EEGDataCollector
from output.drowsiness_monitor import DrowsinessMonitor
from posdbos.app import PoSDBoS
from posdbos.processor.data_processor import DataProcessor
from posdbos.processor.eeg_processor import EEGProcessor
from posdbos.processor.gyro_processor import GyroProcessor
from posdbos.processor.mne_processor import MNEProcessor
from posdbos.source.dummy_data_source import DummyWindowSource, DummyPacketSource
from posdbos.source.emotiv_connector import EmotivConnector
from posdbos.util.file_util import FileUtil


class Factory(object):

    @staticmethod
    def getForDemo(networkFile, demoFile):
        self = Factory

        posdbos= self._get()
        posdbos.dm = DrowsinessMonitor()
        posdbos.nn = self.loadNeuralNetwork(networkFile)
        posdbos.dc = Factory.createDemoDataCollector(demoFile, posdbos.collectedQueue)
        posdbos.dp = Factory.createDataProcessor(posdbos.collectedQueue, posdbos.extractedQueue)

        return posdbos

    @staticmethod
    def getForSave(filePath):
        self = Factory

        posdbos = self._get()
        posdbos.dc = self.createDemoDataCollector(filePath, posdbos.collectedQueue)
        posdbos.dp = self.createDataProcessor(posdbos.collectedQueue, posdbos.extractedQueue)

        return posdbos

    @staticmethod
    def _get():
        self = Factory

        posdbos= self._initPoSDBoS(True)
        posdbos.collectedQueue = Queue()
        posdbos.extractedQueue = Queue()

        posdbos.fileUtil = FileUtil()
        return posdbos

    @staticmethod
    def _initPoSDBoS(demo):
        posdbos = PoSDBoS()
        posdbos.demo = demo
        posdbos.running = True

        posdbosConfig = ConfigProvider().getPoSDBoSConfig()
        posdbos.drowsyMinCount = posdbosConfig.get("drowsyMinCount")
        posdbos.awakeMinCount = posdbosConfig.get("awakeMinCount")

        posdbos.classified = [0, 0]
        posdbos.curClass = 0
        posdbos.classCount = 0
        posdbos.found = 0
        return posdbos

    @staticmethod
    def createNeuralNetwork():
        nnCreate = ConfigProvider().getNNInitConfig()
        return NeuralNetwork().createNew(**nnCreate)

    @staticmethod
    def loadNeuralNetwork(networkFile, defaultPath=True):
        return NeuralNetwork().load(networkFile, defaultPath)

    @staticmethod
    def createDemoDataCollector(demoFile, collectedQueue):
        collectorConfig = ConfigProvider().getCollectorConfig()
        fields = collectorConfig.get("fields")
        windowSeconds = collectorConfig.get("windowSeconds")
        windowCount = collectorConfig.get("windowCount") 
        datasource = Factory.createDummyWindowSource(demoFile, windowSeconds, windowCount)
        return DummyDataCollector(datasource, collectedQueue, fields)

    @staticmethod
    def createDemoEEGDataCollector(demoFile, collectedQueue):
        collectorConfig = ConfigProvider().getCollectorConfig()
        fields = collectorConfig.get("fields")
        windowSeconds = collectorConfig.get("windowSeconds")
        windowCount = collectorConfig.get("windowCount") 
        datasource = Factory.createDummyPacketSource(demoFile)
        return EEGDataCollector(datasource, collectedQueue, fields, windowSeconds, windowCount, 128)

    @staticmethod
    def createDummyWindowSource(demoFile, windowSize, windowCount):
        datasource = DummyWindowSource(demoFile, False, windowSize, windowCount)
        datasource.convert()
        return datasource

    @staticmethod
    def createDummyPacketSource(demoFile):
        datasource = DummyPacketSource(demoFile, False)
        datasource.convert()
        return datasource

    @staticmethod
    def createEmotivDataCollector(collectedQueue):
        collectorConfig = ConfigProvider().getCollectorConfig()
        fields = collectorConfig.get("fields")
        windowSize = collectorConfig.get("windowSeconds")
        windowCount = collectorConfig.get("windowCount") 
        return EEGDataCollector(EmotivConnector(), collectedQueue, fields, windowSize, windowCount)

    @staticmethod
    def createDataProcessor(collectedQueue, extractedQueue):
        return DataProcessor(collectedQueue, extractedQueue, EEGProcessor(), GyroProcessor())

    @staticmethod
    def createMNEDataProcessor(collectedQueue, extractedQueue):
        return DataProcessor(collectedQueue, extractedQueue, MNEProcessor(), GyroProcessor())