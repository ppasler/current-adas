#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 13.06.2016

@author: Paul Pasler
:organization: Reutlingen University
'''
from Queue import Empty

from numpy import array

from config.config import ConfigProvider
from eeg_processor import SignalProcessor, FFTProcessor, SignalPreProcessor


class DataProcessor(object):
    
    def __init__(self, inputQueue, outputQueue):
        config = ConfigProvider()
        self.eegFields = config.getEmotivConfig()["eegFields"]
        self.gyroFields = config.getEmotivConfig()["gyroFields"]
        self.samplingRate = config.getEmotivConfig()["samplingRate"]
        
        self.processingConfig = config.getProcessingConfig()
        self.preProcessor = SignalPreProcessor()
        self.signalProcessor = SignalProcessor()
        self.fftProcessor = FFTProcessor()

        self.inputQueue = inputQueue
        self.outputQueue = outputQueue
        self.runProcess = True
        self.totalInvalid = 0
        self.totalCount = 0

    def close(self):
        self.runProcess = False

    def processData(self):
        while self.runProcess:
            try:
                data = self.inputQueue.get(timeout=1)
                procData, procInvalid = self.process(data)
                if not procInvalid:
                    self.outputQueue.put(procData)
            except Empty:
                pass
        print "invalid: ", self.totalInvalid
        print "total", self.totalCount

    def process(self, data):
        #TODO make me fast and nice
        eegRaw, gyroRaw = self.splitData(data)
        eegProc, eegInvalid = self.processEEGData(eegRaw)
        gyroProc, gyroIvalid = self.processGyroData(gyroRaw)
        eegProc.update(gyroProc)
        return eegProc, (eegInvalid or gyroIvalid)

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

        invalidCount = 0
        for _, signal in eegData.iteritems():
            raw = array(signal["value"])
            quality = array(signal["quality"])

            proc = self.preProcessor.process(raw)
            proc, _ = self.signalProcessor.process(raw, quality)

            chan, fInvalid = self.fftProcessor.process(proc)
            signal["theta"] = chan["theta"]
            invalidCount += sum([fInvalid])
        if invalidCount > 0:
            self.totalInvalid += 1
        self.totalCount += 1
        return eegData, (invalidCount > 0)

    def processGyroData(self, gyroData):
        return gyroData, False
