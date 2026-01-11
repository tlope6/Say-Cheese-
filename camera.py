import cv2

def capture_frame()  :
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    cam.release()

    if ret :
        cv2.imwrite("snapshot.jpg", frame)
        return True
    
    return False