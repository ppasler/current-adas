#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 02.07.2016

:author: Paul Pasler
:organization: Reutlingen University
'''
import logging
from posdbos.util.file_util import FileUtil
from helper.plotter.eeg_signal_plotter import readEEGFile
logging.basicConfig(level=logging.INFO,
                format='%(asctime)s.%(msecs)03d %(levelname)-8s %(module)s.%(funcName)s:%(lineno)d %(message)s',
                datefmt='%H:%M:%S')
from os.path import join, dirname, abspath
import sys
sys.path.append(join(dirname(__file__), '..'))
import matplotlib.pyplot as plt
import unittest



class BaseTest(unittest.TestCase):

    PATH = dirname(abspath(__file__)) + "/test_data/"

    def getData1024CSV(self):
        return self.PATH + "example_1024.csv"

    def readData1024CSV(self):
        filePath = self.getData1024CSV()
        return self.readEEGFile(filePath)

    def readEEGFile(self, filePath):
        return FileUtil().getDto(filePath)
    
    def closePlots(self):
        plt.cla()   # Clear axis
        plt.clf()   # Clear figure
        plt.close() # Close a figure window