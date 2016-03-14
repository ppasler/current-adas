#!/usr/bin/python

import numpy as np

from scipy.io import wavfile

class FFTUtil(object):

    def __init__(self):
        """This class does FFT for EEG signals"""

    def _normalize(self, data):
        '''normalizes data between -1 and 1'''
        extreme = float(max(max(data), abs(min(data))))
        return data / extreme

    def _process(self, p, n):
        nUniquePts = np.ceil((n+1)/2.0) # mirrored data, only take one side
        
        p = p[0:nUniquePts]
        
        p = abs(p)

        p = p / n       # scale by the number of points so that
                        # the magnitude does not depend on the length 
                        # of the signal or on its sampling frequency  
        p = p**2        # square it to get the power 

        # multiply by two (see technical document for details)
        # odd nfft excludes Nyquist point
        if n % 2 > 0:                           # odd number of points fft
            p[1:len(p)] = p[1:len(p)] * 2
        else:                                   # even number of points fft
            p[1:len(p) -1] = p[1:len(p) - 1] * 2

        return p

    def fft(self, data, sampFreq=100):
        '''FFT with several processing steps'''
        n = float(len(data))            # length of data points
        nUniquePts = np.ceil((n+1)/2.0) # mirrored data, only take one side

        data = self._normalize(data)    # normalize from -1 to 1
        
        p = np.fft.fft(data)            # fourier transform
        
        p = self._process(p, n)         # process fft data

        return p
