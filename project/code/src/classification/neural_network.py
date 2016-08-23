'''
Created on 10.05.2016

@author: Paul Pasler
@see: https://github.com/thedanschmidt/PyBrain-Examples/blob/master/xor.py
'''
import os
import pickle

from pybrain.datasets.supervised import SupervisedDataSet
from pybrain.structure.modules.tanhlayer import TanhLayer
from pybrain.supervised.trainers.backprop import BackpropTrainer
from pybrain.tools.shortcuts import buildNetwork


FILE_EXTENSION = ".nn"

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
        
        :return: instance of a new neural network
        :rtype: NeuralNetwork
        '''
        self.net = buildNetwork(nInputs, nHiddenLayers, nOutput, bias=bias, hiddenclass=TanhLayer)
        return self

    def train(self, dataset, maxEpochs = 10, learningrate = 0.01, momentum = 0.99, continueEpochs=10, validationProportion=0.25):
        '''trains a network with the given dataset
        
        :param SupervisedDataSet dataset: the training dataset
        :param int maxEpochs: max number of iterations to train the network
        :parma float learningrate: helps to 
        :param float momentum: helps out of local minima while training, to get better results
        '''
        self.trainer = BackpropTrainer(self.net, learningrate = learningrate, momentum = momentum)
        self.trainer.trainUntilConvergence(dataset, maxEpochs, True, continueEpochs, validationProportion)
        #self.trainer.trainOnDataset(dataset, maxEpochs)

    def test(self, data=None, verbose=False):
        if not self.trainer:
            raise ValueError("call train() first, to create a valid trainer object") 
        return self.trainer.testOnData(data, verbose)

    def activate(self, value, rnd=False):
        inpt = self.net.activate(value)[0]
        if rnd:
            return self._clazz(inpt)
        return inpt

    def _clazz(self, inpt):
        clazz = round(inpt)
        if (clazz < 0):
            return 0
        if (clazz > 1):
            return 1
        return int(clazz)

    def save(self, name):
        '''saves the neural network
        
        :param string name: filename for the to be saved network
        '''
        f = open(self.path + name + FILE_EXTENSION, 'w')
        pickle.dump(self.net, f)
        f.close()

    def load(self, name):
        '''loades the neural network
        
        :param string name: filename for the to be loaded network
        
        :return: instance of a saved neural network
        :rtype: NeuralNetwork
        '''
        f = open(self.path + name + FILE_EXTENSION, 'r')
        self.net = pickle.load(f)
        f.close()
        return self

    def __repr__(self):
        return "%s\n%s" % (self.__class__.__name__, str(self.net))

if __name__ == "__main__": # pragma: no cover
    def _createData(nInput, nTarget, values):
        ds = SupervisedDataSet(nInput, nTarget)
        for inp, target in values:
            ds.addSample(inp, target)
        
        return ds

    def createXORData():
        values = [((0, 0), (0,)), ((0, 1), (1,)), ((1, 0), (1,)), ((1, 1), (0,))]
        return _createData(2, 1, values)

    ds = createXORData()
    nn = NeuralNetwork()
    nn.createNew(2, 4, 1, bias=True)
    nn.train(ds, 5000, 0.01, 0.99)
    
    for inpt, target in ds:
        print "input %s: is %s; should be %s" % (inpt, nn.activate(inpt), target)
    
    nn.save("XOR_test")
