#!/usr/bin/python

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import matplotlib.pyplot as plt

from util.eeg_table_util import EEGTableFileUtil
from util.fft_util import FFTUtil
from util.eeg_util import EEGUtil
from util.signal_util import SignalUtil

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
        
        samplingRate = eeg_data.getSamplingRate()
        raw = eeg_data.getColumn(label)
        
        # doPlot raw and normalized signal
        self.plotRaw(axRaw, axNorm, samplingRate, raw)


        raw = SignalUtil().normalize(raw)     # normalize from -1 to 1

        fft = FFTUtil().fft(raw)
        # doPlot FFT with normal and LOG scale
        self.plotFFT(axFFT, axLogFFT, samplingRate, raw, fft)

        # doPlot channels
        #for i, (label, freqRange) in enumerate(EEGUtil.channel_ranges.iteritems()):
        #    self.plotEEGChannel(fft, label, freqRange, axChan[i])
        
        # doPlot channels
        for i, (label, freqRange) in enumerate(EEGUtil.channel_ranges.iteritems()):
            self.plotEEGChannel2(raw, freqRange, eeg_data.getSamplingRate(), axChan[i])


        self.configureFigure()     
        
        plt.show()
        

    def getTimeArray(self, n, samplingRate):
        timeArray = np.arange(0, n, 1)
        timeArray = timeArray / samplingRate
        timeArray = timeArray * 1000 #scale to milliseconds
        return timeArray

    def plotRaw(self, axRaw, axNorm, samplingRate, raw):
        timeArray = self.getTimeArray(len(raw), samplingRate)
        axRaw.plot(timeArray, raw)
        axNorm.plot(timeArray, SignalUtil().normalize(raw), color='k')

        axRaw.set_ylabel('Amplitude')
        axRaw.set_xlabel('Time (ms)')
        return timeArray


    def plotFFT(self, axFFT, axLogFFT, samplingRate, raw, fft):
        n = float(len(raw))
        nUniquePts = np.ceil((n + 1) / 2.0)
        freqArray = np.arange(0, nUniquePts, 1.0) * (samplingRate / n)
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
        
    def plotEEGChannel2(self, raw, freqRange, samplingRate, axChan):
        timeArray = self.getTimeArray(len(raw), samplingRate)
        filtered = SignalUtil().butterBandpassFilter(raw, freqRange[0], freqRange[1],  samplingRate)
        axChan.plot(timeArray, filtered, color='k')
        axChan.set_xlabel('Frequency (Hz)')
        axChan.set_ylabel(freqRange)

if __name__ == "__main__":
    scriptPath = os.path.dirname(os.path.abspath(__file__))
    eegPath = scriptPath + "/../../examples/"
    fileName = "example_4096.csv"
    #fileName = "co2a0000364.rd.018.csv"
    eegData = EEGTableFileUtil().readFile(eegPath + fileName)

    e = EEGSignalPlotter()
    #e.plotRawSignal(eeg_data, ["F7", "F8"])
    e.plotFFTSignals(eegData, ["F4"])


