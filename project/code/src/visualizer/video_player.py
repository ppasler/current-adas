#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 08.12.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

from PyQt4 import QtGui, QtCore
import cv2

import numpy as np


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Video():
    def __init__(self, videoId, capture):
        self.capture = capture
        self.currentFrame=np.array([])

    def captureNextFrame(self):
        ret, readFrame=self.capture.read()
        if(ret==True):
            self.currentFrame=cv2.cvtColor(readFrame, cv2.COLOR_BGR2RGB)

    # TODO warning
    def captureFrame(self, curFrame):
        self.capture.set(1,curFrame)
        ret, readFrame=self.capture.read()
        if(ret==True):
            self.currentFrame=cv2.cvtColor(readFrame, cv2.COLOR_BGR2RGB)

    def convertFrame(self):
        '''converts frame to format suitable for QtGui'''
        try:
            height,width = self.currentFrame.shape[:2]
            img=QtGui.QImage(self.currentFrame, width, height, QtGui.QImage.Format_RGB888)
            img=QtGui.QPixmap.fromImage(img)
            self.previousFrame = self.currentFrame
            return img
        except:
            return None

class VideoPlayer(QtGui.QWidget):
    def __init__(self, parent, playerId, videoUrl):
        super(VideoPlayer, self).__init__()

        self.parent = parent
        self.capture = cv2.VideoCapture(videoUrl)
        self.frameCount = self.capture.get(cv2.CAP_PROP_FRAME_COUNT)
        self.fps = self.capture.get(cv2.CAP_PROP_FPS)

        print "player%d\t#%d\t%.2ffps\t%ds" % (playerId, self.frameCount, self.fps, self.frameCount / self.fps)

        self.video = Video("video" + str(playerId), self.capture)
        self.videoFrame = QtGui.QLabel(self)
        self.videoFrame.setGeometry(self.geometry())
        self.videoFrame.setObjectName("videoFrame" + str(playerId))

        self.setObjectName("videoPlayer" + str(playerId))

    def show(self, curFrame):
        try:
            #self.video.captureNextFrame()
            self.video.captureFrame(curFrame)
            self.videoFrame.setPixmap(self.video.convertFrame())
            self.videoFrame.setScaledContents(True)
        except TypeError:
            print "No frame"

class VideoWidget(QtGui.QWidget):

    def __init__(self):
        super(VideoWidget, self).__init__()
        self.mainLayout = QtGui.QHBoxLayout(self)
        self.setObjectName("videolwidget")

    def setPlayers(self, videoPlayers):
        for videoPlayer in videoPlayers:
            self.mainLayout.addWidget(videoPlayer)