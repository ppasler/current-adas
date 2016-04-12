#!/usr/bin/python

import numpy as np
import matplotlib.pyplot as plt

from util.eeg_table_reader import EEGTableReader
from util.fft_util import FFTUtil
from util.eeg_util import EEGUtil
from util.signal_util import SignalUtil

import os.path

class EEGSignalPlotter(object):

    def __init__(self):
        """This class plots EEG signals"""

    def plotFFTSignals(self, eeg_data, labels):
        for label in labels:
            self.plotFFTSignal(eeg_data, label)


    def configureFigure(self):
        #http://stackoverflow.com/questions/12439588/how-to-maximize-a-plt-show-window-using-python
        mng = plt.get_current_fig_manager()
        #mng.resize(*mng.window.maxsize())
        mng.window.wm_geometry("+0+0")
        
        #http://stackoverflow.com/questions/6541123/improve-subplot-size-spacing-with-many-subplots-in-matplotlib
        plt.subplots_adjust(left=0.09, right=0.95, bottom=0.05, top=0.95, wspace=0.2, hspace=0.5)

    def plotFFTSignal(self, eeg_data, label):
        #http://stackoverflow.com/questions/332289/how-do-you-change-the-size-of-figures-drawn-with-matplotlib
        _, ax = plt.subplots(9, figsize=(16, 9))
        axRaw, axNorm, axFFT, axLogFFT, axChan = ax[0], ax[1], ax[2], ax[3], ax[4:]
        
        sampFreq = eeg_data.getSampleRate()
        raw = eeg_data.getColumn(label, 0, 1024)
        
        # plot raw and normalized signal
        self.plotRaw(axRaw, axNorm, sampFreq, raw)


        raw = SignalUtil().normalize(raw)     # normalize from -1 to 1

        fft = FFTUtil().fft(raw)
        # plot FFT with normal and LOG scale
        self.plotFFT(axFFT, axLogFFT, sampFreq, raw, fft)

        # plot channels
        for i, (label, freqRange) in enumerate(EEGUtil.channel_ranges.iteritems()):
            self.plotEEGChannel(fft, label, freqRange, axChan[i])


        self.configureFigure()     
        
        plt.show()
        

    def plotRaw(self, axRaw, axNorm, sampFreq, raw):
        timeArray = np.arange(0, len(raw), 1)
        timeArray = timeArray / sampFreq
        timeArray = timeArray * 1000 #scale to milliseconds
        axRaw.plot(timeArray, raw)
        axNorm.plot(timeArray, SignalUtil().normalize(raw), color='k')

        axRaw.set_ylabel('Amplitude')
        axRaw.set_xlabel('Time (ms)')
        return timeArray


    def plotFFT(self, axFFT, axLogFFT, sampFreq, raw, fft):
        n = float(len(raw))
        nUniquePts = np.ceil((n + 1) / 2.0)
        freqArray = np.arange(0, nUniquePts, 1.0) * (sampFreq / n)
        axFFT.plot(freqArray, fft, color='k')
        axFFT.set_xlabel('Frequency (Hz)')
        axFFT.set_ylabel('Power (dB)')
        axLogFFT.plot(freqArray, 10 * np.log10(fft), color='k')
        axLogFFT.set_xlabel('Frequency (Hz)')
        axLogFFT.set_ylabel('LOG Power (dB)')
        
    def plotEEGChannel(self, fft, channel, freqRange, axChan):
        eeg_util = EEGUtil()
        channels = eeg_util.getChannels(fft)
        axChan.plot(range(*freqRange), channels[channel], color='k')
        axChan.set_xlabel('Frequency (Hz)')
        axChan.set_ylabel(channel)

if __name__ == "__main__":
    scriptPath = os.path.dirname(os.path.abspath(__file__))
    eegPath = scriptPath + "/../examples/example_4096.csv"
    eegData = EEGTableReader().readFile(eegPath)
    util = FFTUtil()
    eutil = EEGUtil()

    raw = eegData.getColumn("F7", 0, 32)
    fft = util.fft(raw)
    
    e = EEGSignalPlotter()
    

    #labels = eeg_data.header
    #e.plotRawSignal(eeg_data, ["F7", "F8"])
    e.plotFFTSignals(eegData, ["F7"])


