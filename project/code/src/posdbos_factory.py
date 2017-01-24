#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 30.05.2016

:author: Paul Pasler
:organization: Reutlingen University
'''
from Queue import Queue
import os

from classificator.neural_network import NeuralNetwork
from collector.data_collector import DummyDataCollector, EEGDataCollector
from config.config import ConfigProvider
from emotiv_connector import EmotivConnector
from extractor.feature_extractor import FeatureExtractor
from output.drowsiness_monitor import DrowsinessMonitor
from posdbos import PoSDBoS
from processor.data_processor import DataProcessor
from processor.eeg_processor import EEGProcessor
from processor.gyro_processor import GyroProcessor
from util.eeg_data_source import EEGTableWindowSource
from util.file_util import FileUtil


scriptPath = os.path.dirname(os.path.abspath(__file__))

class PoSDBoSFactory(object):

    @staticmethod
    def getForDemo(networkFile, demoFile):
        self = PoSDBoSFactory

        posdbos= self._get()
        posdbos.nn = self.loadNeuralNetwork(networkFile)
        posdbos.fe = self.createFeatureExtractor(demoFile, posdbos.collectedQueue, posdbos.processedQueue, posdbos.extractedQueue)

        return posdbos

    @staticmethod
    def getForSave(filePath):
        self = PoSDBoSFactory

        posdbos= self._get()
        posdbos.fe = self.createFeatureExtractor(filePath, posdbos.collectedQueue, posdbos.processedQueue, posdbos.extractedQueue)

        return posdbos

    @staticmethod
    def _get():
        self = PoSDBoSFactory

        posdbos= self._initPoSDBoS(True)
        posdbos.collectedQueue = Queue()
        posdbos.processedQueue = Queue()
        posdbos.extractedQueue = Queue()

        posdbos.dm = DrowsinessMonitor()
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
    def loadNeuralNetwork(networkFile):
        return NeuralNetwork().load(networkFile)

    @staticmethod
    def createFeatureExtractor(demoFile, collectedQueue, processedQueue, extractedQueue):
        collector = PoSDBoSFactory.createDemoDataCollector(demoFile, collectedQueue)
        processor = PoSDBoSFactory.createDataProcessor(collectedQueue, processedQueue)
        return FeatureExtractor(collector, processor, collectedQueue, processedQueue, extractedQueue)

    @staticmethod
    def createDemoDataCollector(demoFile, collectedQueue):
        collectorConfig = ConfigProvider().getCollectorConfig()
        fields = collectorConfig.get("fields")
        windowSize = collectorConfig.get("windowSize")
        windowCount = collectorConfig.get("windowCount") 
        datasource = EEGTableWindowSource(demoFile, False, windowSize, windowCount)
        datasource.convert()
        return DummyDataCollector(datasource, collectedQueue, fields, windowSize, windowCount)

    @staticmethod
    def createEmotivDataCollector(collectedQueue):
        collectorConfig = ConfigProvider().getCollectorConfig()
        fields = collectorConfig.get("fields")
        windowSize = collectorConfig.get("windowSize")
        windowCount = collectorConfig.get("windowCount") 
        return EEGDataCollector(EmotivConnector(), collectedQueue, fields, windowSize, windowCount)

    @staticmethod
    def createDataProcessor(collectedQueue, processedQueue):
        return DataProcessor(collectedQueue, processedQueue, EEGProcessor(), GyroProcessor())