#!/usr/bin/python

import os.path
import sys
import unittest

from pylab import ceil
from scipy.io import wavfile
from scipy.signal.filter_design import freqz

import numpy as np
from util.eeg_table_to_packet_converter import EEGTableToPacketUtil
from util.eeg_table_util import EEGTableFileUtil, EEGTableUtil
from util.eeg_util import EEGUtil
from util.fft_util import FFTUtil
from util.quality_util import QualityUtil
from util.signal_util import SignalUtil


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

PATH = os.path.dirname(os.path.abspath(__file__)) +  "/../../examples/"


TEST_DATA_12000Hz = np.array([     0,  32451,  -8988, -29964,  17284,  25176, -24258, -18459,
        29368,  10325, -32229,  -1401,  32616,  -7633, -30503,  16079,
        26049, -23294, -19599,  28721,  11644, -31946,  -2798,  32720,
        -6264, -30987,  14844,  26874, -22288, -20703,  28020,  12942,
       -31606,  -4191,  32765,  -4884, -31414,  13583,  27651, -21241,
       -21770,  27269,  14217, -31207,  -5576,  32750,  -3495, -31783,
        12296,  28377, -20156, -22796,  26468,  15465, -30752,  -6950,
        32675,  -2100, -32095,  10987,  29051, -19033, -23781,  25618,
        16686, -30240,  -8312,  32541,   -701, -32348,   9658,  29672,
       -17876, -24723,  24722,  17875, -29673,  -9659,  32347,    700,
       -32542,   8311,  30239, -16687, -25619,  23780,  19032, -29052,
       -10988,  32094,   2099, -32676,   6949,  30751, -15466, -26469,
        22795,  20155, -28378, -12297,  31782,   3494, -32751,   5575,
        31206, -14218, -27270,  21769,  21240, -27652, -13584,  31413,
         4883, -32766,   4190,  31605, -12943, -28021,  20702,  22287,
       -26875, -14845,  30986,   6263, -32721,   2797,  31945, -11645])

def sameEntries(list1, list2):
    if len(list1) != len(list2):
        return False

    return all([x in list1 for x in list2])

def countOcc(a, x):
    return len(np.where(a==x)[0])

def removeFile(filePath):
    try:
        os.remove(filePath)
    except OSError as e:
        print e.message

class TestQualityUtil(unittest.TestCase):

    def setUp(self):
        self.util = QualityUtil()

    def test_replaceOutliners_withValue(self):
        value = -99
        testList = np.array([-10, -4, -3, -2, 0, 4, 5, 6, 10])
        self.assertEqual(countOcc(testList, value), 0)
        self.util.replaceOutliners(testList, -3, 5, value)
        self.assertEqual(countOcc(testList, value), 4)

    def test_replaceOutliners_withoutValue(self):
        testList = np.array([-10, -4, -3, -2, 0, 4, 5, 6, 10])
        self.assertEqual(countOcc(testList, -3), 1)
        self.assertEqual(countOcc(testList, 5), 1)
        
        self.util.replaceOutliners(testList, -3, 5)

        self.assertEqual(countOcc(testList, -3), 3)
        self.assertEqual(countOcc(testList, 5), 3)

    def test_replaceBadQuality(self):
        value = 99
        testList = np.array([-10, -4, -3, -2, 0, 2, 4, 5, 6, 10])
        qualList = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9])
        
        self.util.replaceBadQuality(testList, qualList, 4, value)
        self.assertEqual(len(qualList), len(testList))
        self.assertEqual(countOcc(testList, value), 4)

