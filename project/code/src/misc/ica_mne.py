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
import time

import mne
from mne.viz.utils import plt_show

import matplotlib.pyplot as plt
import numpy as np
from util.mne_util import MNEUtil


scriptPath = os.path.dirname(os.path.abspath(__file__))

def main():
    util = MNEUtil()

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

    def createICA(fileName):
        start = time.time()
        raw = createRawObject(fileName)
        util.filterData(raw, 1, 45)
        ica = util.ICA(raw)
        print("create raw and ica in %.2fs for %s" % (time.time()-start, fileName))

        return raw, ica

    def plotICA(raw, ica):
        ica.plot_components(inst=raw, colorbar=True, show=False)
        ica.plot_sources(raw, show=False)
        #ica.plot_properties(raw, picks=0, psd_args={'fmax': 35.})
    
    def createICAList():
        icas_from_other_data = list()
        raw_from_other_data = list()
        for sub in range(4):
            raw, ica = createICA(scriptPath + "/" + str(sub) + ".csv")
            raw_from_other_data.append(raw)
            icas_from_other_data.append(ica)
    
        return raw_from_other_data, icas_from_other_data

    #for i in range(len(icas)):
    #    for j in range(n_components):
    #        template = (i, j)
    #        fig_template, fig_detected = corrmap(icas, template=template, label="blinks",
    #                                         show=False, ch_type='eeg', verbose=True)
    #        print i, j, fig_template, fig_detected
    def compICAs(template, icas):
        templates = [#(0, 4), (0, 8), (1, 6), (1, 11), 
                     (2, 1)#, (2, 6), (3, 11)
                    ]
        for template in templates:
            templateICA = icas[template[0]]
            icas.remove(templateICA)
            templateIC = template[1]
            label = "blinks"
            fig_template, fig_detected = util.labelArtefact(template, 0, icas, label)
    
            print template, fig_template, fig_detected
        plt.show()

    templateRaw, templateICA = createICA(scriptPath + "/blink.csv")
    plotICA(templateRaw, templateICA)
    raws, icas = createICAList()
    fig_template, fig_detected = util.labelArtefact(templateICA, 0, icas, "blinks")

    plt_show()
    #compICAs(icas, raws)

if __name__ == "__main__":
    main()
