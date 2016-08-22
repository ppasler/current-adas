#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 16.08.2016

:author: Paul Pasler
:organization: Reutlingen University
'''
from datetime import datetime
import multiprocessing
import os, sys
import time

from pybrain.datasets.supervised import SupervisedDataSet

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from classification.neural_network import NeuralNetwork
from config.config import ConfigProvider
import numpy as np
from util.eeg_table_util import EEGTableFileUtil


N_OUTPUT = 1
scriptPath = os.path.dirname(os.path.abspath(__file__))

class NetworkUtil(object):
    '''
    Class to train and test a neural network 
    '''

    def __init__(self, nInputs, nHiddenLayers, bias=True, new=True):
        self.params = {}
        self.params["nInputs"] = nInputs
        self.params["nHiddenLayers"] = nHiddenLayers
        self.params["bias"] = bias

        if new:
            self.nn = NeuralNetwork().createNew(nInputs, nHiddenLayers, N_OUTPUT, bias)

    def train(self, trainData):
        start = time.time()
        print "start Training at " + str(datetime.fromtimestamp(start))
        self.config = ConfigProvider().getNNTrainConfig()
        self.nn.train(trainData, **self.config)
        print "Training Done in %.2fs" % (time.time() - start)
    
    def test(self, testData=None):
        self.nn.test(testData)
        print "Testing Done"

    def _clazz(self, inpt):
        clazz = round(inpt)
        if (clazz < 0):
            return 0
        if (clazz > 1):
            return 1
        return clazz

    def activate(self, testData):
        total = (len(testData) / 2) / 100.0
        matrix = np.array([[0, 0, 0], [0, 0, 0]])
        resArr = []
        for inpt, target in testData:
            res = self.nn.activate(inpt)
            clazz = self._clazz(res[0])
            resArr.append([res, clazz, target])
            matrix[target[0]][clazz] += 1
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
        self.fileUtil = EEGTableFileUtil()

    def get(self):
        values0, values1 = self.readFiles(self.files)
        return self.buildTestSet(values0, values1)

    def getNInput(self):
        return self.nInputs

    def readFiles(self, files):
        return self.fileUtil.readData(files[0]), self.fileUtil.readData(files[1])

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

    def _separateData(self, values):
        l = len(values)
        d = (2 * l / 3)
        return values[0:d], values[d:]

    def _addClass(self, values, clazz):
        shape = values.shape
        clazzArray = np.full((shape[0], shape[1]+1), clazz)
        clazzArray[:,:-1] = values
        return clazzArray

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

def testSeveral(start, end, name):
    threads = []
    for h in range(start, end):
        threads.append(multiprocessing.Process(target=testSingle, args=(h,name)))

    for thread in threads:
        thread.start()

    for thread in threads:
        thread.join()

    print "Done"

def testSingle(h, name):
    files = [scriptPath + "/../../data/awake_full.csv", scriptPath + "/../../data/drowsy_full.csv"]
    ndu = NetworkDataUtil(files)
    train, test = ndu.get()

    nu = NetworkUtil(ndu.getNInput(), 4)
    nu.train(train)
    nu.test()
    filename = name + "_" + str(h)
    nu.save(filename)
    f = open(os.path.dirname(os.path.abspath(__file__)) + "/../../data/" + filename +  ".nns", 'w')

    results, resArr = nu.activate(test)
    f.write(nu.__str__() + "\n\n")
    f.write("  awk drsy res(%)\n")
    f.write(str(results))
    f.write("\n\nres;clazz;target\n")
    for line in resArr:
        f.write("%.2f;%.2f;%.2f\n" % tuple(line))
    f.close()

if __name__ == "__main__": # pragma: no cover
    name = time.strftime("%Y-%m-%d-%H-%M", time.gmtime())
    testSeveral(2, 6, name)
