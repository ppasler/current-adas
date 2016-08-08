'''
Created on 10.05.2016

@author: Paul Pasler
'''
import sys, os
import unittest

from numpy import NaN, isnan, count_nonzero, copy
from numpy.testing.utils import assert_allclose

from config.config import ConfigProvider
from eeg_processor import EEGProcessor


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))



def sameEntries(list1, list2):
    if len(list1) != len(list2):
        return False

    return all([x in list1 for x in list2])

#TODO make this flexible to config values change
class TestSimpleChain(unittest.TestCase):

    def setUp(self):
        self.chain = EEGProcessor()
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
        data = [1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 4.0]
        qual = [15, 15,15, 15, 15, 15, 15]
        proc = self.chain.process(data, qual)
        assert_allclose(proc, [NaN, NaN, NaN, NaN, NaN, 0.5, 1.0])

    def test_process_replaceOutliners(self):
        data = [-5000, self.lowerBound-1, self.lowerBound, self.lowerBound+1, self.upperBound-1, self.upperBound, self.upperBound+1, 5000]
        qual = [15, 15, 15, 15, 15, 15, 15, 15]
        
        proc = self.chain.process(data, qual)
        self.assertEquals(count_nonzero(isnan(proc)), 4)

    def test_process_allTogether(self):
        data = [3.0, 1.0, 1.0, 1.0, 1.0, 1.0, self.lowerBound-1, self.upperBound+1, -8, -4.0, 2.0, 4.0]
        cp = copy(data[:])
        qual = [self.minQuality-1, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15]
        proc = self.chain.process(data, qual)
        #make sure we work on copies only
        assert_allclose(cp, data)
        assert_allclose(proc, [NaN, NaN, NaN, NaN, NaN, NaN, NaN, NaN, -1.0, -0.5, 0.25, 0.5])

if __name__ == "__main__":
    unittest.main()