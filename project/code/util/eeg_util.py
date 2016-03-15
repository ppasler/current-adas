#!/usr/bin/python

import numpy as np

DELTA_RANGE = slice(0.1, 4)
THETA_RANGE = slice(4, 8)
ALPHA_RANGE = slice(8, 13)
BETA_RANGE  = slice(13, 30)
GAMMA_RANGE = slice(30, 99)



CHANNELS = {
    "delta": DELTA_RANGE,
    "theta": THETA_RANGE,
    "alpha": ALPHA_RANGE,
    "beta":  BETA_RANGE,
    "gamma": GAMMA_RANGE}



class EEGUtil(object):

    def __init__(self):
        """This class does useful things with EEG signals"""

    def getChannels(self, fft):
        channels = {}
        for label, freqRange in CHANNELS.iteritems():
            channels[label] = fft[freqRange]
        return channels
            
    def getAlphaChannel(self, fft):
        return fft[CHANNELS[alpha]]
        
