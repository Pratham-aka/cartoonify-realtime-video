import cv2
import cvzone
from cvzone.SelfiSegmentationModule import SelfiSegmentation
import os
import numpy as np
from PIL import Image, ImageEnhance
import numpy

cap = cv2.VideoCapture(0)
cap.set(3, 1580)
cap.set(4, 1020)
segmentor = SelfiSegmentation()
fpsReader = cvzone.FPS()

def contrast(img):
    # converting to LAB color space
    lab= cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l_channel, a, b = cv2.split(lab)

    # Applying CLAHE to L-channel
    # feel free to try different values for the limit and grid size:
    clahe = cv2.createCLAHE(clipLimit=9.0, tileGridSize=(8,8))
    cl = clahe.apply(l_channel)

    # merge the CLAHE enhanced L-channel with the a and b channel
    limg = cv2.merge((cl,a,b))

    # Converting image from LAB Color model to BGR color spcae
    enhanced_img = cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)
    return enhanced_img

def cartoonize(frame):
    num_down = 1
    num_bilateral = 4

    img=frame
    img_copy = img

    try:
        for _ in range(num_down):
            img_copy = cv2.pyrDown(img_copy)
    except:
        print("No such image found. Please check file path.")
        return 

    for _ in range(num_bilateral):
        img_copy = cv2.bilateralFilter(img_copy, d=7, sigmaColor=7, sigmaSpace=5)

    for _ in range(num_down):
        img_copy = cv2.pyrUp(img_copy)

    img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    img_blur = cv2.medianBlur(img_gray, 9)


    img_edge = cv2.adaptiveThreshold(img_blur, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY,
        blockSize=3,
        C=2)

    #Converting to RGB from GrayScale
    img_edge = cv2.cvtColor(img_edge, cv2.COLOR_GRAY2RGB)
    
    try:
        img_cartoon = cv2.bitwise_and(img_copy, img_edge)
    except: 
        print("Image could not be cartoonized due to inconsistency in channels")
        return

    return img_cartoon
i = 0
while True:
    sucess, img = cap.read()
    #img = cv2.rotate(img, cv2.cv2.ROTATE_90_CLOCKWISE)
    result = cartoonize(img)
    result = contrast(result)
    imgOut = segmentor.removeBG(img,result, threshold=0.6)
    imgstacked = cvzone.stackImages([img, imgOut], 2,1)
    _, imgstacked = fpsReader.update(imgstacked,color=(0,0,255))


    cv2. imshow("segmented ", imgOut)
    k = cv2.waitKey(1)
    if k == ord("q"):
        break
cap.release()
cv2.destroyAllWindows()