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
        if self.demo:
            fields = self.config.getProcessingConfig().get("fields")
            return DummyDataCollector(demoFile, fields=fields)
        else:
            collectorConfig = self.config.getCollectorConfig()
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
                if self.demo:
                    self.close()
            except KeyboardInterrupt:
                self.close()
            except Exception as e:
                print e.message
                self.close()
        #save here
        # features
        self.fe.close()
        self.dm.close()
        dmt.join()

if __name__ == '__main__': # pragma: no cover
    experiments = ConfigProvider().getExperimentConfig()
    scriptPath = os.path.dirname(os.path.abspath(__file__))
    experimentDir = scriptPath + "/../../captured_data/"
    person = "janis"
    #filePath = "%s%s/%s" % (experimentDir, person, experiments[person][0])
    filePath = "%s%s/%s" % (experimentDir, person+"/parts", "2016-07-12-11-15_EEG_8.csv")

    p = PoSDBoS("XOR_network", True, filePath)
    print "START"
    pt = threading.Thread(target=p.run)
    pt.start()

    pt.join()
    print "END"