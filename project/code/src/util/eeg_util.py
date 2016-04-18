#!/usr/bin/python

DELTA_RANGE = (0, 4)
THETA_RANGE = (4, 8)
ALPHA_RANGE = (8, 13)
BETA_RANGE  = (13, 30)
GAMMA_RANGE = (30, 99)


class EEGUtil(object):

    '''
    This class does useful things with EEG signals
    
    Like splitting by channel
    DELTA =  0 -  4hz
    THETA =  4 -  8hz
    ALPHA =  8 - 13hz
    BETA  = 13 - 30hz
    GAMMA = 30 - 99hz
    
    '''

    channel_ranges = {
        "delta": DELTA_RANGE,
        "theta": THETA_RANGE,
        "alpha": ALPHA_RANGE,
        "beta":  BETA_RANGE,
        "gamma": GAMMA_RANGE}

    def getChannels(self, fft):
        '''
        Get a fft signal split by channels 
        {
         "delta": [1, 2, 3],
         ...
         "gamma": [5, 6, 7]
        }
        
        :param array fft:     eeg data with performed fft
        
        :return dict: split channels as map
        '''
        channels = {}
        for label, freqRange in EEGUtil.channel_ranges.iteritems():
            channels[label] = fft[slice(*freqRange)]
        return channels
            
    def getDeltaChannel(self, fft):
        '''
        Get delta channel of a fft signal
        
        :param array    fft     eeg data with performed fft
        
        :return array   split from 0-4hz
        '''
        return fft[slice(*self.channel_ranges["delta"])]
               
    def getThetaChannel(self, fft):
        '''
        Get theta channel of a fft signal
        
        :param array    fft     eeg data with performed fft
        
        :return array   split from 4-8hz
        '''
        return fft[slice(*self.channel_ranges["theta"])]
                
    def getAlphaChannel(self, fft):
        '''
        Get alpha channel of a fft signal
        
        :param array    fft     eeg data with performed fft
        
        :return array   split from 8-13hz
        '''
        return fft[slice(*self.channel_ranges["alpha"])]
                
    def getBetaChannel(self, fft):
        '''
        Get delta channel of a fft signal
        
        :param array    fft     eeg data with performed fft
        
        :return array   split from 13-30hz
        '''
        return fft[slice(*self.channel_ranges["beta"])]
          
    def getGammaChannel(self, fft):
        '''
        Get delta channel of a fft signal
        
        :param array    fft     eeg data with performed fft
        
        :return array   split from 30-99hz
        '''
        return fft[slice(*self.channel_ranges["gamma"])]
