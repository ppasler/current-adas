'''
seen at: `ButterworthBandpass <https://scipy.github.io/old-wiki/pages/Cookbook/ButterworthBandpass>`_
'''
import sys, os

from scipy.signal import freqz
from scipy.io import wavfile
from pylab import arange

import matplotlib.pyplot as plt
import numpy as np
from util.file_util import FileUtil

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from util.eeg_util import EEGUtil
from util.signal_util import SignalUtil


class BandPassExample(object):
    
    def __init__(self):
        self.su = SignalUtil()
    
    def getSignal(self, a, t, f0):
        x = 0.1 * np.sin(2 * np.pi * 1.2 * np.sqrt(t))
        x += 0.01 * np.cos(2 * np.pi * 312 * t + 0.1)
        x += a * np.cos(2 * np.pi * f0 * t + .11)
        x += 0.03 * np.cos(2 * np.pi * 2000 * t)
        return x
    
    def getEEGSignal(self):
        scriptPath = os.path.dirname(os.path.abspath(__file__))
        return FileUtil().getDto(scriptPath + "/../../examples/example_1024.csv")
    
    def plotBBF(self, fs, lowcut, highcut):
        # Plot the frequency response for a few different orders.
        plt.figure(1)
        plt.clf()
        for order in [2, 4, 8]:
            b, a = self.su.butterBandpass(lowcut, highcut, fs, order=order)
            w, h = freqz(b, a, worN=2000)
            plt.plot((fs * 0.5 / np.pi) * w, abs(h), label="order = %d" % order)
        
        plt.plot([0, 0.5 * fs], [np.sqrt(0.5), np.sqrt(0.5)], '--', label='sqrt(0.5)')
        plt.xlabel('Frequency (Hz)')
        plt.ylabel('Gain')
        plt.grid(True)
        plt.legend(loc='best')
    
    
    def getDuration(self, data):
        time = data.getColumn("Timestamp")
        duration = time[len(time) - 1] - time[0]
        return duration
    
    def plotEEGSignal(self):
        # Filter a noisy signal.
        
        data = self.getEEGSignal()
        fs = data.getSamplingRate();
        x = data.getColumn("F3")
        x = SignalUtil().normalize(x)
        
        duration = self.getDuration(data)
        t = np.linspace(0, duration, len(x), endpoint=False)
    
        plt.figure(2)
        plt.clf()
        plt.plot(t, x, label='normalized signal')
        
        for label, (lowcut, highcut) in EEGUtil().channel_ranges.iteritems():
            if label == "alpha":
                y = self.su.butterBandpassFilter(x, lowcut, highcut, fs, order=6)
                plt.plot(t, y, label='%s (%d - %dHz)' % (label, lowcut, highcut))
    
        plt.xlabel('time (seconds)')
        plt.grid(True)
        plt.axis('tight')
        plt.legend(loc='upper left')
    
    def plotSoundSignal(self):
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
        
        y = self.su.butterBandpassFilter(s1, 11000, 13000, fs, order=6)
        #wavfile.write(path + '12000hz_cut.wav', fs, y)
    
        plt.plot(t, y, label='%s (%d - %dHz)' % ("12000Hz", 11000, 13000))
    
        plt.xlabel('time (seconds)')
        plt.grid(True)
        plt.axis('tight')
        plt.legend(loc='upper left')
    
    
    def plotSignal(self, fs, lowcut, highcut):
        # Filter a noisy signal.
        T = 0.05
        nsamples = T * fs
        t = np.linspace(0, T, nsamples, endpoint=False)
        a = 0.02
        f0 = 600.0 # frequency
        x = self.getSignal(a, t, f0)
        
        plt.figure(2)
        plt.clf()
        plt.plot(t, x, label='Noisy signal')
        y = self.butterBandpassFilter(x, lowcut, highcut, fs, order=6)
        plt.plot(t, y, label='Filtered signal (%g Hz)' % f0)
        plt.xlabel('time (seconds)')
        plt.hlines([-a, a], 0, T, linestyles='--')
        plt.grid(True)
        plt.axis('tight')
        plt.legend(loc='upper left')
    
    def main(self):
        # Sample rate and desired cutoff frequencies (in Hz).
        fs = 5000.0
        lowcut = 500.0
        highcut = 1250.0
    
        self.plotBBF(fs, lowcut, highcut)
    
        #self.plotSignal(fs, lowcut, highcut)
        self.plotEEGSignal()
        #self.plotSoundSignal()
        
        plt.show()

if __name__ == "__main__":
    band = BandPassExample().main()
