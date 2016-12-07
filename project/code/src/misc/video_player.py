'''
Created on 06.12.2016

@author: Paul Pasler
'''
import cv2

FRAME_RATE = 32
KEY_ESC = 27

class DataAnalyzer(object):

    def __init__(self, videoPath):
        self.windowName = "PoSDBoS"
        self.videoPath = videoPath
        self.waitTime = FRAME_RATE

        self.openVideo()
        self.createWindow()

    def openVideo(self):
        self.videoCap = cv2.VideoCapture(self.videoPath)
        self.videoLength = int(self.videoCap.get(cv2.CAP_PROP_FRAME_COUNT))

    def createWindow(self):
        cv2.namedWindow(self.windowName)
        cv2.createTrackbar( 'start', self.windowName, 0, self.videoLength-1, self.onChange )
        switch = '0 : play \n1 : pause'
        cv2.createTrackbar( switch, self.windowName, 0, 1, self.toogle )

    def toogle(self, trackbarValue):
        if trackbarValue == 0:
            self.play()
        else:
            self.pause()

    def pause(self):
        self.waitTime = 0

    def play(self):
        self.waitTime = FRAME_RATE

    def onChange(self, trackbarValue):
        self.videoCap.set(cv2.CAP_PROP_POS_FRAMES,trackbarValue)
        err,img = self.videoCap.read()
        cv2.imshow(self.windowName, img)

    def start(self):
        cap = self.videoCap
        while(cap.isOpened()):
            ret, frame = cap.read()
            #gray = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)#cv2.COLOR_BGR2GRAY)

            cv2.imshow('PoSDBoS',frame)
            if cv2.waitKey(self.waitTime) == KEY_ESC:
                break
        self.close()

    def close(self):
        self.videoCap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    #video = 'E:/thesis/experiment/1/2016-12-05_14-25_face.mp4'
    video = 'E:/thesis/experiment/1/2016-12-05_14-25_drive.mp4'
    d = DataAnalyzer(video)
    d.start()