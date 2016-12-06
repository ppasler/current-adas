"""
.. _tut_creating_fixed_size_epochs:

Creating MNE-Python's fixed size Epochs from scratch
====================================================
"""

from __future__ import print_function

import mne
import numpy as np

###################
# create a dummy :class:`mne.io.RawArray` object

# 4 sample eeg channels
ch_names = ["F3", "F4", "AF3", "AF4"]
# sampling rate 128Hz
sfreq = 128
# create info object
info = mne.create_info(ch_names, sfreq)

# create random data for 4 channels, with 4*128 = 512 values each
data = np.random.rand(4,4*sfreq)
# create a :class:`mne.io.RawArray` object
raw = mne.io.RawArray(data, info)

###################
# create fixed size `epochs` like this
# x x x x|x x x x|x x x x

# This is used to identify the events
class_id = 1

# Every event has the duration of 1 sample (~ sfreq)
duration=1

# create a fixed size events array
# start=0 and stop=None
events = mne.make_fixed_length_events(raw, class_id, duration=duration)
print(events)

# for fixed size events no start time before and after event
tmin=0
# Note: as tmax is inclusive (unlikely `range` for example) tmax=1 will produce events with length 129
tmax = 0.99

# create :class:`Epochs <mne.Epochs>` object
epochs = mne.Epochs(raw, events=events, tmin=tmin, tmax=tmax, verbose=True)

###################
# create overlapping epochs like this
# x x x x|x x x x|x x x x
# x x|x x x x|x x x x|x x

# duration is set 0.5 to create overlapping epochs
overlapping_duration = 0.5

# create fixed size events with `length=sfreq` which starts every `sfreq/2`  
overlapping_events = mne.make_fixed_length_events(raw, class_id, duration=overlapping_duration)
print(overlapping_events)

###################
# .. note:: if `preload=True` this will double your data
epochs = mne.Epochs(raw, events=overlapping_events, tmin=tmin, tmax=tmax, verbose=True)
