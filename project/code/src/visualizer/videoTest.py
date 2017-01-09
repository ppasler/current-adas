import cv2

fileName = "E:/thesis/experiment/1/2016-12-05_14-25_drive.mp4"
fileName2 = "E:/thesis/experiment/1/2016-12-05_14-25_face.mp4"
cap1 = cv2.VideoCapture(fileName)
cap2 = cv2.VideoCapture(fileName2)
curFrame = 0

def readFrame(cap, curFrame):
    cap.set(1,curFrame)
    _, frame = cap.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    cv2.imshow('frame',gray)

while(cap1.isOpened() and cap1.isOpened()):
    readFrame(cap1, curFrame)
    readFrame(cap2, curFrame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    curFrame += 1

cap1.release()
cap2.release()
cv2.destroyAllWindows()