#!/usr/bin/python

class SignalUtil(object):

    def __init__(self):
        """This class does signal processing with raw signals"""

    def normalize(self, data):
        '''normalizes data between -1 and 1
        @param data: array like list of values
        
        @return: normalized data
        '''
        
        extreme = float(max(max(data), abs(min(data))))
        return data / extreme

    def energy(self, data):
        '''calc energy E = sum(data ** 2) https://en.wikipedia.org/wiki/Energy_(signal_processing)
        
        @param data: array like list of values
        
        @return: signal energy
        
        '''
        
        return sum(data ** 2)
