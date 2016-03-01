#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from util.eeg_table_reader import EEGTableReader

counter = 211

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
        ret = plt.subplots(len(labels)*2, sharex=True)

        figure = ret[0]
        axis = ret[1]
        
        for i, label in enumerate(labels):
            data = eeg_data.getColumn(label, 1000, 1048)
            self.plotLine(data, axis[i*2], label)
            self.plotLine(np.fft.fft(data), axis[i*2+1], "FFT: " + label)

        plt.show()

if __name__ == "__main__":
    eeg_data = EEGTableReader().readFile("util/example_full.csv")
    
    e = EEGSignalPlotter()

    labels = eeg_data.header
    #e.plotRawSignal(eeg_data, ["F7", "F8"])
    e.plotFFTSignal(eeg_data, ["F7", "F8"])

