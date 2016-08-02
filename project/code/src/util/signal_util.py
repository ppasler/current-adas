#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 10.05.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

from numpy import mean, var, count_nonzero, std
from scipy.signal import butter, lfilter


class SignalUtil(object):

    def __init__(self):
        """This class does signal processing with raw signals"""

    def normalize(self, data):
        '''normalizes data between -1 and 1

        :param numpy.array data: list of values
        
        :return: normalized data
        :rtype: numpy.array
        '''
        if count_nonzero(data) == 0:
            return data
        extreme = float(max(max(data), abs(min(data))))

        return data / extreme

    def maximum(self, data):
        '''calculates the signal max 

        :param numpy.array data: list of values
        
        :return: signal maximum
        :rtype: float
        '''
        return max(data)

    def minimum(self, data):
        '''calculates the signal min

        :param numpy.array data: list of values
        
        :return: signal minimum
        :rtype: float
        '''
        return min(data)

    def mean(self, data):
        '''calculates the signal mean

        :param numpy.array data: list of values
        
        :return: signal mean
        :rtype: float
        '''
        return mean(data)

    def energy(self, data):
        '''calculates signal energy 
        
        :math:`E = \sum(data^2)`
        
        * `Energy_(signal_processing) <https://en.wikipedia.org/wiki/Energy_(signal_processing)>`_
        
        :param numpy.array data: list of values
        
        :return: signal energy
        :rtype: float
        '''
        return sum(data ** 2)

    def std(self, data):
        '''calculates the signal' standard deviation

        :param numpy.array data: list of values
        
        :return: standard deviation
        :rtype: float
        '''
        return std(data)

    def var(self, data):
        '''calculates the signals' variance

        :param numpy.array data: list of values
        
        :return: signal variance
        :rtype: float
        '''
        return var(data)

    def butterBandpass(self, lowcut, highcut, samplingRate, order=5):
        '''
        Creates a butterworth filter design from lowcut to highcut and returns the filter coefficients
        :see: `scipy.signal.butter <http://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.butter.html#scipy.signal.butter>`_

        note: :math:`lowcut >= 0` and :math:`highcut <= samplingRate / 2`

        :param int lowcut: lower border
        :param int highcut: upper border
        :param int samplingRate: sample frequency
        
        :return: filter coefficients a, b
        :rtype: float
        '''
        # TODO throw exception here? 
        if highcut > samplingRate / 2:
            highcut = samplingRate / 2
        if lowcut < 0:
            lowcut = 0
        
        nyq = 0.5 * samplingRate
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        return b, a
    
    
    def butterBandpassFilter(self, data, lowcut, highcut, samplingRate, order=5):
        b, a = self.butterBandpass(lowcut, highcut, samplingRate, order)
        y = lfilter(b, a, data)
        return y