class TestSignalUtil(unittest.TestCase):

    def setUp(self):
        self.util = SignalUtil()

    def test_normalize(self):
        testList = np.array([0, -5, 1, 10])
        normList = self.util.normalize(testList)
        self.assertEqual(len(testList), len(normList))
        self.assertTrue(max(normList) <= 1)
        self.assertTrue(min(normList) >= -1)

    def test_normalize_zero(self):
        testList = np.array([0, 0, 0, 0])
        normList = self.util.normalize(testList)
        self.assertEqual(len(testList), len(normList))
        self.assertTrue(max(normList) <= 1)
        self.assertTrue(min(normList) >= -1)
        self.assertTrue(sameEntries(testList, normList))

    def test_energie(self):
        testList = np.array([1, 2, 3, 4])
        energy = self.util.energy(testList)
        self.assertEqual(energy, 30)

    def test_maximum(self):
        testList = np.array([-5, 1, 2, 3, 4])
        maximum = self.util.maximum(testList)
        self.assertEqual(maximum, 4)

    def test_minimum(self):
        testList = np.array([-5, 1, 2, 3, 6])
        minimum = self.util.minimum(testList)
        self.assertEqual(minimum, -5)

    def test_mean(self):
        testList = np.array([0, 1, 2, 3, 4])
        mean = self.util.mean(testList)
        self.assertEqual(mean, 2)

class TestFrequencyFilter(unittest.TestCase):
    
    def setUp(self):
        self.util = SignalUtil()
        self._setSignalParams()
        
    def _setSignalParams(self, offset=0, length=-1):
        self.samplingRate, self.data= self._readSoundFile(offset=offset, length=length)
        self.n = len(self.data)
        self.nUniquePts = ceil((self.n+1)/2.0)
        
        self.freqArray = np.arange(0, self.nUniquePts, 1.0) * (self.samplingRate / self.n)
    
    def test_butterBandpass(self):
        samplingRate = 32
        i = samplingRate / 4
        b, a = self.util.butterBandpass(i-1, i+1, samplingRate)
        _, h = freqz(b, a, worN=samplingRate*4)
        h = abs(h)
        self.assertEqual(np.argmax(h), len(h)/2)
        self.assertAlmostEqual(max(h), 1, delta=0.1)
        self.assertAlmostEqual(h[0], 0, delta=0.01)
        self.assertAlmostEqual(h[len(h)-1], 0, delta=0.01)


    def test_butterBandpass_egde(self):
        # no signal allowed
        b, a = self.util.butterBandpass(5, 5, 16)
        _, h = freqz(b, a, worN=32)
        self.assertEquals(np.count_nonzero(abs(h)), 0)
        
        # everything gets through (except 0)
        b, a = self.util.butterBandpass(0, 8, 16)
        _, h = freqz(b, a, worN=16)
        self.assertAlmostEqual(sum(abs(h)), len(h)-1, delta = 1)
        
        b, a = self.util.butterBandpass(0.5, 8, 16)
        _, h = freqz(b, a, worN=16)
        self.assertAlmostEqual(sum(abs(h)), len(h)-1, delta = 1)


    @unittest.skip("demonstrating skipping")
    def test_butterBandpass_error(self):
        self.util.butterBandpass(0, 4, 8)

        with self.assertRaises(ValueError):
            _ = self.util.butterBandpass(2, 4, 4)
        with self.assertRaises(ValueError):
            _ = self.util.butterBandpass(2, 4, 7)

        with self.assertRaises(ValueError):
            _ = self.util.butterBandpass(-1, 4, 8)

    def test_butterBandpassFilter(self):
        x = [1, -1, 1, -1]
        _ = self.util.butterBandpassFilter(x, 1, 2, 10)
    
    def _readSoundFile(self, fileName='12000hz.wav', offset=0, length=-1):
        samplingRate, data = wavfile.read(PATH + fileName)
        if len(data.shape) == 2:
            data = data[:,0]
        
        if(length > -1):
            data = data[offset:offset+length]
        
        data = self.util.normalize(data)
        return samplingRate, data

    def _getMaxFrequency(self, data, freqArray):
        fft = FFTUtil().fft(data)
        return freqArray[np.argmax(fft)]

    def test_butterBandpassFilter_original(self):
        freqMax = self._getMaxFrequency(self.data, self.freqArray)
        self.assertAlmostEqual(freqMax, 12000.0, delta= 1000)

    def test_butterBandpassFilter_filterNoCut(self):
        cut = self.util.butterBandpassFilter(self.data, 1000, self.samplingRate/2-1000, self.samplingRate)
        freqMax = self._getMaxFrequency(cut, self.freqArray)
        self.assertAlmostEqual(freqMax, 12000.0, delta= 1000)

    def test_butterBandpassFilter_filterAroundMax(self):
        cut = self.util.butterBandpassFilter(self.data, 11000, 13000, self.samplingRate)
        freqMax = self._getMaxFrequency(cut, self.freqArray)
        self.assertAlmostEqual(freqMax, 12000.0, delta= 1000)
    
    def test_butterBandpassFilter_filterAboveMax(self):
        cut = self.util.butterBandpassFilter(self.data, 0, 2000, self.samplingRate)
        freqMax = self._getMaxFrequency(cut, self.freqArray)
        self.assertNotEqual(freqMax, 12000.0)
        self.assertAlmostEqual(freqMax, 1000.0, delta= 1000)
        
    def test_butterBandpassFilter_filterBeyondMax(self):
        cut = self.util.butterBandpassFilter(self.data, self.samplingRate/2-2000, self.samplingRate/2, self.samplingRate)
        freqMax = self._getMaxFrequency(cut, self.freqArray)
        self.assertNotEqual(freqMax, 12000.0)
        self.assertAlmostEqual(freqMax, self.samplingRate/2-1000, delta= 1000)

    def test_butterBandpassFilter_short(self):
        self._setSignalParams(length=4)
        freqMax = self._getMaxFrequency(self.data, self.freqArray)
        self.assertAlmostEqual(freqMax, 12000.0, delta= 1000)
        
        cut = self.util.butterBandpassFilter(self.data, 1000, self.samplingRate/2-1000, self.samplingRate)
        freqMax = self._getMaxFrequency(cut, self.freqArray)
        self.assertAlmostEqual(freqMax, 12000.0, delta= 1000)

    def test_butterBandpassFilter_originalAndShort(self):
        cutOrig = self.util.butterBandpassFilter(self.data, 1000, self.samplingRate/2-1000, self.samplingRate)
        freqMaxOrig = self._getMaxFrequency(self.data, self.freqArray)
        
        self._setSignalParams(length=4)
        cutShort = self.util.butterBandpassFilter(self.data, 1000, self.samplingRate/2-1000, self.samplingRate)
        freqMaxShort = self._getMaxFrequency(self.data, self.freqArray)
        
        self.assertAlmostEqual(freqMaxShort, freqMaxOrig, delta=1000)
        
        for i in range(len(cutShort)):
            self.assertAlmostEqual(cutOrig[i], cutShort[i], delta=0.02)

