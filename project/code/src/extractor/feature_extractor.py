#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 30.05.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

from Queue import Empty
import threading

from numpy import array


class FeatureExtractor(object):
    '''
    Controls the processor chain and fetches the values needed for the classificator
    '''

    def __init__(self, dataCollector, dataProcessor, collectedQueue, processedQueue, extractedQueue):

        self.collectedQueue = collectedQueue
        self.processedQueue = processedQueue
        self.extractedQueue = extractedQueue

        self.collector = dataCollector
        self.collectorThread = threading.Thread(target=self.collector.collectData)
        
        self.processor = dataProcessor
        self.processingThread = threading.Thread(target=self.processor.processData)

        self.extract = True

    def start(self):
        '''setting data handler and starts collecting'''
        print("%s: starting feature extractor" % self.__class__.__name__)   
        self.collectorThread.start()
        self.processingThread.start()
        
        while self.extract:
            try:
                procData = self.processedQueue.get(timeout=1)
                self.extractFeatures(procData)
            except Empty:
                pass
    
    def extractFeatures(self, data):
        features = []
        for _, sigData in data.iteritems():
            theta = sigData["theta"]
            features.extend(theta)
        self.extractedQueue.put(array(features))
    
    def close(self):
        self.processor.close()
        self.processingThread.join()
        self.collector.close()
        self.collectorThread.join()
        self.extract = False
        print("%s: closing feature extractor" % self.__class__.__name__)