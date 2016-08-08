#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 10.05.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

import warnings

from numpy import count_nonzero, nanmax, nanmin, isnan, nanmean, \
    nanstd, nanvar, NaN
from scipy.signal import butter, lfilter


class SignalUtil(object):

    def __init__(self):
        """This class does signal processing with raw signals"""

    def normalize(self, data):
        '''normalizes data between -1 and 1
        Ignores NaN values

        :param numpy.array data: list of values
        
        :return: normalized data
        :rtype: numpy.array
        '''
        #TODO check condition
        if count_nonzero(data) == 0 or isnan(data).all():
            return data
        extreme = float(max(nanmax(data), abs(nanmin(data))))

        return data / extreme

    def maximum(self, data):
        '''calculates the signal max 
        Ignores NaN values

        :param numpy.array data: list of values
        
        :return: signal maximum
        :rtype: float
        '''
        with warnings.catch_warnings(): #avoid warning because of NaN values
            warnings.simplefilter("ignore", category=RuntimeWarning)
            return nanmax(data)

    def minimum(self, data):
        '''calculates the signal min
        Ignores NaN values

        :param numpy.array data: list of values
        
        :return: signal minimum
        :rtype: float
        '''
        with warnings.catch_warnings(): #avoid warning because of NaN values
            warnings.simplefilter("ignore", category=RuntimeWarning)
            return nanmin(data)

    def mean(self, data):
        '''calculates the signal mean
        Ignores NaN values

        :param numpy.array data: list of values
        
        :return: signal mean
        :rtype: float
        '''
        with warnings.catch_warnings(): #avoid warning because of NaN values
            warnings.simplefilter("ignore", category=RuntimeWarning)
            return nanmean(data)

    def energy(self, data):
        '''calculates signal energy 
        Ignores NaN values

        :math:`E = \sum(data^2)`
        
        * `Energy_(signal_processing) <https://en.wikipedia.org/wiki/Energy_(signal_processing)>`_
        
        :param numpy.array data: list of values
        
        :return: signal energy
        :rtype: float
        '''
        if isnan(data).all():
            return NaN
        return sum(self._removeNaN(data) ** 2)

    def _removeNaN(self, data):
        return data[~isnan(data)]

    def std(self, data):
        '''calculates the signal' standard deviation
        Ignores NaN values

        :param numpy.array data: list of values
        
        :return: standard deviation
        :rtype: float
        '''
        with warnings.catch_warnings(): #avoid warning because of NaN values
            warnings.simplefilter("ignore", category=RuntimeWarning)
            return nanstd(data)

    def var(self, data):
        '''calculates the signals' variance
        Ignores NaN values

        :param numpy.array data: list of values
        
        :return: signal variance
        :rtype: float
        '''
        with warnings.catch_warnings(): #avoid warning because of NaN values
            warnings.simplefilter("ignore", category=RuntimeWarning)
            return nanvar(data)

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
