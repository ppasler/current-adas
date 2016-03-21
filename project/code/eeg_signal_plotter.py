#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt

from util.eeg_table_reader import EEGTableReader
from util.fft_util import FFTUtil
from util.eeg_util import EEGUtil
from util.signal_util import SignalUtil



class EEGSignalPlotter(object):

    def __init__(self):
        """This class plots EEG signals"""

    def plotLine(self, data, axis, label):
        axis.plot(data)
        axis.set_ylabel(label)

    def plotRawSignal(self, eeg_data, labels):
        ret = plt.subplots(len(labels), sharex=True)
        figure = ret[0]
        axis = ret[1]
        
        for i, label in enumerate(labels):
            data = eeg_data.getColumn(label)
            self.plotLine(data, axis[i], label)               

        plt.show()

    def plotFFTSignals(self, eeg_data, labels):
        for label in labels:
            self.plotFFTSignal(eeg_data, label)

    def plotFFTSignal(self, eeg_data, label):
        figure, ax = plt.subplots(9)
        axRaw, axNorm, axFFT, axLogFFT, axChan = ax[0], ax[1], ax[2], ax[3], ax[4:]
        
        fft_util = FFTUtil()
        signal_util = SignalUtil()
        sampFreq = eeg_data.getSampleRate()
        raw = eeg_data.getColumn(label, 0, 1024)
        
        timeArray = np.arange(0, len(raw), 1)
        timeArray = timeArray / sampFreq
        timeArray = timeArray * 1000  #scale to milliseconds
        axRaw.plot(timeArray, raw, color='k')

        axNorm.plot(timeArray, signal_util.normalize(raw), color='k')

        axRaw.set_ylabel('Amplitude')
        axRaw.set_xlabel('Time (ms)')

        fft = fft_util.fft(raw)
        n = float(len(raw))
        nUniquePts = np.ceil((n+1)/2.0)
        
        freqArray = np.arange(0, nUniquePts, 1.0) * (sampFreq / n);

        axFFT.plot(freqArray, fft, color='k')
        axFFT.set_xlabel('Frequency (Hz)')
        axFFT.set_ylabel('Power (dB)')
        
        axLogFFT.plot(freqArray, 10*np.log10(fft), color='k')
        axLogFFT.set_xlabel('Frequency (Hz)')
        axLogFFT.set_ylabel('LOG Power (dB)')

        # print channels
        for i, (label, freqRange) in enumerate(EEGUtil.channel_ranges.iteritems()):
            self.plotEEGChannel(fft, label, freqRange, axChan[i])

            
        plt.show()
        
    def plotEEGChannel(self, fft, channel, freqRange, axChan):
        eeg_util = EEGUtil()
        channels = eeg_util.getChannels(fft)
        axChan.plot(range(*freqRange), channels[channel], color='k')
        axChan.set_xlabel('Frequency (Hz)')
        axChan.set_ylabel(channel)

if __name__ == "__main__":
    eeg_data = EEGTableReader().readFile("util/example_full.csv")
    util = FFTUtil()
    eutil = EEGUtil()

    raw = eeg_data.getColumn("F7", 0, 32)
    fft = util.fft(raw)
    
    e = EEGSignalPlotter()
    

    #labels = eeg_data.header
    #e.plotRawSignal(eeg_data, ["F7", "F8"])
    e.plotFFTSignals(eeg_data, ["F7"])


