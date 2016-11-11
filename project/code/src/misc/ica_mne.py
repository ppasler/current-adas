# found at: http://martinos.org/mne/dev/auto_tutorials/plot_ica_from_raw.html
"""
.. _tut_preprocessing_ica:

Compute ICA on MEG data and remove artifacts
============================================

ICA is fit to MEG raw data.
The sources matching the ECG and EOG are automatically found and displayed.
Subsequently, artifact detection and rejection quality are assessed.
"""
# Authors: Denis Engemann <denis.engemann@gmail.com>
#          Alexandre Gramfort <alexandre.gramfort@telecom-paristech.fr>
#
# License: BSD (3-clause)

import os

import mne
from mne.datasets import sample
from mne.preprocessing import ICA
from mne.preprocessing import create_ecg_epochs, create_eog_epochs

import numpy as np
from util.eeg_table_util import EEGTableFileUtil
from util.mne_util import MNEUtil


###############################################################################
# read and prepare raw data
def createInfo(filePath):
    with open(filePath, 'rb') as f:
        ch_names = f.readline().strip().split(",")
    ch_types = ["eeg"] * len(ch_names)
    sfreq = 128
    montage = mne.channels.read_montage("standard_1020")
    info = mne.create_info(ch_names, sfreq, ch_types, montage)
    return info

def createRawObject(filePath):
    info = createInfo(filePath)
    data = np.swapaxes(np.delete(np.genfromtxt(filePath, dtype=float, delimiter=","), 0, 0),0,1)
    return mne.io.RawArray(data, info)

filePath = "test_data.txt"
raw = createRawObject(filePath)
raw.filter(1, 45, n_jobs=1, l_trans_bandwidth=0.5, h_trans_bandwidth=0.5,
           filter_length='10s', phase='zero-double')


####################################


n_components = 14# 0.99  # if float, select n_components by explained variance of PCA
method = 'fastica'  # for comparison with EEGLAB try "extended-infomax" here
decim = 3  # we need sufficient statistics, not all time points -> saves time
picks = mne.pick_types(raw.info, meg=False, eeg=True, eog=False,
                       stim=False, exclude='bads')

ica = ICA(n_components=n_components, method=method, verbose=True)


reject = dict(eeg=400)

ica.fit(raw, picks=picks, decim=decim, verbose=True, reject=reject)


####################################

def plotICA():
    ica.plot_components()
    
    # Let's take a closer look at properties of first three independent components.
    
    # first, component 0:
    ica.plot_properties(raw, picks=0)
    
    # we can see that the data were filtered so the spectrum plot is not
    # very informative, let's change that:
    ica.plot_properties(raw, picks=0, psd_args={'fmax': 35.})
    
    # we can also take a look at multiple different components at once:
    ica.plot_properties(raw, picks=[1, 2], psd_args={'fmax': 35.})

print(ica)
#plotICA()

def findEOG():
    ch_name = "AF3"
    eog_average = create_eog_epochs(raw, reject=reject, ch_name=ch_name, picks=picks).average()
    
    eog_epochs = create_eog_epochs(raw, ch_name=ch_name, reject=reject)  # get single EOG trials
    eog_inds, scores = ica.find_bads_eog(eog_epochs, ch_name=ch_name)  # find via correlation

    ica.plot_scores(scores, exclude=eog_inds)  # look at r scores of components
    # we can see that only one component is highly correlated and that this
    # component got detected by our correlation analysis (red).
    
    ica.plot_sources(eog_average, exclude=eog_inds)  # look at source time course

    ica.plot_properties(eog_epochs, picks=eog_inds, psd_args={'fmax': 35.},
                        image_args={'sigma': 1.})

    print(ica.labels_)

    ica.plot_overlay(eog_average, exclude=eog_inds, show=False)

    ica.exclude.extend(eog_inds)

#findEOG()

def findCorrmap():
    subjects = ["nati", "janis", "gregor", "gerald"]
    
    icas_from_other_data = list()
    for sub in subjects:
        raw = createRawObject(sub + ".csv")
        raw.filter(1, 45, n_jobs=1, l_trans_bandwidth=0.5, h_trans_bandwidth=0.5,
           filter_length='10s', phase='zero-double')
        print('fitting ICA for {0}'.format(sub))
        this_ica = ICA(n_components=n_components, method=method).fit(raw, picks=picks, reject=reject)
        print(this_ica)
        icas_from_other_data.append(this_ica)

findCorrmap()
