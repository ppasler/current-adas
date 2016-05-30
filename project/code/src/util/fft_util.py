#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 10.05.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

import numpy as np

class FFTUtil(object):
    '''
        process raw eeg data by performing a fast-fourier-transformation

        see: src.example.fft_sound_example

        inspired by:
        
        * `basic sound processing python <http://samcarcagno.altervista.org/blog/basic-sound-processing-python>`_
        * `tech notes fft <https://web.archive.org/web/20120615002031/http://www.mathworks.com/support/tech-notes/1700/1702.html>`_
    '''

    def _removeMirrored(self, fft_data, n):
        '''remove mirrored data, only take left side
        '''
        
        nUniquePts = np.ceil((n+1)/2.0)
        return fft_data[0:nUniquePts]

    def _doubleValues(self, fft_data):
        '''double values to ensure fft_data has the same power as bevor calling _removeMirrored()'''
        
        n_fft_data = len(fft_data)
        
        # multiply by two (see technical document for details)
        # odd nfft excludes Nyquist point
        if n_fft_data % 2 > 0:                      # odd number of points fft
            fft_data[1:n_fft_data] = fft_data[1:n_fft_data] * 2
        else:                                       # even number of points fft
            fft_data[1:n_fft_data -1] = fft_data[1:n_fft_data - 1] * 2

        return fft_data

    def _process(self, fft_data, n):
        fft_data = abs(fft_data)

        fft_data = fft_data / float(n)      # scale by the number of points so that
                                            # the magnitude does not depend on the length 
                                            # of the signal or on its sampling frequency  
        fft_data = fft_data**2              # square it to get the power 

        return fft_data

    def fft(self, data):
        '''FFT with several processing steps
        
        :param array data: raw signal data
        * better use normalized data
        * n_data should be a power of 2
        
        # fourier transform (numpy implementation)
        # remove mirrored data
        # process fft data
        # make sure energy stays the same
        
        :return: tranformed data
        :rtype: array
        '''
        n = len(data)
        # make sure n_data is a power of 2
        fft_data = np.fft.fft(data)                   # fourier transform

        fft_data = self._removeMirrored(fft_data, n)  # remove mirrored data

        fft_data = self._process(fft_data, n)         # process fft data

        fft_data = self._doubleValues(fft_data)       # make sure energy stays the same

        return fft_data
