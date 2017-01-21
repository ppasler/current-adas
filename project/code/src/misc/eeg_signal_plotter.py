#!/usr/bin/python

import sys, os

import matplotlib.pyplot as plt
import numpy as np
from util.eeg_util import EEGUtil
from util.fft_util import FFTUtil
from util.file_util import FileUtil
from util.signal_util import SignalUtil


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))



class EEGSignalPlotter(object):

    def __init__(self):
        """This class plots EEG signals"""

    def plotFFTSignals(self, eeg_data, labels, fileName):
        for label in labels:
            self.plotFFTSignal(eeg_data, label, fileName)

        plt.show()


    def configureFigure(self):
        #http://stackoverflow.com/questions/12439588/how-to-maximize-a-plt-show-collector-using-python
        mng = plt.get_current_fig_manager()
        mng.resize(*mng.window.maxsize())
        mng.window.wm_geometry("+0+0")
        
        #http://stackoverflow.com/questions/6541123/improve-subplot-size-spacing-with-many-subplots-in-matplotlib
        plt.subplots_adjust(left=0.09, right=0.95, bottom=0.05, top=0.95, wspace=0.2, hspace=0.5)

    def plotFFTSignal(self, eeg_data, label, fileName):
        #http://stackoverflow.com/questions/332289/how-do-you-change-the-size-of-figures-drawn-with-matplotlib
        fig, ax = plt.subplots(7, figsize=(16, 9))
        fig.canvas.set_window_title(fileName + "-Channel " + label)
        axRaw, axLogFFT, axChan = ax[0], ax[1], ax[2:]
        
        samplingRate = eeg_data.getSamplingRate()
        raw = eeg_data.getColumn(label)
        
        # doPlot raw and normalized signal
        self.plotRaw(axRaw, samplingRate, raw)


        raw = SignalUtil().normalize(raw)     # normalize from -1 to 1

        fft = FFTUtil().fft(raw)
        # doPlot FFT with normal and LOG scale
        self.plotFFT(axLogFFT, samplingRate, raw, fft)
        # doPlot channels
        for i, (label, freqRange) in enumerate(EEGUtil.channel_ranges.iteritems()):
            self.plotEEGChannel(raw, label, freqRange, eeg_data.getSamplingRate(), axChan[i])

        self.configureFigure()     

    def getTimeArray(self, n, samplingRate):
        timeArray = np.arange(0, n, 1)
        timeArray = timeArray / samplingRate
        timeArray = timeArray * 1000 #scale to milliseconds
        return timeArray

    def plotRaw(self, axRaw, samplingRate, raw):
        timeArray = self.getTimeArray(len(raw), samplingRate)
        axRaw.plot(timeArray, raw)

        axRaw.set_ylabel('Amplitude')
        axRaw.set_xlabel('Time (ms)')
        return timeArray


    def plotFFT(self, axLogFFT, samplingRate, raw, fft):
        n = float(len(raw))
        nUniquePts = np.ceil((n + 1) / 2.0)
        freqArray = np.arange(0, nUniquePts, 1.0) * (samplingRate / n)
        axLogFFT.plot(freqArray, 10 * np.log10(fft), color='k')
        axLogFFT.set_xlabel('Frequency (Hz)')
        axLogFFT.set_ylabel('LOG Power (dB)')

    def plotEEGChannel(self, raw, label, freqRange, samplingRate, axChan):
        timeArray = self.getTimeArray(len(raw), samplingRate)
        filtered = SignalUtil().butterBandpassFilter(raw, freqRange[0], freqRange[1],  samplingRate)
        axChan.plot(timeArray, filtered, color='k')
        axChan.set_xlabel('Frequency (Hz)')
        axChan.set_ylabel(label + str(freqRange))

def readEEGFile(fileName):
    eegPath = "E:/thesis/experiment/"

    return FileUtil().getDto(eegPath + fileName)

def plot(fileName, channels):
    eegData = readEEGFile(fileName)
    e = EEGSignalPlotter()
    e.plotFFTSignals(eegData, channels, fileName)

def plotBlink():
    channels = ["FC5", "FC6", "F8", "F7", "AF4", "AF3", "F4"]
    fileName = "blink_EEG.csv"
    plot(fileName, channels)

def plotLeftRight():
    channels = ["FC5", "FC6", "F8", "F7", "AF4", "AF3", "F4"]
    fileName = "left-right-slow.csv"
    plot(fileName, channels)

def plotCloseOpen():
    channels = ["FC5", "FC6", "F8", "F7", "AF4", "AF3", "F4"]
    fileName = "close-open.csv"
    plot(fileName, channels)

if __name__ == "__main__":
    channels = ["FC5", "FC6", "F8", "F7", "AF4", "AF3", "F4"]
    plot("3/EEG.csv", channels)


