#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 13.06.2016

@author: Paul Pasler
:organization: Reutlingen University
'''
from numpy import array

from config.config import ConfigProvider
from util.eeg_util import EEGUtil
from util.quality_util import QualityUtil
from util.signal_util import SignalUtil
from Queue import Empty
from eeg_processor import EEGProcessor


class DataProcessor(object):
    
    def __init__(self, inputQueue, outputQueue):
        config = ConfigProvider()
        self.eegFields = config.getEmotivConfig()["eegFields"]
        self.gyroFields = config.getEmotivConfig()["gyroFields"]
        self.samplingRate = config.getConfig("eeg")["samplingRate"]
        
        self.processingConfig = config.getProcessingConfig()
        self.qualityUtil = QualityUtil()
        self.signalUtil = SignalUtil()
        self.eegUtil = EEGUtil()
        self.eegProcessor = EEGProcessor()
        
        self.inputQueue = inputQueue
        self.outputQueue = outputQueue
        self.runProcess = True

    def close(self):
        self.runProcess = False

    def processData(self):
        while self.runProcess:
            try:
                data = self.inputQueue.get(timeout=1)
                procData = self.process(data)
                self.outputQueue.put(procData)
            except Empty:
                pass

    def process(self, data):
        #TODO make me fast and nice
        eegRaw, gyroRaw = self.splitData(data)
        return self.processEEGData(eegRaw), gyroRaw

    def splitData(self, data):
        '''split eeg and gyro data
        
        :param data: all values as dict
        
        :return: 
            eegData: eeg values as dict
            gyroData: gyro values as dict
        '''
        #TODO handle data except eeg and gyro?
        eegData = {x: data[x] for x in data if x in self.eegFields}
        gyroData = {x: data[x] for x in data if x in self.gyroFields}
        return eegData, gyroData

    def processEEGData(self, eegData):
        ret = {}
        for field, signal in eegData.iteritems():
            raw = array(signal["value"])
            quality = array(signal["quality"])

            ret[field] = self.eegProcessor.process(raw, quality) 
        return ret

    def processGyroData(self, gyroData):
        pass#print gyroData
