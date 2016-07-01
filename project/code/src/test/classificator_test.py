'''
Created on 10.05.2016

@author: Paul Pasler
'''
import sys, os
import unittest

from pybrain.datasets.supervised import SupervisedDataSet
from config.config import ConfigProvider

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from classification.neural_network import NeuralNetwork




name = "zzz_test"

def sameEntries(list1, list2):
    if len(list1) != len(list2):
        return False

    return all([x in list1 for x in list2])

class TestNeuralNetwork(unittest.TestCase):


    def setUp(self):
        self.nn = NeuralNetwork()
        self.config = ConfigProvider().getNeuralNetworkConfig()
        self.nn.createNew(2, 4, 1, bias=True)

    def _createData(self, nInput, nTarget, values):
        ds = SupervisedDataSet(nInput, nTarget)
        for inp, target in values:
            ds.addSample(inp, target)
        
        return ds

    def createORData(self):
        values = [((0, 0), (0,)), ((0, 1), (1,)), ((1, 0), (1,)), ((1, 1), (1,))]
        return self._createData(2, 1, values)

    def createXORData(self):
        values = [((0, 0), (0,)), ((0, 1), (1,)), ((1, 0), (1,)), ((1, 1), (0,))]
        return self._createData(2, 1, values)

    def createANDData(self):
        values = [((0, 0), (0,)), ((0, 1), (0,)), ((1, 0), (0,)), ((1, 1), (1,))]
        return self._createData(2, 1, values)

    def removeFile(self):
        try:
            os.remove(self.nn.path + name + ".nn")
        except OSError as e:
            print e.message

    def test_xor(self):
        ds = self.createXORData()

        self.nn.train(ds, self.config["maxEpochs"], self.config["learningrate"], self.config["momentum"])

        #TODO may fail with delta 0.2
        for inpt, target in ds:
            self.assertAlmostEqual(self.nn.activate(inpt), target, delta=0.2)

    def test_and(self):
        ds = self.createANDData()
        self.nn.train(ds, self.config["maxEpochs"], self.config["learningrate"], self.config["momentum"])

        #TODO may fail with delta 0.2
        for inpt, target in ds:
            self.assertAlmostEqual(self.nn.activate(inpt), target, delta=0.2)

    def test_saveAndLoad(self):
        ds = self.createORData()
        self.nn.train(ds)
        self.nn.save(name)
        
        nn2 = NeuralNetwork()
        nn2.load(name)
        
        self.assertNotEqual(self.nn, nn2)
        
        self.assertTrue(sameEntries(self.nn.net.params, nn2.net.params))
        for inpt, _ in ds:
            self.assertEqual(self.nn.activate(inpt), nn2.activate(inpt))

        self.removeFile()

    def test_test(self):
        ds = self.createORData()
        self.nn.train(ds)
        self.nn.test(ds, False)

    def test_testBeforeTrain(self):
        with self.assertRaises(ValueError):
            self.nn.test(None, False)

if __name__ == "__main__":
    unittest.main()