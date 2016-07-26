#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 13.06.2016

:author: Paul Pasler
:organization: Reutlingen University
'''
from itertools import groupby

from numpy import array, count_nonzero, isnan, where, hstack, ones, NAN
from scipy.ndimage.morphology import binary_closing

MAX_ZERO_SEQUENCE_LENGTH = 3
MAX_SEQUENCE_LENGTH = 3

class QualityUtil(object):
    """removes signal data with low quality"""

    def replaceOutliners(self, data, lowerBound, upperBound, value=None):
        """outliner values beyond 'lowerBound' and above 'upperBound' will be set to 'value'
        if value is not set, the values will be set to upper and lower bound
          
        inplace method
        :param numpy.array data: list of values
        :param float lowerBound: values < this param will be set to 'value'
        :param float upperBound: values > this param will be set to 'value'
        :param float value: default value for all outside the bounds
        
        :return: data without outliners 
        :rtype: numpy.array
        """
        #TODO could be nicer / faster?
        # http://stackoverflow.com/questions/19666626/replace-all-elements-of-python-numpy-array-that-are-greater-than-some-value
        if value == None:
            data[data > upperBound] = upperBound
            data[data < lowerBound] = lowerBound
        else:
            data[data > upperBound] = value
            data[data < lowerBound] = value
        return data

    def replaceBadQuality(self, data, quality, threshold, value):
        """replaces values from data with value where quality < threshold
        
        inplace method
        :param numpy.array data: list of values
        :param numpy.array quality: list of quality
        :param float threshold: param to compare quality with
        :param float value: param to replace data values
        
        :return: data without bad quality values
        :rtype: numpy.array
        """
        #TODO is this the right way?
        if len(data) != len(quality):
            raise ValueError("data and quality must have the same length")
        
        for i, qual in enumerate(quality):
            if qual < threshold:
                data[i] = value
        return data

    def countZeros(self, data):
        '''calculates the number of countZeros in data

        :param numpy.array data: list of values
        
        :return: zero count
        :rtype: int
        '''
        return len(data) - count_nonzero(data)

    def countNans(self, data):
        '''calculates the number of NaNs in data

        :param numpy.array data: list of values
        
        :return: NaN count
        :rtype: int
        '''
        return count_nonzero(isnan(data))

    def replaceZeroSequences(self, data):
        '''replaces zero sequences, which is an unwanted artefact, with NaN 
        see http://stackoverflow.com/questions/38584956/replace-a-zero-sequence-with-other-value

        :param numpy.array data: list of values

        :return: zero sequences replaced data
        :rtype: numpy.array
        '''
        a_extm = hstack((True,data!=0,True))
        mask = a_extm == binary_closing(a_extm,structure=ones(MAX_ZERO_SEQUENCE_LENGTH))
        return where(~a_extm[1:-1] & mask[1:-1],NAN, data)

    def countSequences(self, data):
        seqList = self._getSequenceList(data)
        return len([s for s in seqList if len(s) >= MAX_SEQUENCE_LENGTH])

    def replaceSequences(self, data):
        '''replaces any sequences of more than MAX_SEQUENCE_LENGTH same numbers in a row with NaN 
        see http://stackoverflow.com/questions/38584956/replace-a-zero-sequence-with-other-value

        :param numpy.array data: list of values

        :return: sequences replaced data
        :rtype: numpy.array
        '''
        seqList = self._getSequenceList(data)
        return array( [ item for l in seqList for item in l ] )

    def _getSequenceList(self, data):
        return array([self._getSequence(value, it) for value, it in groupby(data)])

    def _getSequence(self, value, it):
        itLen = sum(1 for _ in it) # length of iterator
    
        if itLen>=MAX_SEQUENCE_LENGTH:
            return [ NAN ]*itLen
        else:
            return [ value ]*itLen


if __name__ == '__main__':
    pass