class TestFFTUtil(unittest.TestCase):

    def setUp(self):
        self.util = FFTUtil()

    def test__removeMirrored(self):
        testList1 = np.array([0, 1, 2, 3, 4, 4, 3, 2, 1])
        mirrList = self.util._removeMirrored(testList1, len(testList1))
        self.assertEqual(len(mirrList), 5)

        testList2 = np.array([0, 1, 2, 3, 4, 3, 2, 1, 0])
        mirrList = self.util._removeMirrored(testList2, len(testList2))
        self.assertEqual(len(mirrList), 5)

    def test__process(self):
        testList = np.array([1, 2, -3, -4])
        procList = self.util._process(testList, len(testList))
        self.assertEqual(len(testList), len(procList))
        # absolute;     normalize 0,1;          **2
        # [1, 2, 3, 4]; [0.25, 0.5, 0.75, 1];   [0.0625, 0.25, 0.5625, 1] 
        self.assertTrue(sameEntries(procList, [0.0625, 0.25, 0.5625, 1]))
                            
    def test__doubleValues(self):
        # odd: first entry is not doubled
        testOddList = np.array([17, 3, 4, 5, 6])
        doubOddList = self.util._doubleValues(np.copy(testOddList))
        self.assertEqual(len(doubOddList), len(testOddList))
        self.assertTrue(all([x*2 in doubOddList for i, x in enumerate(testOddList) if 0 < i]))
            
        # even: first and last entry is not doubled
        testEvenList = np.array([17, 3, 4, 5, 6, 17])
        doubEvenList = self.util._doubleValues(np.copy(testEvenList))
        self.assertEqual(len(doubEvenList), len(testEvenList))
        self.assertTrue(all([x*2 in doubEvenList for i, x in enumerate(testEvenList) if 0 < i < len(testEvenList)-1]))

    def testFft(self):
        # 128 pts from a 12.000Hz tone with a sample rate of 44.100
        data = TEST_DATA_12000Hz
        samplingRate = 44100

        fft = self.util.fft(data)

        n = float(len(data))
        nUniquePts = np.ceil((n+1)/2.0)
        
        maxIndex = np.argmax(fft)

        # calc frequency array
        freqArray = np.arange(0, nUniquePts, 1.0) * (samplingRate / n);

        # should be around 12000
        self.assertTrue(11800 < freqArray[maxIndex] < 12200)
        

