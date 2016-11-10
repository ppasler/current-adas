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
# Setup paths and prepare raw data

PATH = os.path.dirname(os.path.abspath(__file__)) +  "/../../../captured_data/test_data/"
eegDto = EEGTableFileUtil().readFile(PATH + "awake_full.csv")
raw = MNEUtil().createMNEObjectFromDto(eegDto)

###############################################################################
# 1) Fit ICA model using the FastICA algorithm

# Other available choices are `infomax` or `extended-infomax`
# We pass a float value between 0 and 1 to select n_components based on the
# percentage of variance explained by the PCA components.

ica = ICA(n_components=0.95, method='fastica', verbose=True)

picks = mne.pick_types(raw.info, meg=False, eeg=True, eog=False,
                       stim=False, exclude='bads')

ica.fit(raw, picks=picks, decim=3)#, reject=dict(eeg=40e-6, mag=4e-12, grad=4000e-13))

# maximum number of components to reject
n_max_ecg, n_max_eog = 3, 1  # here we don't expect horizontal EOG components

###############################################################################
# 2) identify bad components by analyzing latent sources.

title = 'Sources related to %s artifacts (red)'
# generate ECG epochs use detection via phase statistics

# ecg_epochs = create_ecg_epochs(raw, tmin=-.5, tmax=.5, picks=picks)

# ecg_inds, scores = ica.find_bads_ecg(ecg_epochs, method='ctps')
# ica.plot_scores(scores, exclude=ecg_inds, title=title % 'ecg', labels='ecg')

# show_picks = np.abs(scores).argsort()[::-1][:5]

# ica.plot_sources(raw, show_picks, exclude=ecg_inds, title=title % 'ecg')
# ica.plot_components(ecg_inds, title=title % 'ecg', colorbar=True)

# ecg_inds = ecg_inds[:n_max_ecg]
# ica.exclude += ecg_inds

# detect EOG by correlation

ch_name = "F3" # ["AF3", "AF4"]
eog_inds, scores = ica.find_bads_eog(raw, ch_name=ch_name, verbose=True)
ica.plot_scores(scores, exclude=eog_inds, title=title % 'eog', labels='eog')

show_picks = np.abs(scores).argsort()[::-1][:5]

ica.plot_sources(raw, show_picks, exclude=eog_inds, title=title % 'eog')
ica.plot_components(eog_inds, title=title % 'eog', colorbar=True)

eog_inds = eog_inds[:n_max_eog]
ica.exclude += eog_inds

###############################################################################
# 3) Assess component selection and unmixing quality

# estimate average artifact
# ecg_evoked = ecg_epochs.average()
# ica.plot_sources(ecg_evoked, exclude=ecg_inds)  # plot ECG sources + selection
# ica.plot_overlay(ecg_evoked, exclude=ecg_inds)  # plot ECG cleaning

eog_evoked = create_eog_epochs(raw, tmin=-.5, tmax=.5, picks=picks).average()
ica.plot_sources(eog_evoked, exclude=eog_inds)  # plot EOG sources + selection
ica.plot_overlay(eog_evoked, exclude=eog_inds)  # plot EOG cleaning

# check the amplitudes do not change
ica.plot_overlay(raw)  # EOG artifacts remain

###############################################################################

# To save an ICA solution you can say:
# ica.save('my_ica.fif')

# You can later load the solution by saying:
# from mne.preprocessing import read_ica
# read_ica('my_ica.fif')

# Apply the solution to Raw, Epochs or Evoked like this:
# ica.apply(epochs)
