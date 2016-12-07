#http://stackoverflow.com/questions/21983062/in-python-opencv-is-there-a-way-to-quickly-scroll-through-frames-of-a-video-all
'''
Created on 07.12.2016

@author: Paul Pasler
'''
import cv2


def main(video):
    cap = cv2.VideoCapture(video)
    length = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def onChange(trackbarValue):
        cap.set(cv2.CAP_PROP_POS_FRAMES,trackbarValue)
        err,img = cap.read()
        cv2.imshow("mywindow", img)
        pass

    cv2.namedWindow('mywindow')
    cv2.createTrackbar( 'start', 'mywindow', 0, length, onChange )
    cv2.createTrackbar( 'end'  , 'mywindow', 100, length, onChange )
    
    onChange(0)
    cv2.waitKey()
    
    start = cv2.getTrackbarPos('start','mywindow')
    end   = cv2.getTrackbarPos('end','mywindow')
    if start >= end:
        raise Exception("start must be less than end")
    
    cap.set(cv2.CAP_PROP_POS_FRAMES,start)
    while cap.isOpened():
        err,img = cap.read()
        if cap.get(cv2.CAP_PROP_POS_FRAMES) >= end:
            break
        cv2.imshow("mywindow", img)
        k = cv2.waitKey(10) & 0xff
        if k==27:
            break

if __name__ == "__main__":
    video = 'E:/thesis/experiment/1/2016-12-05_14-25_face.mp4'
    #video = 'E:/thesis/experiment/1/2016-12-05_14-25_drive.mp4'
    main(video)