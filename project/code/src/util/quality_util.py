#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 13.06.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

class QualityUtil(object):
    """removes signal data with low quality"""

    def removeOutliners(self, data, lowerBound, upperBound, value=None):
        """outliner values beyond 'lowerBound' and above 'upperBound' will be set !inplace! to 'value'
        
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

if __name__ == '__main__':
    pass