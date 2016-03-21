#!/usr/bin/python

import numpy as np

DELTA_RANGE = (0, 4)
THETA_RANGE = (4, 8)
ALPHA_RANGE = (8, 13)
BETA_RANGE  = (13, 30)
GAMMA_RANGE = (30, 99)


class EEGUtil(object):

    channel_ranges = {
        "delta": DELTA_RANGE,
        "theta": THETA_RANGE,
        "alpha": ALPHA_RANGE,
        "beta":  BETA_RANGE,
        "gamma": GAMMA_RANGE}

    def __init__(self):
        """This class does useful things with EEG signals"""

    def getChannels(self, fft):
        channels = {}
        for label, freqRange in EEGUtil.channel_ranges.iteritems():
            channels[label] = fft[slice(*freqRange)]
        return channels
            
    def getDeltaChannel(self, fft):
        return fft[slice(*self.channel_ranges["delta"])]
               
    def getThetaChannel(self, fft):
        return fft[slice(*self.channel_ranges["theta"])]
                
    def getAlphaChannel(self, fft):
        return fft[slice(*self.channel_ranges["alpha"])]
                
    def getBetaChannel(self, fft):
        return fft[slice(*self.channel_ranges["beta"])]
          
    def getGammaChannel(self, fft):
        return fft[slice(*self.channel_ranges["gamma"])]
