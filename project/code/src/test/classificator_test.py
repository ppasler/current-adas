'''
Created on 10.05.2016

@author: Paul Pasler
'''
import sys, os
import time
import unittest

from pybrain.datasets.supervised import SupervisedDataSet

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from classification.neural_network import NeuralNetwork




name = time.strftime("%Y-%M-%d-%H-%M", time.gmtime()) + "_test"

def sameEntries(list1, list2):
    if len(list1) != len(list2):
        return False

    return all([x in list1 for x in list2])

class TestNeuralNetwork(unittest.TestCase):


    def setUp(self):
        self.nn = NeuralNetwork()
        self.nn.createNew(2, 4, 1, bias=True)

    def createXORData(self):
        ds = SupervisedDataSet(2, 1)
        ds.addSample((0, 0), (0,))
        ds.addSample((0, 1), (1,))
        ds.addSample((1, 0), (1,))
        ds.addSample((1, 1), (0,))
        return ds

    def createANDData(self):
        ds = SupervisedDataSet(2, 1)
        ds.addSample((0, 0), (0,))
        ds.addSample((0, 1), (0,))
        ds.addSample((1, 0), (0,))
        ds.addSample((1, 1), (1,))
        return ds

    def test_xor(self):
        ds = self.createXORData()

        self.nn.train(ds)

        #TODO may fail with delta 0.2
        for inpt, target in ds:
            self.assertAlmostEqual(self.nn.activate(inpt), target, delta=0.2)

    def test_and(self):
        ds = self.createANDData()

        self.nn.train(ds)

        #TODO may fail with delta 0.2
        for inpt, target in ds:
            self.assertAlmostEqual(self.nn.activate(inpt), target, delta=0.2)

    def test_saveAndLoad(self):
        self.nn.save(name)
        
        nn2 = NeuralNetwork()
        nn2.load(name)
        
        #TODO check for equality
        self.assertTrue(sameEntries(self.nn.net.params, nn2.net.params))
        
        #TODO remove file
        self.removeFile()

    def removeFile(self):
        try:
            os.remove(name)
        except OSError as e:
            print e.message


if __name__ == "__main__":
    unittest.main()