class TestEEGUtil(unittest.TestCase):

    def setUp(self):
        self.util = EEGUtil()

    def test__getSliceParams(self):
        for _, freqRange in self.util.channel_ranges.iteritems():
            self.assertEqual(type(self.util._getSliceParam(freqRange)[0]), int)

    def test_getChannels_short(self):
        data = [1, 2, 3, 4, 5, 6, 7, 8]

        channels = self.util.getChannels(data)
        self.assertTrue(len(channels) == 5)
        self.assertTrue(len(channels["delta"]) > 0)
        self.assertTrue(len(channels["theta"]) > 0)
        
        self.assertTrue(len(channels["alpha"]) == 0)

    def test_getChannels(self):
        fft = TEST_DATA_12000Hz

        channels = self.util.getChannels(fft)
        flattenChannels = np.hstack(channels.values())
        self.assertTrue(all([x in fft for x in flattenChannels]))
        
        self.assertTrue(len(flattenChannels) <= len(fft))

    def test_getSingleChannels(self):
        fft = TEST_DATA_12000Hz
        channels = self.util.getChannels(fft)

        delta = self.util.getDeltaChannel(fft)
        # TODO delta range from 0.5 to 4Hz, actual range from 1 - 4Hz
        self.assertEqual(len(delta), 3)
        self.assertTrue(all([x in channels["delta"] for x in delta]))
               
        theta = self.util.getThetaChannel(fft)
        self.assertEqual(len(theta), 4)
        self.assertTrue(all([x in channels["theta"] for x in theta]))
                
        alpha = self.util.getAlphaChannel(fft)
        self.assertEqual(len(alpha), 5)
        self.assertTrue(all([x in channels["alpha"] for x in alpha]))
                
        beta = self.util.getBetaChannel(fft)
        self.assertEqual(len(beta), 17)
        self.assertTrue(all([x in channels["beta"] for x in beta]))
          
        gamma = self.util.getGammaChannel(fft)
        self.assertEqual(len(gamma), len(range(*self.util.channel_ranges["gamma"])))
        self.assertTrue(all([x in channels["gamma"] for x in gamma]))

    def test_getWaves(self):
        eeg_data = EEGTableFileUtil().readFile(PATH + "example_32.csv")
        eeg = eeg_data.getColumn("F3")
        nEeg = len(eeg)
        waves = self.util.getWaves(eeg, eeg_data.getSamplingRate())
        
        self.assertEqual(len(waves), 5)
        for _, wave in waves.iteritems():
            self.assertEqual(len(wave), nEeg)

    def test_getSingleWaves(self):
        eeg_data = EEGTableFileUtil().readFile(PATH + "example_32.csv")
        eeg = eeg_data.getColumn("F3")
        nEeg = len(eeg)
        samplingRate = eeg_data.getSamplingRate()
        waves = self.util.getWaves(eeg, samplingRate)

        delta = self.util.getDeltaWaves(eeg, samplingRate)
        self.assertEqual(len(delta), nEeg)
        self.assertTrue(all([x in waves["delta"] for x in delta]))

        theta = self.util.getThetaWaves(eeg, samplingRate)
        self.assertEqual(len(theta), nEeg)
        self.assertTrue(all([x in waves["theta"] for x in theta]))

        alpha = self.util.getAlphaWaves(eeg, samplingRate)
        self.assertEqual(len(alpha), nEeg)
        self.assertTrue(all([x in waves["alpha"] for x in alpha]))

        beta = self.util.getBetaWaves(eeg, samplingRate)
        self.assertEqual(len(beta), nEeg)
        self.assertTrue(all([x in waves["alpha"] for x in alpha]))
          
        gamma = self.util.getGammaWaves(eeg, samplingRate)
        self.assertEqual(len(gamma), nEeg)
        self.assertTrue(all([x in waves["gamma"] for x in gamma]))

