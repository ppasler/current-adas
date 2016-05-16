'''
Created on 10.05.2016

@author: Paul Pasler
@see: https://github.com/thedanschmidt/PyBrain-Examples/blob/master/xor.py
'''
import os
import pickle

from pybrain.structure.modules.tanhlayer import TanhLayer
from pybrain.supervised.trainers.backprop import BackpropTrainer
from pybrain.tools.shortcuts import buildNetwork


class NeuralNetwork(object):
    '''Neural network wrapper for the pybrain implementation
    '''

    def __init__(self):
        self.path = os.path.dirname(os.path.abspath(__file__)) + "/../../data/"
        self.net = None
        self.trainer = None

    def createNew(self, nInputs, nHiddenLayers, nOutput, bias):
        '''builds a new neural network
        
        :param int nInputs: the number of input nodes
        :param int nHiddenLayers: the number of hidden layers
        :parma int nOutputs: the number of output nodes
        :param bool bias: if True an bias node will be added
        '''
        self.net = buildNetwork(nInputs, nHiddenLayers, nOutput, bias=bias, hiddenclass=TanhLayer)

    def train(self, dataset, maxEpochs = 10, learningrate = 0.01, momentum = 0.99):
        '''trains a network with the given dataset
        
        :param SupervisedDataSet dataset: the training dataset
        :param int maxEpochs: max number of iterations to train the network
        :parma float learningrate: helps to 
        :param float momentum: helps out of local minima while training, to get better results
        '''
        self.trainer = BackpropTrainer(self.net, learningrate = learningrate, momentum = momentum)
        return self.trainer.trainOnDataset(dataset, maxEpochs)
    
    def test(self, data=None, verbose=False):
        if not self.trainer:
            raise ValueError("call train() first, to create a valid trainer object") 
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