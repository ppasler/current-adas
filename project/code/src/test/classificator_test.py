'''
Created on 10.05.2016

@author: Paul Pasler
'''
import sys, os
import unittest

from numpy import array
from pybrain.datasets.supervised import SupervisedDataSet

from classification.network_util import NetworkDataUtil, NetworkUtil
from classification.neural_network import NeuralNetwork
from config.config import ConfigProvider
from numpy.testing.utils import assert_array_equal


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))




name = "zzz_test"

def sameEntries(list1, list2):
    if len(list1) != len(list2):
        return False

    return all([x in list1 for x in list2])

class TestNeuralNetwork(unittest.TestCase):

    def setUp(self):
        self.nn = NeuralNetwork()
        self.config = ConfigProvider().getNNTrainConfig()
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

        self.nn.train(ds, **self.config)

        #TODO may fail with delta 0.2
        for inpt, target in ds:
            self.assertAlmostEqual(self.nn.activate(inpt), target, delta=0.2)

    def test_and(self):
        ds = self.createANDData()
        self.nn.train(ds, **self.config)

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

class TestNetworkUtil(unittest.TestCase):

    def setUp(self):
        self.nu = NetworkUtil(2, 4)

    def _buildXORData(self):
        ndu = NetworkDataUtil()
        return ndu.createXORData()

    def test_XOR(self):
        ds = self._buildXORData()
        self.nu.train(ds)
    
        results = self.nu.activate(ds)
    
        assert_array_equal(results, [[2, 0], [0, 2]])

class TestNetworkDataUtil(unittest.TestCase):

    def setUp(self):
        self.n = NetworkDataUtil()

    def test_buildTestSet(self):
        classOne = array([[1., 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]])
        classTwo = array([[4., 5, 6], [4, 6, 5], [5, 4, 6], [5, 6, 4], [6, 4, 5], [6, 5, 4]])
        
        n = NetworkDataUtil()
        print n.buildTestSet(classOne, classTwo)

if __name__ == "__main__":
    unittest.main()