class TestEEGTableReader(unittest.TestCase):

    def setUp(self):
        self.reader = EEGTableFileUtil()

    def test_readData(self):
        file_path = PATH + "example_32.csv"
        if os.path.isfile(file_path):
            self.reader.readData(file_path)
        else:
            print "'%s' not found" % file_path

    def test_readHeader(self):
        file_path = PATH + "example_32.csv"
        if os.path.isfile(file_path):
            self.reader.readHeader(file_path)
        else:
            print "'%s' not found" % file_path

    def test_readFile(self):
        file_path = PATH + "example_32.csv"
        if os.path.isfile(file_path):
            self.reader.readFile(file_path)
        else:
            print "'%s' not found" % file_path

    def test_writeFile(self):
        filePath = PATH + "test.csv"
        header= ["A", "B", "C"]
        data = np.array([[1.123456789, 2, 3], [-4.123456789, 5, 6], [7.123456789, 8, 99.123]])
        self.reader.writeFile(filePath, data, header)
        
        if os.path.isfile(filePath):
            read = self.reader.readFile(filePath)

            for i in range(len(data)):
                for j in range(len(data[i])):
                    self.assertAlmostEqual(data[i, j], read.data[i, j], delta= 0.001)

        removeFile(filePath)

    def test_writeStructredFile(self):
        filePath = PATH + "test_structured.csv"
        data = {
            "A": {
                "value": [1, 2, 3],
                "quality": [-1, -1, -1]
            },
            "B": {
                "value": [4, 5, 6],
                "quality": [-2, -2, -2]
            },
            "C": {
                "value": [7, 8, 9],
                "quality": [-3, -3, -3]
            }
        }
        self.reader.writeStructredFile(filePath, data)
        
        if os.path.isfile(filePath):
            read = self.reader.readFile(filePath)
            for key, values in data.iteritems():
                self.assertTrue(sameEntries(values["value"], read.getColumn(key)))
        removeFile(filePath)

