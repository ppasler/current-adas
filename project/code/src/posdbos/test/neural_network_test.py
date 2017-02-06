#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 10.05.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

from base_test import * # @UnusedWildImport

from numpy.testing.utils import assert_array_equal
from pybrain.datasets.supervised import SupervisedDataSet

from posdbos.classificator.network_util import NetworkDataUtil, NetworkUtil
from posdbos.classificator.neural_network import NeuralNetwork


name = "zzz_test"


class TestNeuralNetwork(BaseTest):

    def setUp(self):
        self.nn = NeuralNetwork()
        self.config = {
            "learningrate": 0.01,
            "momentum": 0.1,
            "maxEpochs": 500,
            "continueEpochs": 15,
            "validationProportion": 0.25
        }
        self.nn.createNew(2, 4, 1, bias=True)

    def _createData(self, nInput, nTarget, values):
        ds = SupervisedDataSet(nInput, nTarget)
        for inp, target in values:
            ds.addSample(inp, target)
        
        return ds

    def createORData(self):
        values = [((0, 0), (0,)), ((0, 1), (1,)), ((1, 0), (1,)), ((1, 1), (1,))]*2
        return self._createData(2, 1, values)

    def createXORData(self):
        values = [((0, 0), (0,)), ((0, 1), (1,)), ((1, 0), (1,)), ((1, 1), (0,))]*2
        return self._createData(2, 1, values)

    def createANDData(self):
        values = [((0, 0), (0,)), ((0, 1), (0,)), ((1, 0), (0,)), ((1, 1), (1,))]*2
        return self._createData(2, 1, values)

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
            self.assertEqual(self.nn._clazz(self.nn.activate(inpt)), target)

    def test_saveAndLoad(self):
        ds = self.createORData()
        self.nn.train(ds)
        self.nn.save(name)

        nn2 = NeuralNetwork()
        nn2.load(name)

        self.assertNotEqual(self.nn, nn2)

        assert_array_equal(self.nn.net.params, nn2.net.params)
        for inpt, _ in ds:
            self.assertEqual(self.nn.activate(inpt), nn2.activate(inpt))

        self.removeFile(self.nn._createFilename(name))

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
    
        results, _ = self.nu.activate(ds)
    
        assert_array_equal(results, [[2, 0, 100], [0, 2, 100]])

class TestNetworkDataUtil(unittest.TestCase):

    def setUp(self):
        self.n = NetworkDataUtil()

    # TODO complete this
    def test_buildTestSet(self):
        classOne = np.array([[1., 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]])
        classTwo = np.array([[4., 5, 6], [4, 6, 5], [5, 4, 6], [5, 6, 4], [6, 4, 5], [6, 5, 4]])
        
        n = NetworkDataUtil()
        #logging.info(n.buildTestSet(classOne, classTwo))

if __name__ == "__main__":
    unittest.main()