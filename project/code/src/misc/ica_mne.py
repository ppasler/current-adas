#!/usr/bin/env python -W ignore::DeprecationWarning
# based on: http://martinos.org/mne/dev/auto_tutorials/plot_ica_from_raw.html

import os
import time

import mne
from mne.viz.utils import plt_show
import numpy as np
from util.mne_util import MNEUtil


scriptPath = os.path.dirname(os.path.abspath(__file__))

def main():
    util = MNEUtil()

    def createRawObject(filePath):
        with open(filePath, 'rb') as f:
            ch_names = f.readline().strip().split(",")
        info = util._createEEGInfo(ch_names, filePath, 128)
        data = np.swapaxes(np.delete(np.genfromtxt(filePath, dtype=float, delimiter=","), 0, 0),0,1)
        return mne.io.RawArray(data, info)

    def createICA(fileName):
        start = time.time()
        raw = createRawObject(fileName)
        util.filterData(raw, 1, 45)
        ica = util.ICA(raw)
        print("create raw and ica in %.2fs for %s" % (time.time()-start, fileName))

        return raw, ica

    def plotICA(raw, ica):
        ica.plot_components(inst=raw, colorbar=True, show=False, picks=[0, 1, 2, 3])
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

    def excludeAndPlotRaw(raw, ica, exclude, title):
        raw1 = raw.copy()
        eog = ica.apply(raw1, exclude=exclude)
        eog.plot(show=False, scalings=dict(eeg=300), title=title)

    def plotSignal(raw, ica):
        filename = raw.info["filename"]
        raw.plot(show=False, title="%s: Raw data" % filename, scalings=dict(eeg=300))
        #eogInd = ica.labels_["blinks"]
        #withoutEogInds = range(14)
        #withoutEogInds.remove(eogInd[0])
        #excludeAndPlotRaw(raw, ica, eogInd, "%s: Blinks removed" % filename)
        #excludeAndPlotRaw(raw, ica, withoutEogInds, "%s: Only blinks" % filename)

    def plotSignals(templateRaw, templateICA, raws, icas):
        plotSignal(templateRaw, templateICA)
        for i in range(len(icas)):
            plotSignal(raws[i], icas[i])

    # load raw data and calc ICA
    templateRaw, templateICA = createICA(scriptPath + "/blink.csv")

    # plot ICs with topographic info
    plotICA(templateRaw, templateICA)
    plotSignal(templateRaw, templateICA)
    
    # load data from previous experiment and calc ICA
    #raws, icas = createICAList()

    # match blink IC (0) from template with other ICs 
    #_, _ = util.labelArtefact(templateICA, 0, icas, "blinks")

    # print raw, cleaned and eog data
    #plotSignals(templateRaw, templateICA, raws, icas)

    #plt_show()
    print ",".join(templateICA.ch_names)
    for row in templateICA.unmixing_matrix_:
        s = ""
        for c in row:
            s += "%.5f," % c
        print s
    
    print templateICA.get_components()
    print "hello"
if __name__ == "__main__":
    main()