class TestEEGTableData(unittest.TestCase):

    def setUp(self):
        self.header = ["Timestamp", "X", "Y", "Z"]
        self.data = np.array([
            [1456820379.00, 1, 2, 3],
            [1456820379.25, 1, 2, 4],
            [1456820379.50, 1, 2, 5],
            [1456820379.75, 1, 2, 6],
            [1456820380.00, 1, 2, 7],
            [1456820380.25, 1, 2, 8],
            [1456820380.50, 1, 2, 9],
            [1456820380.75, 1, 2, 10],
            [1456820381.00, 1, 2, 11]
        ])
        self.eeg_data = EEGTableUtil(self.header, self.data)

    def test_getSamplingRate(self):
        # 9 values within 2 seconds = sampling rate 4.5
        self.assertTrue(self.eeg_data.getSamplingRate() == 4.5)

    def test_getColumn(self):
        for i, header in enumerate(self.header[1:3]):
            column = self.eeg_data.getColumn(header)
            # make sure data columns only contain X:1, Y:2
            self.assertTrue(countOcc(column, i+1) == len(self.data))

    def test_getColumn_withOffset(self):
        offset = 3
        column = self.eeg_data.getColumn("Z", offset)
        self.assertTrue(len(column) == len(self.data)-offset)
        self.assertTrue(sameEntries(column, [6, 7, 8, 9, 10, 11]))

    def test_getColumn_withOffsetAndLimit(self):
        offset = 3
        limit = 7
        column = self.eeg_data.getColumn("Z", offset, limit)
        self.assertTrue(len(column) == limit-offset)
        self.assertTrue(sameEntries(column, [6, 7, 8, 9]))

    def test_getColumn_withOffsetAndLength(self):
        offset = 2
        length = 5
        column = self.eeg_data.getColumn("Z", offset, length=length)
        self.assertTrue(len(column) == length)
        self.assertTrue(sameEntries(column, [5, 6, 7, 8, 9]))        

    def test_getColumn_withOffsetAndLimitAndLength(self):
        offset = 1
        limit = 7
        # length is ignored in this case
        length = 3
        column = self.eeg_data.getColumn("Z", offset, limit, length=length)
        self.assertTrue(len(column) == limit-offset)
        self.assertTrue(sameEntries(column, [4, 5, 6, 7, 8, 9]))     

    def test_getTimeIndex(self):
        self.assertTrue(self.eeg_data.getTimeIndex(1456820379.00) == 0)
        self.assertTrue(self.eeg_data.getTimeIndex(1456820379.75) == 3)
        self.assertTrue(self.eeg_data.getTimeIndex(1456820381) == 8)

    def test_getTimeIndex_notExactly(self):
        self.assertTrue(self.eeg_data.getTimeIndex(1456820379.00) == 0)
        self.assertTrue(self.eeg_data.getTimeIndex(1456820379.01) == 1)
        self.assertTrue(self.eeg_data.getTimeIndex(1456820379.5) == 2)
        self.assertTrue(self.eeg_data.getTimeIndex(1456820379.51) == 3)
        self.assertTrue(self.eeg_data.getTimeIndex(1456820379.74) == 3)
        self.assertTrue(self.eeg_data.getTimeIndex(1456820379.75) == 3)
        self.assertTrue(self.eeg_data.getTimeIndex(1456820379.76) == 4)
        self.assertTrue(self.eeg_data.getTimeIndex(1456820381) == 8)

    def test_getTimeIndex_outOfRange(self):
        with self.assertRaises(ValueError):
            self.eeg_data.getTimeIndex(1456820378.00)

        with self.assertRaises(ValueError):
            self.eeg_data.getTimeIndex(1456820382.00)

    def test_getColumnByTime(self):
        column = self.eeg_data.getColumnByTime("Z", 1456820379.00, 1456820379.75)
        self.assertTrue(sameEntries(column, [3, 4, 5]))

        column2 = self.eeg_data.getColumnByTime("Z", 1456820379.00, 1456820381)
        self.assertTrue(sameEntries(column2, [3, 4, 5, 6, 8, 8, 9, 10]))

    def test_getColumnByTime_notExactly(self):
        column = self.eeg_data.getColumnByTime("Z", 1456820379.00, 1456820379.75)
        self.assertTrue(sameEntries(column, [3, 4, 5]))
        
        column2 = self.eeg_data.getColumnByTime("Z", 1456820379.01, 1456820379.75)
        self.assertTrue(sameEntries(column2, [4, 5]))

        column3 = self.eeg_data.getColumnByTime("Z", 1456820379.00, 1456820379.74)
        self.assertTrue(sameEntries(column3, [3, 4, 5]))

        column4 = self.eeg_data.getColumnByTime("Z", 1456820379.00, 1456820379.76)
        self.assertTrue(sameEntries(column4, [3, 4, 5, 6])) 


    def test_getColumnByTime_outOfRange(self):
        with self.assertRaises(ValueError):
            self.eeg_data.getColumnByTime("Z", 1456820378.00, 1456820379.75)

        with self.assertRaises(ValueError):
            self.eeg_data.getColumnByTime("Z", 1456820379.00, 1456820382.0)

    def test__switchTime(self):
        x, y = 1, 2
        a, b = self.eeg_data._switchTime(x, y)
        self.assertEqual(x, b)
        self.assertEqual(y, a)

    def test__timeInData(self):
        data = self.eeg_data.getColumn("Timestamp")
        self.assertTrue(self.eeg_data._timeInData(data, 1456820379.75))
        self.assertFalse(self.eeg_data._timeInData(data, 1456820378))
        self.assertFalse(self.eeg_data._timeInData(data, 1456820382))


class TestEEGTableToPacketUtil(unittest.TestCase):

    def setUp(self):
        self.util = EEGTableToPacketUtil()

    def test_dequeue(self):
        data = self.util.dequeue() 
        self.assertEquals(len(data.sensors), 17)
        self.assertTrue("X" in data.sensors.keys())
        self.assertTrue("quality" in data.sensors["X"].keys())

if __name__ == '__main__':
    unittest.main()