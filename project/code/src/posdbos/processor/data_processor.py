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
import logging

class DataProcessor(object):

    def __init__(self, collectedQueue, extractedQueue, eegProcessor, gyroProcessor):
        config = ConfigProvider()
        self.eegFields = config.getEmotivConfig()["eegFields"]
        self.gyroFields = config.getEmotivConfig()["gyroFields"]
        self.samplingRate = config.getEmotivConfig()["samplingRate"]
        self.processingConfig = config.getProcessingConfig()

        self.eegProcessor = eegProcessor
        self.gyroProcessor = gyroProcessor

        self.collectedQueue = collectedQueue
        self.extractedQueue = extractedQueue
        self.runProcess = True

    def close(self):
        self.runProcess = False

    def processData(self):
        logging.info("starting data processing")
        while self.runProcess:
            try:
                dto = self.collectedQueue.get(timeout=1)
                try:
                    procData, procInvalid = self.process(dto)
                    if not procInvalid:
                        extData = self._extractFeatures(procData)
                        self.extractedQueue.put(extData)
                except Exception as e:
                    logging.exception(e.message)
            except Empty:
                logging.warn("collectedQueue empty")
                self.close()
        logging.info("ending data processing")

    def extractFeatures(self, data):
        return data.flatten()

    def _extractFeatures(self, dto):
        features = []
        for key in dto:
            theta = dto.getField(key, "theta")
            features.extend(theta)
        return array(features)

    def process(self, dto):
        #TODO make me fast and nice
        eegDto, gyroDto = self.splitData(dto)

        eegProc, eegInvalid = self.eegProcessor.process(eegDto)
        gyroProc, gyroInvalid = self.gyroProcessor.process(gyroDto)

        self.reuniteData(eegProc, gyroProc)
        return eegProc, (eegInvalid or gyroInvalid)

    def reuniteData(self, eegData, gyroData):
        pass#eegData.update(gyroData)

    def splitData(self, dto):
        '''split eeg and gyro data
        
        :param data: all values as dict
        
        :return: 
            eegData: eeg values as dict
            gyroData: gyro values as dict
        '''
        eegDto = self._getSplit(dto, self.eegFields)
        gyroDto = self._getSplit(dto, self.gyroFields)
        return eegDto, gyroDto

    def _getSplit(self, dto, fields):
        cpDto = dto.copy()
        cpDto.filter(fields)
        return cpDto