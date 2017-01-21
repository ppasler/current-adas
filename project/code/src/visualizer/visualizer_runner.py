#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 21.01.2017

:author: Paul Pasler
:organization: Reutlingen University
'''

import sys

from PyQt4 import QtGui

from config.config import ConfigProvider
from visualizer import DataVisualizer


EXPERIMENT_PATH = "E:/thesis/experiment/"

def runWithProband(proband):
    probands = ConfigProvider().getExperimentConfig().get("probands")
    files = ["drive.mp4", "face.mp4", "EEG.raw.fif"]
    #dataUrls = ['../../examples/example_4096.csv']

    url = EXPERIMENT_PATH + str(proband) + "/"
    videoUrls = [url+files[0], url+files[1]]
    dataUrls = [url+files[2]]
    return videoUrls, dataUrls

def main():
    app = QtGui.QApplication(sys.argv)
    
    videoUrls, dataUrls = runWithProband(1)

    vis = DataVisualizer(None, videoUrls, dataUrls)
    vis.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()