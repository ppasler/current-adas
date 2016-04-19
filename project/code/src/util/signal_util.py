#!/usr/bin/python

class SignalUtil(object):

    def __init__(self):
        """This class does signal processing with raw signals"""

    def normalize(self, data):
        '''normalizes data between -1 and 1
        
        :param numpy.array data: list of values
        
        :return: normalized data
        :rtype: numpy.array
        '''
        
        extreme = float(max(max(data), abs(min(data))))
        return data / extreme

    def normalize2(self, data):
        '''normalizes data between 0 and 1
        
        Using formula :math:`z_i = (x_i-\min(x)) / (\max(x)-\min(x))`.
        
        :param numpy.array data: list of values
        
        :return: normalized data
        :rtype: numpy.array
        '''
        dataMin = min(data)
        return (data-dataMin)/(max(data)-dataMin)

    def energy(self, data):
        '''calculates signal energy 
        
        :math:`E = \sum(data^2)`
        
        * `Energy_(signal_processing) <https://en.wikipedia.org/wiki/Energy_(signal_processing)>`_
        
        :param numpy.array data: list of values
        
        :return: signal energy
        :rtype: float
        '''
        return sum(data ** 2)