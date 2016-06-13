#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 13.06.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

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

if __name__ == '__main__':
    pass