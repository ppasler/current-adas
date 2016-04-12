#!/usr/bin/python

import unittest
import numpy as np
import matplotlib.pyplot as plt
import os.path

from util.fft_util import FFTUtil
from util.eeg_util import EEGUtil
from util.signal_util import SignalUtil
from util.eeg_table_reader import EEGTableReader, EEGTableData


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
    
    

class TestSignalUtil(unittest.TestCase):

    def setUp(self):
        self.util = SignalUtil()

    def test_normalize(self):
        testList = np.array([0, -5, 1, 10])
        normList = self.util.normalize(testList)
        self.assertEqual(len(testList), len(normList))
        self.assertTrue(max(normList) <= 1)
        self.assertTrue(min(normList) >= -1)

    def test_energie(self):
        testList = np.array([1, 2, 3, 4])
        energy = self.util.energy(testList)
        self.assertTrue(energy == 30)

class TestFFTUtil(unittest.TestCase):

    def setUp(self):
        self.util = FFTUtil()

    def test__removeMirrored(self):
        testList1 = np.array([0, 1, 2, 3, 4, 4, 3, 2, 1])
        mirrList = self.util._removeMirrored(testList1)
        self.assertEqual(len(mirrList), 5)

        testList2 = np.array([0, 1, 2, 3, 4, 3, 2, 1, 0])
        mirrList = self.util._removeMirrored(testList2)
        self.assertEqual(len(mirrList), 5)

    def test__process(self):
        testList = np.array([1, 2, -3, -4])
        procList = self.util._process(testList)
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
        sampFreq = 44100

        fft = self.util.fft(data)

        n = float(len(data))
        nUniquePts = np.ceil((n+1)/2.0)
        
        maxIndex = np.argmax(fft)

        # calc frequency array
        freqArray = np.arange(0, nUniquePts, 1.0) * (sampFreq / n);

        # should be around 12000
        self.assertTrue(11800 < freqArray[maxIndex] < 12200)
        

class TestEEGUtil(unittest.TestCase):

    def setUp(self):
        self.util = EEGUtil()

    def test_getChannels_short(self):
        data = [1, 2, 3, 4, 5, 6, 7, 8]

        channels = self.util.getChannels(data)

    def test_getChannels(self):
        fft = TEST_DATA_12000Hz

        channels = self.util.getChannels(fft)
        flattenChannels = np.hstack(channels.values())
        self.assertTrue(all([x in fft for x in flattenChannels]))
        
        self.assertTrue(len(flattenChannels) <= len(fft))
        self.assertTrue(len(flattenChannels) == 99)

    
    def test_getSingleChannels(self):
        fft = TEST_DATA_12000Hz
        channels = self.util.getChannels(fft)

        delta = self.util.getDeltaChannel(fft)
        self.assertTrue(len(delta) == 4)
        self.assertTrue(all([x in channels["delta"] for x in delta]))
               
        theta = self.util.getThetaChannel(fft)
        self.assertTrue(len(theta) == 4)
        self.assertTrue(all([x in channels["theta"] for x in theta]))
                
        alpha = self.util.getAlphaChannel(fft)
        self.assertTrue(len(alpha) == 5)
        self.assertTrue(all([x in channels["alpha"] for x in alpha]))
                
        beta = self.util.getBetaChannel(fft)
        self.assertTrue(len(beta) == 17)
        self.assertTrue(all([x in channels["beta"] for x in beta]))
          
        gamma = self.util.getGammaChannel(fft)
        self.assertTrue(len(gamma) == 69)
        self.assertTrue(all([x in channels["gamma"] for x in gamma]))        


class TestEEGTableReader(unittest.TestCase):

    def setUp(self):
        self.reader = EEGTableReader()

    def test_readData(self):
        file_path = "example_short.csv"
        if os.path.isfile(file_path):
            self.reader.readData(file_path)

    def test_readHeader(self):
        file_path = "example_short.csv"
        if os.path.isfile(file_path):
            self.reader.readHeader(file_path)
            
    def test_readFile(self):
        file_path = "example_short.csv"
        if os.path.isfile(file_path):
            self.reader.readFile(file_path)


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
        self.eeg_data = EEGTableData(self.header, self.data)

    def test_getSampleRate(self):
        # 9 values within 2 seconds = sampling rate 4.5
        self.assertTrue(self.eeg_data.getSampleRate() == 4.5)

    def countOcc(self, a, x):
        return len(np.where(a==x)[0])

    def test_getColumn(self):
        for i, header in enumerate(self.header[1:3]):
            column = self.eeg_data.getColumn(header)
            # make sure data columns only contain X:1, Y:2
            self.assertTrue(self.countOcc(column, i+1) == len(self.data))

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

if __name__ == '__main__':
    unittest.main()












    
