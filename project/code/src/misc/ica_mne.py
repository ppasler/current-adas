#!/usr/bin/env python -W ignore::DeprecationWarning
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
from mne.preprocessing.ica import corrmap

import numpy as np
import matplotlib.pyplot as plt
from mne.viz.utils import plt_show
from util.mne_util import MNEUtil

def main():
    util = MNEUtil()
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
    
    def createPicks(raw):
        return mne.pick_types(raw.info, meg=False, eeg=True, eog=False,
                           stim=False, exclude='bads')
    
    n_components = 14# 0.99  # if float, select n_components by explained variance of PCA
    method = 'fastica'  # for comparison with EEGLAB try "extended-infomax" here
    decim = 3  # we need sufficient statistics, not all time points -> saves time
    filter_length = "5s"
    reject = dict(eeg=300)
    
    def plotICA(ica, raw):
        ica.plot_components()
        
        ica.plot_properties(raw, picks=0)
        
        # we can see that the data were filtered so the spectrum plot is not
        # very informative, let's change that:
        ica.plot_properties(raw, picks=0, psd_args={'fmax': 35.})
        
        # we can also take a look at multiple different components at once:
        ica.plot_properties(raw, picks=[1, 2], psd_args={'fmax': 35.})
    
    subjects = ["nati", "janis", "gregor", "gerald"]
    
    def findCorrmap():
        icas_from_other_data = list()
        raw_from_other_data = list()
        for sub in subjects:
            raw = createRawObject(sub + ".csv")
            util.filterData(raw, 1, 45)
            print('fitting ICA for {0}'.format(sub))
            picks = util.createPicks(raw)
            this_ica = util.ICA(raw)
            raw_from_other_data.append(raw)
            icas_from_other_data.append(this_ica)
    
        return icas_from_other_data, raw_from_other_data
    
    icas, raws = findCorrmap()
    
    
    ###############################################################################
    # Now we can do the corrmap.

    #for i in range(len(icas)):
    #    for j in range(n_components):
    #        template = (i, j)
    #        fig_template, fig_detected = corrmap(icas, template=template, label="blinks",
    #                                         show=False, ch_type='eeg', verbose=True)
    #        print i, j, fig_template, fig_detected
    def compICAs(icas):
        templates = [#(0, 4), (0, 8), (1, 6), (1, 11), 
                     (2, 1)#, (2, 6), (3, 11)
                    ]
        for template in templates:
            templateICA = icas[template[0]]
            icas.remove(templateICA)
            templateIC = template[1]
            label = "blinks"
            fig_template, fig_detected = util.labelArtefact(templateICA, templateIC, icas, label)
    
            print template, fig_template, fig_detected
        plt.show()

    def plotICAs(icas):
        for i in range(len(icas)):
            #art = icas[i].labels_["blinks"][0]
            #print art
            icas[i].plot_sources(raws[i], show=False)
            
        #icas[i].plot_components(picks=range(10), inst=raws[i])
        plt_show()

    compICAs(icas)
    

    

if __name__ == "__main__":
    main()
