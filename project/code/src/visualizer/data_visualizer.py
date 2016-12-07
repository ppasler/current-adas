import sys

from PyQt4 import QtGui, QtCore
import cv2

import numpy as np
from data_visualizer_ui import Ui_MainWindow

class Video():
    def __init__(self,capture):
        self.capture = capture
        self.currentFrame=np.array([])

    def captureNextFrame(self):
        ret, readFrame=self.capture.read()
        if(ret==True):
            self.currentFrame=cv2.cvtColor(readFrame,cv2.COLOR_BGR2RGB)

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
    def __init__(self, parent, videoUrl):
        super(VideoPlayer, self).__init__()
        self.parent = parent
        self.video = Video(cv2.VideoCapture(videoUrl))

    def play(self):
        try:
            self.video.captureNextFrame()
            self.parent.ui.videoFrame.setPixmap(self.video.convertFrame())
            self.parent.ui.videoFrame.setScaledContents(True)
        except TypeError:
            print "No frame"

class DataVisualizer(QtGui.QMainWindow):
    def __init__(self,parent, videoUrls):
        super(DataVisualizer, self).__init__()

        self._initPlayer(videoUrls)
        self._initUI()
        self._initTimer()

        self.update()

    def _initPlayer(self, videoUrls):
        self.videoPlayers = []
        for videoUrl in videoUrls:
            self.videoPlayers.append(VideoPlayer(self, videoUrl))

    def _initUI(self):
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self, self.videoPlayers[0])

    def _initTimer(self):
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.play)
        self._timer.start(27)

    def play(self):
        for videoPlayer in self.videoPlayers:
            videoPlayer.play()

def main():
    app = QtGui.QApplication(sys.argv)
    videoUrls = ['E:/thesis/experiment/1/2016-12-05_14-25_drive.mp4', 'E:/thesis/experiment/1/2016-12-05_14-25_face.mp4']
    vis = DataVisualizer(None, videoUrls)
    vis.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()