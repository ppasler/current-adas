'''
Created on 10.05.2016

@author: Paul Pasler
'''
import os
import pickle

from pybrain.structure.modules.tanhlayer import TanhLayer
from pybrain.supervised.trainers.backprop import BackpropTrainer
from pybrain.tools.shortcuts import buildNetwork


class NeuralNetwork(object):

    def __init__(self):
        self.path = os.path.dirname(os.path.abspath(__file__)) + "/../../data/"

    def createNew(self, nInputs, nHiddenLayers, nOutput, bias):
        self.net = buildNetwork(nInputs, nHiddenLayers, nOutput, bias=bias, hiddenclass=TanhLayer)

    def train(self, dataset, maxEpochs=10):
        self.trainer = BackpropTrainer(self.net, learningrate = 0.01, momentum = 0.99)
        return self.trainer.trainOnDataset(dataset, 1000)
    
    def test(self, data=None, verbose=False):
        return self.trainer.testOnData(data, verbose)

    def activate(self, value):
        return self.net.activate(value)
        
    def save(self, name):
        f = open(self.path + name, 'w')
        pickle.dump(self.net, f)
        f.close()
    
    def load(self, name):
        f = open(self.path + name, 'r')
        self.net = pickle.load(f)
        f.close()
        
    def __repr__(self):
        return "%s\n%s" % (self.__class__.__name__, str(self.net))