#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Created on 08.12.2016

:author: Paul Pasler
:organization: Reutlingen University
'''

from PyQt4 import QtGui
import cv2
import logging

class Video():
    def __init__(self, videoId, capture):
        self.capture = capture

    # TODO warning
    def captureFrame(self, curFrame):
        self.capture.set(1,curFrame)
        ret, readFrame=self.capture.read()
        if(ret==True):
            currentFrame=cv2.cvtColor(readFrame, cv2.COLOR_BGR2RGB)
            return self.convertFrame(currentFrame)
        return None

    def convertFrame(self, currentFrame):
        '''converts frame to format suitable for QtGui'''
        try:
            height, width = currentFrame.shape[:2]
            videoImage = QtGui.QImage(currentFrame, width, height, QtGui.QImage.Format_RGB888)
            videoImage = QtGui.QPixmap.fromImage(videoImage)
            return videoImage
        except:
            logging.warn("no frame")
            return None

class VideoPlayer(QtGui.QWidget):
    def __init__(self, playerId, videoUrl):
        super(VideoPlayer, self).__init__()

        self.playerId = playerId
        self.capture = cv2.VideoCapture(videoUrl)
        self.frameCount = self.capture.get(cv2.CAP_PROP_FRAME_COUNT)
        self.fps = self.capture.get(cv2.CAP_PROP_FPS)

        logging.info("player%d\t#%d\t%.2ffps\t%ds" % (self.playerId, self.frameCount, self.fps, self.frameCount / self.fps))

        self.video = Video("video" + str(self.playerId), self.capture)
        self.videoFrame = QtGui.QLabel(self)
        self.videoFrame.setGeometry(self.geometry())
        self.videoFrame.setObjectName("videoFrame" + str(self.playerId))

        self.setObjectName("videoPlayer" + str(self.playerId))

    def setMaxFps(self, maxFps):
        self.maxFps = maxFps

    def show(self, curFrame):
        try:
            curFrame = self._calcCurFrame(curFrame)
            videoImage = self.video.captureFrame(curFrame)
            self.videoFrame.setPixmap(videoImage)
            self.videoFrame.setScaledContents(True)
        except TypeError:
            logging.error("No frame for player %s" % self.playerId)

    def _calcCurFrame(self, curFrame):
        return int(curFrame * (self.fps / self.maxFps))

class VideoWidget(QtGui.QWidget):

    def __init__(self, videoPlayers):
        super(VideoWidget, self).__init__()
        self.mainLayout = QtGui.QVBoxLayout(self)
        for videoPlayer in videoPlayers:
            self.mainLayout.addWidget(videoPlayer)

        self.setObjectName("videolwidget")