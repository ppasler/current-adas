'''
Created on 10.05.2016

@author: Paul Pasler
'''
import sys, os
import unittest

from numpy import NaN, array, arccos, cos
from numpy.testing.utils import assert_almost_equal, assert_allclose

from config.config import ConfigProvider
from statistic.simple_chain import SimpleChain


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))



def sameEntries(list1, list2):
    if len(list1) != len(list2):
        return False

    return all([x in list1 for x in list2])

class TestSimpleChain(unittest.TestCase):

    def setUp(self):
        self.chain = SimpleChain()
        config = ConfigProvider().getProcessingConfig()
        self.upperBound = config.get("upperBound")
        self.lowerBound = config.get("lowerBound")
        self.minQuality = config.get("minQual")

    def test_process_sunshine(self):
        data = [-2.0, -1.0, 0, 1.0, 2.0]
        qual = [15, 15, 15, 15, 15]
        proc = self.chain.process(data, qual)
        assert_allclose(proc, [-1.0, -0.5, 0, 0.5, 1])

    def test_process_badQuality(self):
        data = [-2.0, -1.0, 0, 1.0, 2.0]
        qual = [15, 0, self.minQuality-1, self.minQuality, self.minQuality+1]
        proc = self.chain.process(data, qual)
        assert_allclose(proc, [-1.0, NaN, NaN, 0.5, 1])

    def test_process_replaceSequences(self):
        data = [1.0, 1, 1, 2, 3]
        qual = [15, 15, 15, 15, 15]
        proc = self.chain.process(data, qual)
        assert_allclose(proc, [NaN, NaN, NaN, 2, 3])

    def test_process_replaceOutliners(self):
        data = [self.lowerBound-1, self.lowerBound, self.lowerBound+1, self.upperBound-1, self.upperBound, self.upperBound+1]
        qual = [15, 15, 15, 15, 15, 15]
        proc = self.chain.process(data, qual)
        assert_allclose(proc, [NaN, self.lowerBound, self.lowerBound+1, self.upperBound-1, self.upperBound, NaN])

if __name__ == "__main__":
    unittest.main()