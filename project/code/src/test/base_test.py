#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 02.07.2016

:author: Paul Pasler
:organization: Reutlingen University
'''
from os.path import join, dirname, abspath
import sys
sys.path.append(join(dirname(__file__), '..'))

from os import remove
import unittest

import numpy as np



class BaseTest(unittest.TestCase):

    PATH = dirname(abspath(__file__)) +  "/../../examples/"

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

    TEST_DATA_ZERO = np.array([ 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0 ])

    TEST_DATA_MIXED = np.array([ np.NAN, 1.0, 0.0, 1.0, 0.0, np.NAN ])

    TEST_DATA_NAN = np.array([ np.NAN, np.NAN, np.NAN ,np.NAN ])

    def countOcc(self, a, x):
        return len(np.where(a==x)[0])
    
    def removeFile(self, filePath):
        try:
            remove(filePath)
        except OSError as e:
            print e.message