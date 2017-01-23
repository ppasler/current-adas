#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 30.05.2016

:author: Paul Pasler
:organization: Reutlingen University
'''
from Queue import Queue, Empty
import os
import threading
from time import time, sleep

from classificator.neural_network import NeuralNetwork
from collector.data_collector import DummyDataCollector, EEGDataCollector
from config.config import ConfigProvider
from emotiv_connector import EmotivConnector
from extractor.feature_extractor import FeatureExtractor
from output.drowsiness_monitor import DrowsinessMonitor
from processor.data_processor import DataProcessor
from processor.eeg_processor import EEGProcessor
from processor.gyro_processor import GyroProcessor
from util.eeg_data_source import EEGTableWindowSource
from util.file_util import FileUtil


scriptPath = os.path.dirname(os.path.abspath(__file__))

class PoSDBoS(object):

    def __init__(self, networkFile=None, demo=False, demoFile=None):
        '''Main class for drowsiness detection
        
        :param string networkFile: file name of the saved neural network (path: "/../../data/<networkFile>.nn")
        '''
        self.demo = demo
        self.running = True
        self.config = ConfigProvider()
        self._initPoSDBoS()
        self._initNeuralNetwork(networkFile)
        self._initQueues()
        self._initFeatureExtractor(demoFile)
        self.dm = DrowsinessMonitor()
        self.fileUtil = FileUtil()

    def _initQueues(self):
        self.collectedQueue = Queue()
        self.processedQueue = Queue()
        self.extractedQueue = Queue()

    def _initPoSDBoS(self):
        posdbosConfig = self.config.getPoSDBoSConfig()
        self.drowsyMinCount = posdbosConfig.get("drowsyMinCount")
        self.awakeMinCount = posdbosConfig.get("awakeMinCount")
        self.classified = [0, 0]
        self.curClass = 0
        self.classCount = 0
        self.found = 0

    def _initNeuralNetwork(self, networkFile):
        nnCreate = self.config.getNNInitConfig()
        self.nn = NeuralNetwork()
        if networkFile == None:
            self.nn.createNew(**nnCreate)
        else:
            self.nn.load(networkFile)

    def _initFeatureExtractor(self, demoFile):
        self.demoFile = demoFile
        collector = self._initDataCollector(self.demoFile)
        processor = self._initDataProcessor()
        self.fe = FeatureExtractor(collector, processor, self.collectedQueue, self.processedQueue, self.extractedQueue)

    def _initDataCollector(self, demoFile):
        collectorConfig = self.config.getCollectorConfig()
        fields = collectorConfig.get("fields")
        windowSize = collectorConfig.get("windowSize")
        windowCount =collectorConfig.get("windowCount") 
        if self.demo:
            datasource = EEGTableWindowSource(demoFile, False, windowSize, windowCount)
            datasource.convert()
            return DummyDataCollector(datasource, self.collectedQueue, fields, windowSize, windowCount)
        else:
            return EEGDataCollector(EmotivConnector(), self.collectedQueue, fields, windowSize, windowCount)

    def _initDataProcessor(self):
        return DataProcessor(self.collectedQueue, self.processedQueue, EEGProcessor(), GyroProcessor())

    def stop(self):
        self.running = False

    def close(self):
        self.running = False
        self.fe.close()
        self.dm.close()

    def run(self):
        fet = threading.Thread(target=self.fe.start)
        fet.start()
        dmt = threading.Thread(target=self.dm.run)
        dmt.start()
        features = []
        total = 0
        start = time()
        c = []
        while self.running and dmt.is_alive():
            try:
                #awake = 0, drowsy = 1
                data = self.extractedQueue.get(timeout=1)
                features.append(data)
                clazz = self.nn.activate(data, True)
                c.append([clazz, clazz])
                self.setState(clazz)
                total += 1
            except Empty:
                print "Needed %.2fs for %d windows" % (time() - start, total) 
                self.stop()
            except KeyboardInterrupt:
                self.close()
            except Exception as e:
                print e.message
                self.close()


        while dmt.is_alive():
            try:
                sleep(1)
            except KeyboardInterrupt:
                self.close()
        #self.writeFeature(c)
        self.close()
        fet.join()
        dmt.join()
        print "done"

    def setState(self, clazz):
        self.classified[clazz] += 1
        if self.curClass == clazz:
            self.classCount += 1
        else:
            self.curClass = clazz
            self.classCount = 0

        info = "class %d row (%s)" % (clazz, str(self.classCount))
        if clazz == 1 and self.classCount >= self.drowsyMinCount:
            self.dm.setState(clazz, info)
            self.found += 1
        elif clazz == 0 and self.classCount >= self.awakeMinCount:
            self.dm.setState(clazz, info)

    def writeFeature(self, data):
        filePath = scriptPath + "/../data/" + "classes.csv"
        #filePath = scriptPath + "/../data/" + "drowsy_full_.csv"

        header = ["clazz", "clazz2"]
        #start = 4
        #end = start + len(data[0])/6
        #for field in self.config.getCollectorConfig().get("fields"):
        #    header.extend([str(x) + "Hz" + field for x in range(start, end)])
        self.fileUtil.saveCSV(filePath, data, header)