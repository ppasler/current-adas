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
from output.drowsiness_monitor import DrowsinessMonitor
from posdbos.app import PoSDBoS
from processor.data_processor import DataProcessor
from processor.mne_processor import MNEProcessor
from processor.eeg_processor import EEGProcessor
from processor.gyro_processor import GyroProcessor
from source.dummy_data_source import DummyWindowSource
from source.emotiv_connector import EmotivConnector
from util.file_util import FileUtil


scriptPath = os.path.dirname(os.path.abspath(__file__))

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
        windowSize = collectorConfig.get("windowSeconds")
        windowCount = collectorConfig.get("windowCount") 
        datasource = DummyWindowSource(demoFile, False, windowSize, windowCount)
        datasource.convert()
        return DummyDataCollector(datasource, collectedQueue, fields)

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