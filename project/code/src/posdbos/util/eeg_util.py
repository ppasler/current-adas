#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 10.05.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

from posdbos.util.signal_util import SignalUtil
from config.config import ConfigProvider
from numpy import ceil

# TODO should be from 0.5 to 4
DELTA_RANGE = (1, 4)
THETA_RANGE = (4, 8)
ALPHA_RANGE = (8, 13)
BETA_RANGE  = (13, 30)

samplingRate = ConfigProvider().getEmotivConfig().get("samplingRate")
gammaMax = min(samplingRate / 2, 99)
GAMMA_RANGE = (30, gammaMax)


class EEGUtil(object):

    '''
    This class does useful things with EEG signals
    
    Like splitting by channel
    DELTA =  0.5 -  4hz
    THETA =  4   -  8hz
    ALPHA =  8   - 13hz
    BETA  = 13   - 30hz
    GAMMA = 30   - 99hz
    
    '''

    channel_ranges = {
        "delta": DELTA_RANGE,
        "theta": THETA_RANGE,
        "alpha": ALPHA_RANGE,
        "beta":  BETA_RANGE,
        "gamma": GAMMA_RANGE}

    def __init__(self):
        self.signalUtil = SignalUtil()

    def getChannels(self, fft):
        '''
        Get a fft signal split by channels 
        {
         "delta": [1, 2, 3],
         ...
         "gamma": [5, 6, 7]
        }
        
        :param array fft:     eeg data with performed fft
        
        :return: split channels as map
        :rtype: dict
        '''
        channels = {}
        for label, freqRange in EEGUtil.channel_ranges.iteritems():
            channels[label] = fft[slice(*self._getSliceParam(freqRange))]
        return channels

    def _getSliceParam(self, freqRange):
        return (int(ceil(freqRange[0])), int(ceil(freqRange[1])))

    def getDeltaChannel(self, fft):
        '''
        Get delta channel of a fft signal
        
        :param array    fft:     eeg data with performed fft
        
        :return: split from 0.5-4hz
        :rtype: array
        '''
        return fft[slice(*self._getSliceParam(self.channel_ranges["delta"]))]
               
    def getThetaChannel(self, fft):
        '''
        Get theta channel of a fft signal
        
        :param array    fft:     eeg data with performed fft
        
        :return: split from 4-8hz
        :rtype: array
        '''
        return fft[slice(*self.channel_ranges["theta"])]
                
    def getAlphaChannel(self, fft):
        '''
        Get alpha channel of a fft signal
        
        :param array    fft:     eeg data with performed fft
        
        :return: split from 8-13hz
        :rtype: array 
        '''
        return fft[slice(*self.channel_ranges["alpha"])]
                
    def getBetaChannel(self, fft):
        '''
        Get delta channel of a fft signal
        
        :param array    fft:     eeg data with performed fft
        
        :return: split from 13-30hz
        :rtype: array 
        '''
        return fft[slice(*self.channel_ranges["beta"])]
          
    def getGammaChannel(self, fft):
        '''
        Get delta channel of a fft signal
        
        :param array    fft:     eeg data with performed fft
        
        :return: split from 30-99hz
        :rtype: array 
        '''
        return fft[slice(*self.channel_ranges["gamma"])]


    def getWaves(self, eeg, samplingRate):
        '''
        Get a eeg signal split by waves 
        {
         "delta": [1, 2, 3],
         ...
         "gamma": [5, 6, 7]
        }
        
        :param numpy.array eeg:     eeg data with performed butterworth filter
        
        :return: split channels as map
        :rtype: dict 
        '''
        waves = {}
        for label, (lowcut, highcut) in EEGUtil.channel_ranges.iteritems():
            waves[label] = self.signalUtil.butterBandpassFilter(eeg, lowcut, highcut, samplingRate)
        return waves

    def getDeltaWaves(self, eeg, samplingRate):
        '''
        Get band pass filtered delta waves (0.5-4hz) of a eeg signal 
        
        :param numpy.array    eeg     raw eeg data
        
        :return: filtered signal
        :rtype:  numpy.array
        '''
        lowcut, highcut = self.channel_ranges["delta"]
        return self.signalUtil.butterBandpassFilter(eeg, lowcut, highcut, samplingRate)

    def getThetaWaves(self, eeg, samplingRate):
        '''
        Get band pass filtered theta waves (4-8hz) of an eeg signal 
        
        :param numpy.array    eeg:     raw eeg data
        
        :return: filtered signal
        :rtype:  numpy.array
        '''
        lowcut, highcut = self.channel_ranges["theta"]
        return self.signalUtil.butterBandpassFilter(eeg, lowcut, highcut, samplingRate)

    def getAlphaWaves(self, eeg, samplingRate):
        '''
        Get band pass filtered alpha waves (8-13hz) of an eeg signal 
        
        :param numpy.array    eeg     raw eeg data
        
        :return: filtered signal
        :rtype:  numpy.array
        '''
        lowcut, highcut = self.channel_ranges["alpha"]
        return self.signalUtil.butterBandpassFilter(eeg, lowcut, highcut, samplingRate)
                
    def getBetaWaves(self, eeg, samplingRate):
        '''
        Get band pass filtered beta waves (13-30hz) of an eeg signal 
        
        :param numpy.array    eeg     raw eeg data
        
        :return: filtered signal
        :rtype:  numpy.array
        '''
        lowcut, highcut = self.channel_ranges["beta"]
        return self.signalUtil.butterBandpassFilter(eeg, lowcut, highcut, samplingRate)
                
    def getGammaWaves(self, eeg, samplingRate):
        '''
        Get band pass filtered gamma waves (30-99hz) or 30-samplingRate/2 of a eeg signal 
        
        :param numpy.array    eeg     raw eeg data
        
        :return: filtered signal
        :rtype:  numpy.array
        '''
        lowcut, highcut = self.channel_ranges["gamma"]
        return self.signalUtil.butterBandpassFilter(eeg, lowcut, highcut, samplingRate)
