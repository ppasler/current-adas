#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 13.06.2016

:author: Paul Pasler
:organization: Reutlingen University
'''
from itertools import groupby

from numpy import array, count_nonzero, isnan, where, hstack, ones, NaN, errstate, copy, nan_to_num, \
    clip
from scipy.ndimage.morphology import binary_closing

from config.config import ConfigProvider


DEFAULT_REPLACE_VALUE = NaN

class QualityUtil(object):
    """removes signal data with low quality"""
    
    def __init__(self):
        self.config = ConfigProvider().getProcessingConfig()
        self.upperBound = self.config.get("upperBound")
        self.lowerBound = self.config.get("lowerBound")
        self.minQuality = self.config.get("minQual")
        self.maxSeqLength = self.config.get("maxSeqLength")
        self.maxNaNValues = self.config.get("maxNaNValues")

    def _copyArray(self, data):
        return copy(data[:])

    def replaceOutliners(self, data, value=None, lowerBound=None, upperBound=None):
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
        if lowerBound == None:
            lowerBound=self.lowerBound
        if upperBound == None:
            upperBound=self.upperBound
        #TODO could be nicer / faster?
        with errstate(invalid='ignore'): #avoid warning because of DEFAULT_REPLACE_VALUE value
            ret = self._copyArray(data)
            if value == None:
                #http://stackoverflow.com/questions/41329691/pythonic-way-to-replace-list-values-with-upper-and-lower-bound/41329750#41329750
                clip(ret, lowerBound, upperBound, out=ret)
            else:
                # http://stackoverflow.com/questions/19666626/replace-all-elements-of-python-numpy-array-that-are-greater-than-some-value
                ret[ret > upperBound] = value
                ret[ret < lowerBound] = value
        return ret

    def countOutliners(self, data, lowerBound=None, upperBound=None):
        """counts the outliner values beyond 'lowerBound' and above 'upperBound'
     
        :param numpy.array data: list of values
        :param float lowerBound: values < this param will be set to 'value'
        :param float upperBound: values > this param will be set to 'value'
        
        :return: number of outliners in data 
        :rtype: int
        """
        if lowerBound == None:
            lowerBound=self.lowerBound
        if upperBound == None:
            upperBound=self.upperBound
        
        cdata = copy(data[:])
        with errstate(invalid='ignore'): 
            cdata[cdata > upperBound] = DEFAULT_REPLACE_VALUE
            cdata[cdata < lowerBound] = DEFAULT_REPLACE_VALUE
        return count_nonzero(isnan(cdata))

    def replaceBadQuality(self, data, quality, value, threshold=None):
        """replaces values from data with value where quality < threshold
        
        inplace method
        :param numpy.array data: list of values
        :param numpy.array quality: list of quality
        :param float threshold: param to compare quality with
        :param float value: param to replace data values
        
        :return: data without bad quality values
        :rtype: numpy.array
        """
        if len(data) != len(quality):
            raise ValueError("data and quality must have the same length")
        
        if threshold == None:
            threshold = self.minQuality
        #TODO make me nice
        ret = self._copyArray(data)
        ret[quality < threshold] = value

        return ret

    def countBadQuality(self, data, quality, threshold=None):
        """counts values from data with value where quality < threshold
        
        inplace method
        :param numpy.array data: list of values
        :param numpy.array quality: list of quality
        :param float threshold: param to compare quality with
        
        :return: number of data with bad quality values
        :rtype: int
        """
        if len(data) != len(quality):
            raise ValueError("data and quality must have the same length")
        if threshold == None:
            threshold = self.minQuality
        
        count = 0
        for _, qual in enumerate(quality):
            if qual < threshold:
                count += 1
        return count

    def countZeros(self, data):
        '''calculates the number of countZeros in data

        :param numpy.array data: list of values
        
        :return: zero count
        :rtype: int
        '''
        return len(data) - count_nonzero(data)

    def replaceNans(self, data):
        '''replaces NaNs in data with zero

        :param numpy.array data: list of values
        
        :return: data without Nan
        :rtype: numpy.array
        '''
        return nan_to_num(self._copyArray(data))

    def countNans(self, data):
        '''calculates the number of NaNs in data

        :param numpy.array data: list of values
        
        :return: NaN count
        :rtype: int
        '''
        return count_nonzero(isnan(data))

    def isInvalidData(self, data):
        '''considers a data set invalid, if there are more NaNs than maxNaNValues in the set

        :param numpy.array data: list of values
        
        :return: invalid
        :rtype: boolean
        '''
        return self.maxNaNValues < count_nonzero(isnan(data))

    def replaceZeroSequences(self, data):
        '''replaces zero sequences, which is an unwanted artefact, with DEFAULT_REPLACE_VALUE 
        see http://stackoverflow.com/questions/38584956/replace-a-zero-sequence-with-other-value

        :param numpy.array data: list of values

        :return: zero sequences replaced data
        :rtype: numpy.array
        '''
        a_extm = hstack((True,data!=0,True))
        mask = a_extm == binary_closing(a_extm,structure=ones(self.maxSeqLength))
        return where(~a_extm[1:-1] & mask[1:-1],DEFAULT_REPLACE_VALUE, data)

    def countSequences(self, data):
        seqList = self._getSequenceList(data)
        return len([s for s in seqList if len(s) >= self.maxSeqLength])

    def replaceSequences(self, data):
        '''replaces any sequences of more than MAX_SEQUENCE_LENGTH same numbers in a row with DEFAULT_REPLACE_VALUE 
        see http://stackoverflow.com/questions/38584956/replace-a-zero-sequence-with-other-value

        :param numpy.array data: list of values

        :return: sequences replaced data
        :rtype: numpy.array
        '''
        ret = self._copyArray(data)
        seqList = self._getSequenceList(ret)
        return array( [ item for l in seqList for item in l ] )

    def _getSequenceList(self, data):
        return array([self._getSequence(value, it) for value, it in groupby(data)])

    def _getSequence(self, value, it):
        itLen = sum(1 for _ in it) # length of iterator
    
        if itLen>=self.maxSeqLength:
            return [ DEFAULT_REPLACE_VALUE ]*itLen
        else:
            return [ value ]*itLen

if __name__ == '__main__':
    pass