#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 21.01.2017

:author: Paul Pasler
:organization: Reutlingen University
'''

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
import logging
from PyQt4 import QtGui

from visualizer import DataVisualizer


EXPERIMENT_PATH = "E:/thesis/experiment/%s/"
EXPERIMENT_FILES = ["drive.mp4", "face.mp4", "EEG.raw.fif"]

def runTest(videoFiles, dataFile):
    url = EXPERIMENT_PATH % "test"
    videoUrls = [url + videoFile for videoFile in videoFiles]
    dataUrls = [url + dataFile]
    return videoUrls, dataUrls

def runWithProband(proband):
    url = EXPERIMENT_PATH % str(proband)
    videoUrls = [url + EXPERIMENT_FILES[0], url + EXPERIMENT_FILES[1]]
    dataUrls = [url + EXPERIMENT_FILES[2]]
    return videoUrls, dataUrls

def main():
    app = QtGui.QApplication(sys.argv)

    videoUrls, dataUrls = runWithProband(1)
    #videoUrls, dataUrls = runTest(["blink.mp4"], "blink.csv")

    vis = DataVisualizer(None, videoUrls, dataUrls)
    vis.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    logging.getLogger().setLevel(logging.DEBUG)
    main()