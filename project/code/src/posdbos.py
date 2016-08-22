#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 30.05.2016

:author: Paul Pasler
:organization: Reutlingen University
'''
from Queue import Empty
import os
import random
import threading

from classification.neural_network import NeuralNetwork
from config.config import ConfigProvider
from data_collector import DummyDataCollector, EEGDataCollector
from feature_extractor import FeatureExtractor
from output.drowsiness_monitor import DrowsinessMonitor
from util.eeg_table_util import EEGTableFileUtil

scriptPath = os.path.dirname(os.path.abspath(__file__))

class PoSDBoS(object):
    
    def __init__(self, networkFile=None, demo=False, demoFile=None):
        '''Main class for drowsiness detection
        
        :param string networkFile: file name of the saved neural network (path: "/../../data/<networkFile>.nn")
        '''
        self.demo = demo
        self.running = True
        self.config = ConfigProvider()
        self._initNeuralNetwork(networkFile)
        self._initFeatureExtractor(demoFile)
        self.dm = DrowsinessMonitor()
        self.fileUtil = EEGTableFileUtil()

    def _initNeuralNetwork(self, networkFile):
        nnCreate = self.config.getNNInitConfig()
        self.nn = NeuralNetwork()
        if networkFile == None:
            self.nn.createNew(**nnCreate)
        else:
            self.nn.load(networkFile)

    def _initFeatureExtractor(self, demoFile):
        collector = self._initDataCollector(demoFile)
        self.fe = FeatureExtractor(collector)
        self.inputQueue = self.fe.extractQueue

    def _initDataCollector(self, demoFile):
        collectorConfig = self.config.getCollectorConfig()
        if self.demo:
            return DummyDataCollector(demoFile, **collectorConfig)
        else:
            return EEGDataCollector(None, **collectorConfig)

    def close(self):
        self.running = False

    def run(self):
        fet = threading.Thread(target=self.fe.start)
        fet.start()
        dmt = threading.Thread(target=self.dm.run)
        dmt.start()
        features = []
        while self.running and dmt.is_alive():
            try:
                data = self.inputQueue.get(timeout=1)
                features.append(data)
                x = random.randint(1, 10)%2
                y = random.randint(1, 10)%2
                data = (x, y)
                
                clazz = self.nn.activate(data)
                info = "%d XOR %d is %d; queue: %d" % (x, y, clazz, self.inputQueue.qsize()) 
                self.dm.setStatus(clazz, info)
                #sleep(1)
            except Empty:
                pass
                #if self.demo:
                #    self.close()
            except KeyboardInterrupt:
                self.close()
            except Exception as e:
                print e.message
                self.close()
        self.writeFeature(features)
        self.fe.close()
        self.dm.close()
        dmt.join()

    def writeFeature(self, data):
        #filePath = scriptPath + "/../data/" + "awake_full_.csv"
        filePath = scriptPath + "/../data/" + "drowsy_full_.csv"

        header = []
        start = 4
        end = start + len(data[0])/6
        for field in self.config.getCollectorConfig().get("fields"):
            header.extend([str(x) + "Hz" + field for x in range(start, end)])
        self.fileUtil.writeFile(filePath, data, header)

if __name__ == '__main__': # pragma: no cover
    experiments = ConfigProvider().getExperimentConfig()
    experimentDir = scriptPath + "/../../captured_data/"
    dire = "test_data"
    #filePath = "%s%s/%s" % (experimentDir, dire, "awake_full.csv")
    filePath = "%s%s/%s" % (experimentDir, dire, "drowsy_full.csv")

    p = PoSDBoS("XOR_network", True, filePath)
    print "START"
    pt = threading.Thread(target=p.run)
    pt.start()

    pt.join()
    print "END"