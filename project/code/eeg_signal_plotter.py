#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from util.eeg_table_reader import EEGTableReader
from util.fft_util import FFTUtil


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

    def plotFFTSignal(self, eeg_data, labels):
        ret = plt.subplots(len(labels)*2)
        figure = ret[0]
        axis = ret[1]
        
        fft_util = FFTUtil()
        sampFreq = eeg_data.getSampleRate()

        for i, label in enumerate(labels):
            axRaw = axis[i*2]
            axFFT = axis[i*2+1]
            
            raw = eeg_data.getColumn(label, 0, 1024)
            
            timeArray = np.arange(0, len(raw), 1)
            timeArray = timeArray / sampFreq
            timeArray = timeArray * 1000  #scale to milliseconds
            axRaw.plot(timeArray, raw, color='k')
            axRaw.set_ylabel('Amplitude')
            axRaw.set_xlabel('Time (ms)')

            fft = fft_util.fft(raw)
            n = float(len(raw))
            nUniquePts = np.ceil((n+1)/2.0)
            
            freqArray = np.arange(0, nUniquePts, 1.0) * (sampFreq / n);
            axFFT.plot(freqArray/1000, 10*np.log10(fft), color='k')
            axFFT.set_xlabel('Frequency (kHz)')
            axFFT.set_ylabel('Power (dB)')
            
        plt.show()

if __name__ == "__main__":
    eeg_data = EEGTableReader().readFile("util/example_full.csv")
    print eeg_data.getSampleRate()
    util = FFTUtil()
    
    e = EEGSignalPlotter()
    

    #labels = eeg_data.header
    #e.plotRawSignal(eeg_data, ["F7", "F8"])
    e.plotFFTSignal(eeg_data, ["F7", "F8"])


