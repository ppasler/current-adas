#!/usr/bin/env python -W ignore::DeprecationWarning
# based on: http://martinos.org/mne/dev/auto_tutorials/plot_ica_from_raw.html

import os
import time

from mne.viz.utils import plt_show
from util.mne_util import MNEUtil
from config.config import ConfigProvider


scriptPath = os.path.dirname(os.path.abspath(__file__))

def main():
    util = MNEUtil()

    def createICA(fileName):
        start = time.time()
        raw = util.load(fileName)
        #util.bandpassFilterData(raw)
        ica = util.ICA(raw)
        print("create raw and ica in %.2fs for %s" % (time.time()-start, fileName))

        return raw, ica

    def plotICA(raw, ica):
        picks=None
        ica.plot_components(inst=raw, colorbar=True, show=False, picks=picks)
        ica.plot_sources(raw, show=False, picks=picks)
        #ica.plot_properties(raw, picks=0, psd_args={'fmax': 35.})
    
    def createICAList():
        icas_from_other_data = list()
        raw_from_other_data = list()
        probands = ConfigProvider().getExperimentConfig().get("probands")
        for proband in probands:
            raw, ica = createICA("E:/thesis/experiment/" + proband + "/EEG_.raw.fif")
            raw_from_other_data.append(raw)
            icas_from_other_data.append(ica)
    
        return raw_from_other_data, icas_from_other_data

    def excludeAndPlotRaw(raw, ica, exclude, title):
        raw1 = raw.copy()
        eog = ica.apply(raw1, exclude=exclude)
        eog.plot(show=False, scalings=dict(eeg=300), title=title)

    def plotSignal(raw, ica):
        filename = raw.info["description"]
        raw.plot(show=False, title="%s: Raw data" % filename, scalings=dict(eeg=300))
        eogInd = ica.labels_["blinks"]
        withoutEogInds = range(14)
        withoutEogInds.remove(eogInd[0])
        excludeAndPlotRaw(raw, ica, eogInd, "%s: Blinks removed" % filename)
        excludeAndPlotRaw(raw, ica, withoutEogInds, "%s: Only blinks" % filename)

    def plotSignals(templateRaw, templateICA, raws, icas):
        plotSignal(templateRaw, templateICA)
        for i in range(len(icas)):
            plotSignal(raws[i], icas[i])

    # load raw data and calc ICA
    dataPath = scriptPath + "/../../data/"
    files = ["blink"]
    for f in files:
        templateRaw = util.load(dataPath + f + ".raw.fif")
        #util.markBadChannels(templateRaw, ["T7", "P7", "O1", "O2", "P8", "T8"])
        templateICA = util.ICA(templateRaw)
        plotICA(templateRaw, templateICA)
    #    util.saveICA(templateICA, dataPath + f + ".ica.fif")
    
    #util.loadICA(dataPath + "EEG_ic2.ica.fif")
    #templateICA.exclude.extend([2])
    #_, _ = util.labelArtefact(templateICA, 2, icas, "blinks")
    #templateRaw.plot(show=False, scalings=dict(eeg=300), title="raw")

    #excludeAndPlotRaw(templateRaw, templateICA, [0, 2], "eog")
    #plotSignal(templateRaw, templateICA)
    
    # load data from previous experiment and calc ICA
    #raws, icas = createICAList()

    # match blink IC (0) from template with other ICs 

    # print raw, cleaned and eog data
    #plotSignals(templateRaw, templateICA, raws, icas)

    plt_show()
    #print templateICA.get_components()

if __name__ == "__main__":
    main()
