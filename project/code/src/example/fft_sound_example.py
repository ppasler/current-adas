'''
Shows simple sound processing with fft

Inspired by `Basic Sound Processing with Python <http://samcarcagno.altervista.org/blog/basic-sound-processing-python/>`_
'''

from pylab import fft, arange, log10, ceil
from scipy.io import wavfile
from matplotlib.pyplot import ylabel, xlabel, subplots, show
from util.fft_util import FFTUtil
import numpy as np


def getFFT(s1, n):
    p = fft(s1) # take the fourier transform
    print p
    nUniquePts = ceil((n + 1) / 2.0)
    p = p[0:nUniquePts]
    print p
    p = abs(p)
    p = p / n # scale by the number of points so that
    # the magnitude does not depend on the length
    # of the signal or on its sampling frequency
    p = p ** 2 # square it to get the power
# multiply by two (see technical document for details)
# odd nfft excludes Nyquist point
    print p
    if n % 2 > 0: # we've got odd number of points fft
        p[1:len(p)] = p[1:len(p)] * 2
    else:
        p[1:len(p) - 1] = p[1:len(p) - 1] * 2 # we've got even number of points fft
    return nUniquePts, p

def getFFTUtil(s1, n):
    nUniquePts = ceil((n + 1) / 2.0)
    
    return nUniquePts, FFTUtil().fft(s1)


def main():

    path = "../../examples/"
    #sampFreq, s1 = wavfile.read(path + '440_sine.wav')
    sampFreq, s1 = wavfile.read(path + '12000hz.wav')
    
    if len(s1.shape) == 2:
        s1 = s1[:,0]
    
    #if len(s1) > 8192:
    #    s1 = s1[:16384]
    
    print repr(s1)
    n = float(len(s1))
    
    print "DType %s" % s1.dtype
    print "Sound File Shape " + str(s1.shape)
    print "Sample Frequency / Entries: %.2f / %.2f" % (sampFreq, n)
    print "Duration %.2f ms" % ((n / sampFreq)*1000)
    
    s1 = s1 / (2.**15)
    # Plotting the Tone
    timeArray = arange(0, n, 1)
    timeArray = timeArray / sampFreq
    timeArray = timeArray * 1000  #scale to milliseconds
    
    _, (axTone, axFreq, axLogFreq) = subplots(3)
    axTone.plot(timeArray, s1, color='k')
    ylabel('Amplitude')
    xlabel('Time (ms)')
    
    
    #Plotting the Frequency Content
    nUniquePts, p = getFFT(s1, n)
    #nUniquePts, p = getFFTUtil(s1, n)
    
    freqArray = arange(0, nUniquePts, 1.0) * (sampFreq / n);
    
    print "FreqMax %fHz" % freqArray[np.argmax(p)]
    
    axFreq.plot(freqArray/1000, p, color='k')
    axLogFreq.plot(freqArray/1000, 10*log10(p), color='k')
    
    
    xlabel('Frequency (kHz)')
    ylabel('Power (dB)')
    show()
    
if __name__ == "__main__":
    main()
