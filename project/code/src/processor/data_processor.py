#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 13.06.2016

@author: Paul Pasler
:organization: Reutlingen University
'''
from Queue import Empty

from config.config import ConfigProvider


class DataProcessor(object):

    def __init__(self, collectedQueue, processedQueue, eegProcessor, gyroProcessor):
        config = ConfigProvider()
        self.eegFields = config.getEmotivConfig()["eegFields"]
        self.gyroFields = config.getEmotivConfig()["gyroFields"]
        self.samplingRate = config.getEmotivConfig()["samplingRate"]
        self.processingConfig = config.getProcessingConfig()

        self.eegProcessor = eegProcessor
        self.gyroProcessor = gyroProcessor

        self.collectedQueue = collectedQueue
        self.processedQueue = processedQueue
        self.runProcess = True

    def close(self):
        self.runProcess = False

    def processData(self):
        while self.runProcess:
            try:
                data = self.collectedQueue.get(timeout=1)
                try:
                    procData, procInvalid = self.process(data)
                    if not procInvalid:
                        self.processedQueue.put(procData)
                except Exception as e:
                    print e.message
                    pass
            except Empty:
                self.close()

    def process(self, data):
        #TODO make me fast and nice
        eegRaw, gyroRaw = self.splitData(data)

        eegProc, eegInvalid = self.eegProcessor.process(eegRaw)
        gyroProc, gyroInvalid = self.gyroProcessor.process(gyroRaw)

        self.reuniteData(eegProc, gyroProc)
        return eegProc, (eegInvalid or gyroInvalid)

    def reuniteData(self, eegData, gyroData):
        pass#eegData.update(gyroData)

    def splitData(self, data):
        '''split eeg and gyro data
        
        :param data: all values as dict
        
        :return: 
            eegData: eeg values as dict
            gyroData: gyro values as dict
        '''
        eegData = self.filterDictByKey(data, self.eegFields)
        gyroData = self.filterDictByKey(data, self.gyroFields)
        return eegData, gyroData

    def filterDictByKey(self, data, keys):
        return {key: data[key] for key in keys if key in data}