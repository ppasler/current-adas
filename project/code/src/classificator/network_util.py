#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 16.08.2016

:author: Paul Pasler
:organization: Reutlingen University
'''
from datetime import datetime
import os, sys
import time

from pybrain.datasets.supervised import SupervisedDataSet
from util.file_util import FileUtil

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from classificator.neural_network import NeuralNetwork
from config.config import ConfigProvider
import numpy as np


N_OUTPUT = 1

class NetworkUtil(object):
    '''
    Class to train and test a neural network 
    '''

    def __init__(self, nInputs=None, nHiddenLayers=None, bias=True, new=True, fileName=""):
        self.params = {}
        self.config = ConfigProvider().getNNTrainConfig()
        if new:
            self.params["nInputs"] = nInputs
            self.params["nHiddenLayers"] = nHiddenLayers
            self.params["bias"] = bias
            self.nn = NeuralNetwork().createNew(nInputs, nHiddenLayers, N_OUTPUT, bias)
        else:
            self.nn = NeuralNetwork().load(fileName)

    def train(self, trainData, convergence=False):
        start = time.time()
        print "start Training at " + str(datetime.fromtimestamp(start))
        if convergence:
            self.nn.trainConvergence(trainData, **self.config)
        else:
            self.nn.train(trainData, **self.config)
        print "Training Done in %.2fs" % (time.time() - start)
    
    def test(self, testData=None):
        self.nn.test(testData)
        print "Testing Done"

    def activate(self, testData):
        total = (len(testData) / 2) / 100.0
        matrix = np.array([[0, 0, 0], [0, 0, 0]])
        resArr = []
        for inpt, target in testData:
            res = self.nn.activate(inpt)
            clazz = self.nn._clazz(res)
            resArr.append([res, clazz, target])
            matrix[int(target[0])][clazz] += 1
        matrix[0, 2] = matrix[0, 0] / total
        matrix[1, 2] = matrix[1, 1] / total 
        return matrix, np.array(resArr)

    def save(self, name):
        self.nn.save(name)

    def __str__(self):
        self.params.update(self.config)
        return str(self.nn) + "\n" + str(self.params)

class NetworkDataUtil(object):
    '''
    Class to load and separate data for a neural network 
    '''

    def __init__(self, files=[]):
        self.files = files
        self.fileUtil = FileUtil()

    def get(self, separate=True):
        values0, values1 = self.readFiles(self.files)
        if separate:
            return self.buildTestSet(values0, values1)
        else:
            return self.buildFullTestSet(values0, values1)

    def getNInput(self):
        return self.nInputs

    def readFiles(self, files):
        return self.fileUtil.getDto(files[0]), self.fileUtil.getDto(files[1])

    def buildFullTestSet(self, values0, values1):
        values0 = self._addClass(values0, 0.)
        values1 = self._addClass(values1, 1.)
        rawData = self._postprocData(values0, values1)
        self.nInputs = len(rawData[0])-1

        return self.createData(self.nInputs, rawData)

    def buildTestSet(self, values0, values1):
        train0, test0 = self._preprocData(values0, 0.)
        train1, test1 = self._preprocData(values1, 1.)

        trainRawData = self._postprocData(train0, train1)
        testRawData = self._postprocData(test0, test1)
        self.nInputs = len(trainRawData[0])-1

        trainData = self.createData(self.nInputs, trainRawData)
        testData = self.createData(self.nInputs, testRawData)
        return trainData, testData

    def _preprocData(self, values, clazz):
        np.random.shuffle(values)
        values0 = self._addClass(values, clazz)
        return self._separateData(values0) 

    def _addClass(self, values, clazz):
        shape = values.shape
        clazzArray = np.full((shape[0], shape[1]+1), clazz)
        clazzArray[:,:-1] = values
        return clazzArray

    def _separateData(self, values):
        l = len(values)
        d = (2 * l / 3)
        return values[0:d], values[d:]

    def _postprocData(self, values0, values1):
        values = np.concatenate((values0, values1), axis=0)
        np.random.shuffle(values)
        return values

    def createXORData(self):
        values = [[0, 0, 0], [0, 1, 1], [1, 0, 1], [1, 1, 0]]
        return self.createData(2, values)

    def createData(self, nInput, values):
        ds = SupervisedDataSet(nInput, N_OUTPUT)
        for value in values:
            ds.addSample(value[:nInput], value[nInput])
        return ds