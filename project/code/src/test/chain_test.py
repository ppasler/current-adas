'''
Created on 10.05.2016

@author: Paul Pasler
'''
import sys, os
import unittest

from numpy import NaN, isnan, count_nonzero, array
from numpy.testing.utils import assert_allclose

from config.config import ConfigProvider
from eeg_processor import SignalProcessor
from util.quality_util import QualityUtil


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))



def sameEntries(list1, list2):
    if len(list1) != len(list2):
        return False

    return all([x in list1 for x in list2])

#TODO make this flexible to config values change
class TestSimpleChain(unittest.TestCase):

    def setUp(self):
        self.chain = SignalProcessor()
        self.qualUtil = QualityUtil()
        config = ConfigProvider().getProcessingConfig()
        self.upperBound = config.get("upperBound")
        self.lowerBound = config.get("lowerBound")
        self.minQuality = config.get("minQual")
        self.maxNaNValues = config.get("maxNaNValues")

    def _checkValidData(self, data, invalid):
        self.assertEqual(invalid, self.maxNaNValues < count_nonzero(isnan(data)))

    def test_process_sunshine(self):
        data = [self.lowerBound, self.lowerBound / 2.0, 0, self.upperBound / 2.0, self.upperBound]
        qual = [15, 15, 15, 15, 15]

        proc, invalidData = self.chain.process(data, qual)
        self._checkValidData(proc, invalidData)
        assert_allclose(proc, [-1.0, -0.5, 0, 0.5, 1])

    @unittest.skip("unused")
    def test_process_badQuality(self):
        data = [-2.0, -1.0, 0, 1.0, 2.0]
        qual = [15, 0, self.minQuality-1, self.minQuality, self.minQuality+1]

        proc, invalidData = self.chain.process(data, qual)
        self._checkValidData(proc, invalidData)
        assert_allclose(proc, [-1.0, NaN, NaN, 0.5, 1])

    @unittest.skip("unused")
    def test_process_replaceSequences(self):
        data = [1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 4.0]
        qual = [15, 15,15, 15, 15, 15, 15]

        proc, invalidData = self.chain.process(data, qual)
        self._checkValidData(proc, invalidData)
        assert_allclose(proc, [NaN, NaN, NaN, NaN, NaN, 0.5, 1.0])

    def test_process_replaceOutliners(self):
        data = [-5000, self.lowerBound-1, self.lowerBound, self.lowerBound+1, self.upperBound-1, self.upperBound, self.upperBound+1, 5000]
        qual = [15, 15, 15, 15, 15, 15, 15, 15]

        proc, invalidData = self.chain.process(data, qual)
        self._checkValidData(proc, invalidData)
        self.assertEquals(count_nonzero(proc), 4)

    def test_checkValid(self):
        maxNaNValues = self.maxNaNValues
        for length in range(0, maxNaNValues+1):
            data = self._getNaNList(length)
            qual = [15]*length
            _, invalidData = self.chain.process(data, qual)
            self.assertFalse(invalidData, "length %d" % length)
        
        for length in range(maxNaNValues+1, maxNaNValues+5):
            data = self._getNaNList(length)
            qual = [15]*length
            _, invalidData = self.chain.process(data, qual)
            self.assertTrue(invalidData, "length %d" % length)

    def _getNaNList(self, length):
        return array([NaN]*length)


if __name__ == "__main__":
    unittest.main()