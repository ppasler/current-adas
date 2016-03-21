'''
Inspired by http://samcarcagno.altervista.org/blog/basic-sound-processing-python/
'''

from pylab import*
from scipy.io import wavfile

#sampFreq, s1 = wavfile.read('440_sine.wav')
sampFreq, s1 = wavfile.read('12000hz.wav')

if len(s1.shape) == 2:
    s1 = s1[:,0]

if len(s1) > 8192:
    s1 = s1[:128]

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

f, (axTone, axFreq, axLogFreq) = plt.subplots(3)
axTone.plot(timeArray, s1, color='k')
ylabel('Amplitude')
xlabel('Time (ms)')


#Plotting the Frequency Content
p = fft(s1) # take the fourier transform
nUniquePts = ceil((n+1)/2.0)
p = p[0:nUniquePts]
p = abs(p)

p = p / n        # scale by the number of points so that
                 # the magnitude does not depend on the length 
                 # of the signal or on its sampling frequency  
p = p**2  # square it to get the power 
# multiply by two (see technical document for details)
# odd nfft excludes Nyquist point
if n % 2 > 0: # we've got odd number of points fft
    p[1:len(p)] = p[1:len(p)] * 2
else:
    p[1:len(p) -1] = p[1:len(p) - 1] * 2 # we've got even number of points fft

freqArray = arange(0, nUniquePts, 1.0) * (sampFreq / n);


axFreq.plot(freqArray/1000, p, color='k')
axLogFreq.plot(freqArray/1000, 10*log10(p), color='k')


xlabel('Frequency (kHz)')
ylabel('Power (dB)')
show()
