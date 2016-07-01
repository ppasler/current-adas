#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 30.05.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

from Queue import Queue, Empty
import threading
from time import sleep

from config.config import ConfigProvider
from data_collector import DataCollector
from default_chain import ProcessingChain


class FeatureExtractor(object):
    '''
    Controls the processing chain and fetches the values needed for the classificator
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.collectorConfig = ConfigProvider().getCollectorConfig()
        
        self.inputQueue = Queue()
        self.outputQueue = Queue()
        self.extractQueue = Queue()
        
        self.collector = DataCollector(None, **self.collectorConfig)
        self.collectorThread = threading.Thread(target=self.collector.collectData)
        
        self.processor = ProcessingChain(self.inputQueue, self.outputQueue)
        self.processingThread = threading.Thread(target=self.processor.processData)

        self.extract = True

    def start(self):
        '''setting data handler and starts collecting'''
        print("%s: starting feature extractor" % self.__class__.__name__)   
        self.collector.setHandler(self.handleDataSet)  
        self.collectorThread.start()
        self.processingThread.start()
        
        while self.extract:
            try:
                procData = self.outputQueue.get(timeout=1)
                self.extractFeatures(procData)
            except Empty:
                pass
    
    def extractFeatures(self, data):
        #TODO fill with live
        self.extractQueue.put(data)
    
    def handleDataSet(self, data):
        '''Add the given data to the processingQueue'''
        self.inputQueue.put(data)
    
    def close(self):
        self.processor.close()
        self.processingThread.join()
        self.collector.close()
        self.collectorThread.join()
        print("%s: closing feature extractor" % self.__class__.__name__)     

        
if __name__ == "__main__":  # pragma: no cover
    extractor = FeatureExtractor()
    extractor.start()
    
    sleep(2)
    
    extractor.close()
