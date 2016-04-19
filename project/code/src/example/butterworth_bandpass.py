'''
seen at: `ButterworthBandpass <https://scipy.github.io/old-wiki/pages/Cookbook/ButterworthBandpass>`_
'''
import sys, os

from scipy.signal import butter, lfilter, filtfilt, freqz
from scipy.io import wavfile
from pylab import fft, arange, log10, ceil

import matplotlib.pyplot as plt
import numpy as np
from util.eeg_table_reader import EEGTableReader
from util.eeg_util import EEGUtil
from util.signal_util import SignalUtil


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))



def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = min(highcut / nyq, 1)
    b, a = butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

def butter_bandpass_filter_2(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = filtfilt(b, a, data)
    return y

def getSignal(a, t, f0):
    x = 0.1 * np.sin(2 * np.pi * 1.2 * np.sqrt(t))
    x += 0.01 * np.cos(2 * np.pi * 312 * t + 0.1)
    x += a * np.cos(2 * np.pi * f0 * t + .11)
    x += 0.03 * np.cos(2 * np.pi * 2000 * t)
    return x

def getEEGSignal():
    scriptPath = os.path.dirname(os.path.abspath(__file__))
    return EEGTableReader().readFile(scriptPath + "/../../examples/example_1024.csv")

def plotBBF(fs, lowcut, highcut):
    # Plot the frequency response for a few different orders.
    plt.figure(1)
    plt.clf()
    for order in [3, 6, 9]:
        b, a = butter_bandpass(lowcut, highcut, fs, order=order)
        w, h = freqz(b, a, worN=2000)
        plt.plot((fs * 0.5 / np.pi) * w, abs(h), label="order = %d" % order)
    
    plt.plot([0, 0.5 * fs], [np.sqrt(0.5), np.sqrt(0.5)], '--', label='sqrt(0.5)')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Gain')
    plt.grid(True)
    plt.legend(loc='best')


def getDuration(data):
    time = data.getColumn("Timestamp")
    duration = time[len(time) - 1] - time[0]
    return duration

def plotEEGSignal():
    # Filter a noisy signal.
    
    data = getEEGSignal()
    fs = data.getSampleRate();
    x = data.getColumn("F3")
    x = SignalUtil().normalize2(x)
    
    duration = getDuration(data)
    t = np.linspace(0, duration, len(x), endpoint=False)

    plt.figure(2)
    plt.clf()
    plt.plot(t, x, label='normalized signal')
    
    for label, (lowcut, highcut) in EEGUtil.channel_ranges.iteritems():
        if label != "gamma":
            y = butter_bandpass_filter(x, lowcut, highcut, fs, order=6)
            plt.plot(t, y, label='%s (%d - %dHz)' % (label, lowcut, highcut))

    plt.xlabel('time (seconds)')
    plt.grid(True)
    plt.axis('tight')
    plt.legend(loc='upper left')

def plotSoundSignal():
    # Filter a noisy signal.
    path = "../../examples/"
    fs, s1 = wavfile.read(path + '12000hz.wav')
   
    if len(s1.shape) == 2:
        s1 = s1[:,0]
    
    n = float(len(s1))

    
    t = arange(0, n, 1)
    t = t / fs
    t = t * 1000  #scale to milliseconds

    plt.figure(2)
    plt.clf()
    plt.plot(t, s1, label='sound signal')
    
    y = butter_bandpass_filter(s1, 1000, 2000, fs, order=6)
    #wavfile.write(path + '12000hz_cut.wav', fs, y)

    plt.plot(t, y, label='%s (%d - %dHz)' % ("12000Hz", 11000, 13000))

    plt.xlabel('time (seconds)')
    plt.grid(True)
    plt.axis('tight')
    plt.legend(loc='upper left')


def plotSignal(fs, lowcut, highcut):
    # Filter a noisy signal.
    T = 0.05
    nsamples = T * fs
    t = np.linspace(0, T, nsamples, endpoint=False)
    print t
    a = 0.02
    f0 = 600.0 # frequency
    x = getSignal(a, t, f0)
    
    plt.figure(2)
    plt.clf()
    plt.plot(t, x, label='Noisy signal')
    y = butter_bandpass_filter(x, lowcut, highcut, fs, order=6)
    plt.plot(t, y, label='Filtered signal (%g Hz)' % f0)
    plt.xlabel('time (seconds)')
    plt.hlines([-a, a], 0, T, linestyles='--')
    plt.grid(True)
    plt.axis('tight')
    plt.legend(loc='upper left')

def main():
# Sample rate and desired cutoff frequencies (in Hz).
    fs = 5000.0
    lowcut = 500.0
    highcut = 1250.0

    #plotBBF(fs, lowcut, highcut)

    #plotSignal(fs, lowcut, highcut)
    #plotEEGSignal()
    plotSoundSignal()
    
    plt.show()

if __name__ == "__main__":
    main()