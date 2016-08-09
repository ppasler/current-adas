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
from time import sleep

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
        nn_conf = self.config.getNeuralNetworkConfig()
        self.nn = NeuralNetwork()
        if networkFile == None:
            self.nn.createNew(nn_conf["nInputs"], nn_conf["nHiddenLayers"], nn_conf["nOutput"], nn_conf["bias"])
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
        filePath = scriptPath + "/../data/" + "test.csv"
        header = []
        for field in ["F3", "F4", "F7", "F8"]:
            for i in range(1, 5):
                header.append("%s_%s" % (field ,str(i)))
        self.fileUtil.writeFile(filePath, data, header)

if __name__ == '__main__': # pragma: no cover
    experiments = ConfigProvider().getExperimentConfig()
    experimentDir = scriptPath + "/../../captured_data/"
    person = "janis"
    filePath = "%s%s/%s" % (experimentDir, person, experiments[person][0])
    print filePath
    #filePath = "%s%s/%s" % (experimentDir, person+"/parts", "2016-07-12-11-15_EEG_8.csv")

    p = PoSDBoS("XOR_network", True, filePath)
    print "START"
    pt = threading.Thread(target=p.run)
    pt.start()

    pt.join()
    print "END"