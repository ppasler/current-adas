import sys

from PyQt4 import QtGui, QtCore
import cv2

import numpy as np
from ui import Ui_MainWindow

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

class Gui(QtGui.QMainWindow):
    def __init__(self,parent=None):
        QtGui.QWidget.__init__(self,parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.video = Video(cv2.VideoCapture('E:/thesis/experiment/1/2016-12-05_14-25_drive.mp4'))
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.play)
        self._timer.start(27)
        self.update()
    
    def play(self):
        try:
            self.video.captureNextFrame()
            self.ui.videoFrame.setPixmap(
            self.video.convertFrame())
            self.ui.videoFrame.setScaledContents(True)
        except TypeError:
            print "No frame"

def main():
    app = QtGui.QApplication(sys.argv)
    ex = Gui()
    ex.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()