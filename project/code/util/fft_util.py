#!/usr/bin/python


import numpy as np

from signal_util import SignalUtil

class FFTUtil(object):
    '''inspired by:
        * http://samcarcagno.altervista.org/blog/basic-sound-processing-python/
        * https://web.archive.org/web/20120615002031/http://www.mathworks.com/support/tech-notes/1700/1702.html
    '''

    def __init__(self):
        """This class does FFT for EEG signals"""
        self.signal_util = SignalUtil()

    def _removeMirrored(self, fft_data):
        '''remove mirrored data, only take left side'''
        
        nUniquePts = np.ceil((len(fft_data)+1)/2.0)
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

    def _process(self, fft_data):
        n_fft_data = float(len(fft_data))
        
        fft_data = abs(fft_data)

        fft_data = fft_data / n_fft_data    # scale by the number of points so that
                                            # the magnitude does not depend on the length 
                                            # of the signal or on its sampling frequency  
        fft_data = fft_data**2              # square it to get the power 

        return fft_data

    def fft(self, data):
        '''FFT with several processing steps'''
        n_data = float(len(data))                   # length of data points

        data = self.signal_util.normalize(data)     # normalize from -1 to 1

        # make sure n_data is a power of 2
        fft_data = np.fft.fft(data)                 # fourier transform

        fft_data = self._removeMirrored(fft_data)   # remove mirrored data
        
        fft_data = self._process(fft_data)          # process fft data

        fft_data = self._doubleValues(fft_data)     # make sure energy stays the same

        return fft_data
